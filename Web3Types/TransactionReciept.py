from typing import List

from Web3Types.SimpleTypes import HexBytes, Address
from Web3Types.TransactionLog import Log


class TransactionReceipt:

    def __init__(self, block_hash: HexBytes, block_number: int, transaction_index: int, transaction_hash: HexBytes,
                 t_from: Address, t_to: Address, cumulative_gas_used: int, gas_used: int, logs: List[Log],
                 logs_bloom: HexBytes, status: int, effective_gas_price: int, t_type: int):
        self.block_hash: HexBytes = block_hash
        self.block_number: int = block_number
        self.transaction_index: int = transaction_index
        self.transaction_hash: HexBytes = transaction_hash
        self.t_from: Address = t_from
        self.t_to: Address = t_to
        self.cumulative_gas_used: int = cumulative_gas_used
        self.gas_used: int = gas_used
        self.logs: List[Log] = logs
        self.logs_bloom: HexBytes = logs_bloom
        self.status: int = status
        self.effective_gas_price: int = effective_gas_price
        self.t_type: int = t_type

    def __str__(self):
        return f"{self.transaction_hash}, {self.transaction_index}, {self.t_from}"
