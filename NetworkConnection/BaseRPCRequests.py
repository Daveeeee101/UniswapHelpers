from typing import List, Optional
from Utilities.FunctionCallBuilder import create_event_topic, decode_function_output
from Web3Types.Block import Block
from Web3Types.SimpleTypes import HexBytes, Address
from Web3Types.Transaction import Transaction, SmartContractTransaction
from Web3Types.TransactionLog import Log


class RPC_Error(Exception):

    def __init__(self, error_id, msg=None):
        if msg is not None:
            super().__init__(msg)
        self.id = error_id


class RPCRequest:

    def __init__(self, request_name, params):
        self.request_name = request_name
        self.params = params

    def decode_response(self, response):
        return response

class BlockNumberRequest(RPCRequest):

    def __init__(self):
        super().__init__("eth_blockNumber", [])

    def decode_response(self, response):
        return int(response, 16)


class GetBlockByHash(RPCRequest):

    def __init__(self, block_hash):
        super().__init__("eth_getBlockByHash", [block_hash, False])

    def decode_response(self, response):
        gasUsed = int(response['gasUsed'], 16)
        logsBloom = HexBytes(response['logsBloom'])
        block_hash = HexBytes(response['hash'])
        miner = Address(response['miner'])
        number = int(response['number'], 16)
        parent_hash = HexBytes(response['parentHash'])
        timestamp = int(response['timestamp'], 16)
        return Block(block_hash, gasUsed, logsBloom, miner, number, parent_hash, timestamp)


class SubscriptionRequest(RPCRequest):

    def __init__(self, params):
        self.subscription_id = None
        super().__init__("eth_subscribe", params)

    def set_subscription_id(self, sub_id):
        self.subscription_id = sub_id

    def get_subscription_id(self):
        if self.subscription_id is None:
            raise RPC_Error("Subscription not yet initialised")
        else:
            return self.subscription_id


class FilterRequest(RPCRequest):

    def __init__(self, method, params):
        self.filter_id = None
        super().__init__(method, params)

    def set_filter_id(self, sub_id):
        self.filter_id = sub_id

    def get_filter_id(self):
        if self.filter_id is None:
            raise RPC_Error("Filter not yet initialised")
        else:
            return self.filter_id

    def get_filter_changes_request(self):
        return FilterRequest("eth_getFilterChanges", [self.get_filter_id()])


class HeadSubscriptionRequest(SubscriptionRequest):

    def __init__(self):
        super().__init__(["newHeads"])

    def decode_response(self, response):
        gasUsed = int(response['gasUsed'], 16)
        logsBloom = HexBytes(response['logsBloom'])
        block_hash = HexBytes(response['hash'])
        miner = Address(response['miner'])
        number = int(response['number'], 16)
        parent_hash = HexBytes(response['parentHash'])
        timestamp = int(response['timestamp'], 16)
        return Block(block_hash, gasUsed, logsBloom, miner, number, parent_hash, timestamp)


class PendingTransactionSubscriptionRequest(SubscriptionRequest):

    def __init__(self):
        super().__init__(["newPendingTransactions"])

    def decode_response(self, response):
        return HexBytes(response)


class GetLogsRequest(RPCRequest):

    def __init__(self, from_block, to_block, event_abis, address: Address = None):
        self.abis = event_abis
        if type(from_block) == int:
            from_block = hex(from_block)
        if type(to_block) == int:
            to_block = hex(to_block)
        params = {"fromBlock": from_block, "toBlock": to_block}
        if event_abis is not None:
            params["topics"] = [str(create_event_topic(a)) for a in event_abis]
        if address is not None:
            params['address'] = str(address)
        super().__init__("eth_getLogs", [params])

    def decode_response(self, response) -> List[Log]:
        outs = []
        for l in response:
            log = Log(HexBytes(l['blockHash']), int(l['blockNumber'], 16), int(l['transactionIndex'], 16),
                      Address(l['address']), int(l['logIndex'], 16), HexBytes(l['data']),
                      True if l['removed'] == "true" else False, [HexBytes(t) for t in l['topics']],
                      HexBytes(l['transactionHash']))
            for t in self.abis:
                if log.topics[0] == create_event_topic(t):
                    log.decode_data(t)
            outs.append(log)
        return outs


class HeadFilterRequest(FilterRequest):

    def __init__(self):
        super().__init__("eth_newBlockFilter", [])

    def decode_response(self, response):
        gasUsed = int(response['gasUsed'], 16)
        logsBloom = HexBytes(response['logsBloom'])
        block_hash = HexBytes(response['hash'])
        miner = Address(response['miner'])
        number = int(response['number'], 16)
        parent_hash = HexBytes(response['parentHash'])
        timestamp = int(response['timestamp'], 16)
        return Block(block_hash, gasUsed, logsBloom, miner, number, parent_hash, timestamp)


class CallRequest(RPCRequest):

    def __init__(self, transaction: Transaction, block_number: Optional[int] = None):
        if block_number is not None:
            block = hex(block_number)
        else:
            block = "latest"
        self.transaction: Transaction = transaction
        super().__init__("eth_call", [transaction.to_json(), block])

    def decode_response(self, response):
        if response is None:
            return None
        if type(self.transaction) == Transaction:
            return HexBytes(response)
        elif type(self.transaction) == SmartContractTransaction:
            return decode_function_output(HexBytes(response), self.transaction.abi_function)


class GetStorageRequest(RPCRequest):

    def __init__(self, address, slot_number):
        super().__init__("eth_getStorageAt", [address, hex(slot_number), "latest"])

    def decode_response(self, response):
        return HexBytes(response)


class GasPriceRequest(RPCRequest):

    def __init__(self):
        super().__init__("eth_gasPrice", [])

    def decode_response(self, response):
        return int(response, 16)


class GasHistoryRequest(RPCRequest):

    def __init__(self, block_count: int, newest_block: int):
        super().__init__("eth_feeHistory", [hex(block_count), hex(newest_block)])

    def decode_response(self, response):
        return [int(r, 16) for r in response["baseFeePerGas"]]