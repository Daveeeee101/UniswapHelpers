from __future__ import annotations
from Utilities.FunctionCallBuilder import *
from Web3Types.SimpleTypes import Address, HexBytes


null_address = Address("0x0000000000000000000000000000000000000000")


class Transaction:

    def __init__(self, transfer_from: Address, transfer_to: Address, transfer_value: int,
                 transfer_data: HexBytes = HexBytes("0x"), transfer_gas: int = 0, transfer_gasPrice: int = 0,
                 transfer_maxFeePerGas: int = 0, transfer_maxPriorityFeePerGas: int = 0):
        self.t_from: Address = transfer_from
        self.to: Address = transfer_to
        self.value: int = transfer_value
        self.data: HexBytes = transfer_data
        self.gas: int = transfer_gas
        self.gasPrice: int = transfer_gasPrice
        self.maxFeePerGas: int = transfer_maxFeePerGas
        self.maxPriorityFeePerGas: int = transfer_maxPriorityFeePerGas

    def to_json(self):
        out = {
            "from": str(self.t_from),
            "to": str(self.to),
            "value": hex(self.value),
            "data": str(self.data),
        }
        if self.gas != 0:
            out["gas"] = hex(self.gas)
        if self.gasPrice != 0:
            out["gasPrice"] = hex(self.gasPrice)
        if self.maxFeePerGas != 0:
            out["maxFeePerGas"] = hex(self.maxFeePerGas)
        if self.maxPriorityFeePerGas != 0:
            out["maxPriorityFeePerGas"] = hex(self.maxPriorityFeePerGas)
        return out

    def set_function_call(self, function_abi, *args):
        self.data = create_function_call(function_abi, *args)


class SmartContractTransaction(Transaction):

    def __init__(self, abi_function, input_tuple, transfer_to: Address, transfer_value: int,
                 transfer_from: Address = null_address, transfer_gas: int = 0,
                 transfer_gasPrice: int = 0, transfer_maxFeePerGas: int = 0,
                 transfer_maxPriorityFeePerGas: int = 0):
        self.abi_function = abi_function
        data = create_function_call(abi_function, *input_tuple)
        super().__init__(transfer_from, transfer_to, transfer_value, data, transfer_gas, transfer_gasPrice, transfer_maxFeePerGas, transfer_maxPriorityFeePerGas)

