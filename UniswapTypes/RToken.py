from typing import Union
from Web3Types.SimpleTypes import Address


class BadTokenAddressError(Exception):
    pass


class RToken:
    """A class that represents an ERC-20 token"""

    __slots__ = "__address"

    WETH_ADDRESS = Address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
    USDC_ADDRESS = Address("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
    USD_ADDRESS = Address("0xd233D1f6FD11640081aBB8db125f722b5dc729dc")

    def __init__(self, contract_address: Union[str, Address]):
        if isinstance(contract_address, str):
            self.__address = Address(contract_address)
        elif isinstance(contract_address, Address):
            self.__address = contract_address
        else:
            raise BadTokenAddressError()

    def __repr__(self):
        return self.__address.__repr__()

    def __str__(self):
        return str(self.__address)

    def __eq__(self, other):
        return self.__address == other.__address

    def __hash__(self):
        return hash(self.__address)

    def get_address(self):
        return self.__address


WETH_TOKEN = RToken(RToken.WETH_ADDRESS)
USD_TOKEN = RToken(RToken.USD_ADDRESS)
USDC_TOKEN = RToken(RToken.USDC_ADDRESS)
