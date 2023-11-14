from typing import Union
from Web3Types.SimpleTypes import Address
from UniswapTypes.RToken import RToken


class ILiquidityPool:
    """Interface for different liquidity pools"""

    __slots__ = ("address", "token0", "token1")

    def __init__(self, address: Union[str, Address], token0: RToken, token1: RToken):
        if isinstance(address, str):
            self.address: Address = Address(address)
        elif isinstance(address, Address):
            self.address: Address = address
        else:
            raise TypeError
        self.token0: RToken = token0
        self.token1: RToken = token1

    def __eq__(self, other):
        return self.address == other.address

    def __repr__(self):
        return f"{self.address.__repr__()} from {self.token0} to {self.token1}"

    def __hash__(self):
        return hash(self.address)

    def simulate_swap(self, token0_in: int, token1_in: int) -> int:
        """Method that simulates the result of a swap without altering internal liquidity"""
        pass

    def swap(self, token0_in: int, token1_in: int) -> int:
        """Method that performs a swap and changes pool liquidity"""
        pass

    def get_price(self) -> float:
        """Gets the price for converting an infinitesimally small amount of token0 for token1"""
        pass

    def to_json(self) -> str:
        """Converts the liquidity pool to a json string representation"""
        pass


def from_json(json_str: str) -> ILiquidityPool:
    pass
