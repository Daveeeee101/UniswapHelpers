from typing import List, Optional
from NetworkConnection.BaseRPCRequests import RPCRequest, SubscriptionRequest, CallRequest
from Web3Types.SimpleTypes import HexBytes, Address
from Web3Types.Transaction import Transaction
from Web3Types.TransactionLog import Log
from Web3Types.TransactionReciept import TransactionReceipt


class AlchemyRPCRequest(RPCRequest):
    pass


class GetTransactionReceiptsByBlock(AlchemyRPCRequest):

    def __init__(self, blockNumberOrHash):
        if type(blockNumberOrHash) == int:
            blockNumberOrHash = hex(blockNumberOrHash)
            obj = {"blockNumber": blockNumberOrHash}
        else:
            obj = {"blockHash": str(blockNumberOrHash)}
        super().__init__("alchemy_getTransactionReceipts", [obj])

    def decode_response(self, response):
        outs = []
        for tr in response['receipts']:
            if tr['contractAddress'] is not None:
                continue
            logs = [Log(HexBytes(l['blockHash']), int(l['blockNumber'], 16), int(l['transactionIndex'], 16),
                        Address(l['address']), int(l['logIndex'], 16), HexBytes(l['data']),
                        True if l['removed'] == "true" else False, [HexBytes(t) for t in l['topics']],
                        HexBytes(l['transactionHash'])) for l in tr['logs']]
            receipt = TransactionReceipt(HexBytes(tr['blockHash']), int(tr['blockNumber'], 16),
                                         int(tr['transactionIndex'], 16),
                                         HexBytes(tr['transactionHash']), Address(tr['from']), Address(tr['to']),
                                         int(tr['cumulativeGasUsed'], 16), int(tr['gasUsed'], 16), logs,
                                         HexBytes(tr['logsBloom']),
                                         int(tr['status'], 16), int(tr['effectiveGasPrice'], 16), int(tr['type'], 16))
            outs.append(receipt)
        return outs


class BundleCallRequest(AlchemyRPCRequest):

    def __init__(self, transactions: List[Transaction]):
        self.transactions = transactions
        super().__init__("alchemy_simulateExecutionBundle", [[t.to_json() for t in transactions]])

    def decode_response(self, response):
        print(response)


class AlchemyPendingTransactions(SubscriptionRequest, AlchemyRPCRequest):

    def __init__(self, to_addresses):
        super().__init__(["alchemy_pendingTransactions", {"toAddress": to_addresses}])


class AlchemyCallRequest(CallRequest):

    def __init__(self, transaction: Transaction, code_override: str, address_override: Address, block_number: Optional[int] = None):
        super().__init__(transaction, block_number)
        self.params.append({str(address_override): {"code": code_override}})

