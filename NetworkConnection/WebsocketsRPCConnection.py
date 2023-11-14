import asyncio
import json
import websockets as ws
from NetworkConnection.BaseRPCRequests import *
from NetworkConnection.RPCConnection import Batch_Error, ExecutionRevertError, BlockRangeError


class WebsocketsRPCConnection:
    def __init__(self, websocket_url, max_pending_requests=1000):
        self.websocket_connection = None
        self.url = websocket_url
        self.max_pending_requests = max_pending_requests
        self.current_request_id = 0
        self.pending_requests = {}
        self.received_responses = {}
        self.subscription_responses = {}
        self.running_receive_loop = None

    async def __aenter__(self):
        self.websocket_connection = await ws.connect(self.url)
        self.running_receive_loop = asyncio.create_task(self.consumer_loop())
        await asyncio.sleep(0)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.clean_up()

    async def clean_up(self):
        self.running_receive_loop.cancel()
        await self.websocket_connection.close()

    async def setup_websocket(self):
        self.websocket_connection = await ws.connect(self.url)

    async def setup_task(self):
        asyncio.create_task(self.consumer_loop())
        await asyncio.sleep(0)

    @staticmethod
    def response_code_valid(response):
        if "error" not in response:
            return True
        else:
            if response['error']['code'] == 3:
                raise ExecutionRevertError(3, response['error']['message'])
            elif response['error']['code'] == -32000:
                raise RPC_Error(response['error']['code'], response)
            elif response['error']['code'] == -32005:
                response = response['error']
                block_list = response['message'][response['message'].index('[') + 1: response['message'].index(']')]
                num_lower = block_list[: block_list.index(',')]
                num_upper = block_list[block_list.index(',') + 2:]
                raise BlockRangeError(num_lower, num_upper, "more than 10000 logs requested, try within error ranges")
            else:
                raise RPC_Error(response['error']['code'], response)

    async def consumer_loop(self):
        while True:
            message = await self.websocket_connection.recv()
            response = json.loads(message)
            if type(response) == list:
                response_id = response[0]['id']
                self.received_responses[response_id] = response
                self.pending_requests[response_id].set()
            else:
                try:
                    response_id = response['id']
                    self.received_responses[response_id] = response
                    self.pending_requests[response_id].set()
                except KeyError:
                    subscription_id = response['params']['subscription']
                    await self.subscription_responses[subscription_id].put(response['params'])

    async def send_request(self, request: RPCRequest, d=False):
        request_id = self.generate_request_id()
        rpc_json = {"jsonrpc": "2.0", "method": request.request_name, "params": request.params, "id": request_id}
        await self.websocket_connection.send(json.dumps(rpc_json))
        self.pending_requests[request_id] = asyncio.Event()
        await self.pending_requests[request_id].wait()
        self.pending_requests.pop(request_id)
        response = self.received_responses[request_id]
        self.received_responses.pop(request_id)
        if self.response_code_valid(response):
            return request.decode_response(response['result']) if not d else response['result']

    async def send_batch_request(self, batch_list: List[RPCRequest]):
        request_id_start = self.generate_request_id()
        request_id = request_id_start
        batch = []
        for request in batch_list:
            batch.append({"jsonrpc": "2.0", "method": request.request_name, "params": request.params, "id": request_id})
            request_id = self.generate_request_id()
        await self.websocket_connection.send(json.dumps(batch))
        self.pending_requests[request_id_start] = asyncio.Event()
        await self.pending_requests[request_id_start].wait()
        self.pending_requests.pop(request_id_start)
        response = self.received_responses[request_id_start]
        self.received_responses.pop(request_id_start)
        out = []
        for batch_req, (index, resp) in zip(batch_list, enumerate(response)):
            if batch[index]['id'] != resp['id']:
                raise Batch_Error()
            valid = self.response_code_valid(resp)
            if valid is None:
                out.append(None)
            elif valid:
                out.append(batch_req.decode_response(resp['result']))
            else:
                out.append(batch_req.handle_error(resp))
        return out

    async def subscribe_to_events(self, request: SubscriptionRequest):
        response = await self.send_request(request, True)
        self.subscription_responses[response] = asyncio.Queue(self.max_pending_requests)
        request.set_subscription_id(response)

    async def poll_subscription(self, subscription: SubscriptionRequest):
        response = await self.subscription_responses[subscription.get_subscription_id()].get()
        return subscription.decode_response(response['result'])

    async def poll_subscription_as_list(self, subscription: SubscriptionRequest):
        size = self.subscription_responses[subscription.get_subscription_id()].qsize()
        if size == 0:
            response = await self.subscription_responses[subscription.get_subscription_id()].get()
            return [subscription.decode_response(response['result'])]
        else:
            responses = (await self.subscription_responses[subscription.get_subscription_id()].get() for _ in range(size))
            return [subscription.decode_response(response['result']) async for response in responses]

    async def add_filter(self, request: FilterRequest):
        response = await self.send_request(request)
        request.filter_id = response

    async def poll_filter(self, filter_request: FilterRequest):
        response = await self.send_request(filter_request.get_filter_changes_request())
        return filter_request.decode_response(response)

    def generate_request_id(self):
        cur_id = self.current_request_id
        self.current_request_id += 1
        if self.current_request_id > (self.max_pending_requests * 100):
            self.current_request_id = 0
        return cur_id