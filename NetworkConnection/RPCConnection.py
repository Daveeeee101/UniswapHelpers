import asyncio
import copy
import aiohttp
from NetworkConnection.BaseRPCRequests import *


class Batch_Error(Exception):
    pass


class BlockRangeError(Exception):

    def __init__(self, lower_range: str, upper_range: str, msg):
        super().__init__(msg)
        self.lower_block = lower_range
        self.upper_block = upper_range


class ExecutionRevertError(RPC_Error):

    pass


class HTTPRPCConnection:
    __slots__ = ("http_connection", "http_url", "current_request_id")

    MAX_REQUESTS = 10000

    def __init__(self, http_url: str):
        self.http_connection: aiohttp.ClientSession = None
        self.http_url: str = http_url
        self.current_request_id = 0

    def enter(self):
        self.http_connection = aiohttp.ClientSession()

    async def __aenter__(self):
        self.enter()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.clean_up()

    async def clean_up(self):
        await self.http_connection.close()

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

    async def send_request(self, request: RPCRequest):
        request_id = self.generate_request_id()
        rpc_json = {"jsonrpc": "2.0", "method": request.request_name, "params": request.params, "id": request_id}
        async with self.http_connection.post(self.http_url, json=rpc_json) as resp:
            response = await resp.json()
            if self.response_code_valid(response):
                return request.decode_response(response['result'])

    async def smart_send_log_request(self, request: GetLogsRequest, lower_block: Optional[str] = None,
                                     upper_block: Optional[str] = None):
        """repeatedly sends log requests, resending requests if limit exceeded"""
        request_id = self.generate_request_id()
        rpc_json = {"jsonrpc": "2.0", "method": request.request_name, "params": copy.deepcopy(request.params),
                    "id": request_id}
        if lower_block is not None and upper_block is not None:
            rpc_json["params"][0]["fromBlock"] = lower_block
            rpc_json["params"][0]["toBlock"] = upper_block
        async with self.http_connection.post(self.http_url, json=rpc_json) as resp:
            response = await resp.json()
            try:
                valid_resp = self.response_code_valid(response)
            except BlockRangeError as err:
                required_spread = int(err.upper_block, 16) - int(err.lower_block, 16)
                from_block = int(rpc_json["params"][0]["fromBlock"], 16)
                to_block = int(rpc_json["params"][0]["toBlock"], 16)
                use_spread = required_spread // 2
                coros_recurse = [self.smart_send_log_request(request, hex(i), hex(min(to_block, i + use_spread - 1)))
                                 for i in range(from_block, to_block, use_spread)]
                results = await asyncio.gather(*coros_recurse)
                outs = []
                for res in results:
                    outs += res
                return outs
            if valid_resp:
                return request.decode_response(response['result'])

    async def send_batch_request(self, batch_list: List[RPCRequest]):
        request_id_start = self.generate_request_id()
        request_id = request_id_start
        batch = []
        for request in batch_list:
            batch.append({"jsonrpc": "2.0", "method": request.request_name, "params": request.params, "id": request_id})
            request_id = self.generate_request_id()
        async with self.http_connection.post(self.http_url, json=batch) as resp:
            response = await resp.json()
            out = []
            print(batch, response)
            for batch_req, (index, r) in zip(batch_list, enumerate(response)):
                if batch[index]['id'] != r['id']:
                    raise Batch_Error()
                if self.response_code_valid(r):
                    out.append(batch_req.decode_response(r['result']))
                else:
                    out.append(batch_req.handle_error(r))
            return out

    async def add_filter(self, request: FilterRequest):
        response = await self.send_request(request)
        request.filter_id = response

    async def poll_filter(self, filter_request: FilterRequest):
        response = await self.send_request(filter_request.get_filter_changes_request())
        return filter_request.decode_response(response)

    def generate_request_id(self):
        cur_id = self.current_request_id
        self.current_request_id += 1
        if self.current_request_id > self.MAX_REQUESTS:
            self.current_request_id = 0
        return cur_id
