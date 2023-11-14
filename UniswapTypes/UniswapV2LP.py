from typing import Union, Optional, Tuple
from UniswapTypes.ILiquidityPool import ILiquidityPool
from UniswapTypes.RToken import RToken
from Web3Types.SimpleTypes import Address
import json


class SwapError(Exception):
    pass


class UninstantiatedReserves(Exception):
    pass


class InsufficientReserves(Exception):
    pass


def get_swap_out(reserves_in: int, reserves_out: int, token_in: int, fees_as_fraction: Tuple[int, int]) -> int:
    """Emulates the exact maths used for a Uniswap V2 swap"""
    amountInWithFee = fees_as_fraction[0] * token_in
    numerator = amountInWithFee * reserves_out
    denominator = (reserves_in * fees_as_fraction[1]) + amountInWithFee
    return numerator // denominator


class UniswapV2LP(ILiquidityPool):
    """Uniswap V2 liquidity pool representation"""

    __slots__ = ("reserves0", "reserves1", "fees_as_fraction")

    def __init__(self, address: Union[str, Address], token0: RToken, token1: RToken, reserves0: Optional[int] = None, reserves1: Optional[int] = None):
        super().__init__(address, token0, token1)
        self.reserves0: Optional[int] = reserves0
        self.reserves1: Optional[int] = reserves1
        self.fees_as_fraction: Tuple[int, int] = (997, 1000)

    def __str__(self):
        return str(self.address)

    def __eq__(self, other):
        return self.address == other.address

    def __hash__(self):
        return hash(self.address)

    def get_reserves(self) -> Tuple[int, int]:
        if self.reserves0 is None or self.reserves1 is None:
            raise UninstantiatedReserves("Reserves have not been instantiated yet")
        else:
            return self.reserves0, self.reserves1

    def simulate_swap(self, token0_in: int, token1_in: int) -> int:
        reserves0, reserves1 = self.get_reserves()
        if reserves0 == 0 or reserves1 == 0:
            raise SwapError("No reserves to swap!")
        """if token0_in > reserves0 or token1_in > reserves1:
            raise InsufficientReserves(f"Input a swap which requires more liquidity than exists. Reserves0: {reserves0}"
                                       f", token0 in: {token0_in}, Reserves1: {reserves1}, token1 in: {token1_in}")"""
        if token0_in != 0 and token1_in != 0:
            raise SwapError("One token input must be zero")
        elif token0_in != 0:
            return get_swap_out(reserves0, reserves1, token0_in, self.fees_as_fraction)
        elif token1_in != 0:
            return get_swap_out(reserves1, reserves0, token1_in, self.fees_as_fraction)
        else:
            raise SwapError("Must swap non-negative tokens")

    def swap(self, token0_in: int, token1_in: int) -> int:
        reserves0, reserves1 = self.get_reserves()
        """if token0_in > reserves0 or token1_in > reserves1:
            raise InsufficientReserves(f"Input a swap which requires more liquidity than exists. Reserves0: {reserves0}"
                                       f", token0 in: {token0_in}, Reserves1: {reserves1}, token1 in: {token1_in}")"""
        if token0_in != 0 and token1_in != 0:
            raise SwapError("One token input must be zero")
        elif token0_in != 0:
            token_out = get_swap_out(reserves0, reserves1, token0_in, self.fees_as_fraction)
            self.reserves0 += token0_in
            self.reserves1 -= token_out
            return token_out
        elif token1_in != 0:
            token_out = get_swap_out(reserves1, reserves0, token1_in, self.fees_as_fraction)
            self.reserves1 += token1_in
            self.reserves0 -= token_out
            return token_out
        else:
            raise SwapError("Must swap non-negative tokens")

    def simulate_swap_price(self, token0_in: int, token1_in: int) -> float:
        reserves0, reserves1 = self.get_reserves()
        if reserves0 == 0 or reserves1 == 0:
            raise SwapError("No reserves to swap!")
        """if token0_in > reserves0 or token1_in > reserves1:
            raise InsufficientReserves(f"Input a swap which requires more liquidity than exists. Reserves0: {reserves0}"
                                       f", token0 in: {token0_in}, Reserves1: {reserves1}, token1 in: {token1_in}")"""
        if token0_in != 0 and token1_in != 0:
            raise SwapError("One token input must be zero")
        elif token0_in != 0:
            token_out = get_swap_out(reserves0, reserves1, token0_in, self.fees_as_fraction)
            return (reserves1 - token_out) / (reserves0 + token0_in)
        elif token1_in != 0:
            token_out = get_swap_out(reserves0, reserves1, token0_in, self.fees_as_fraction)
            return (reserves1 + token1_in) / (reserves0 - token_out)
        else:
            raise SwapError("Must swap non-negative tokens")

    def get_price(self) -> float:
        r0, r1 = self.get_reserves()
        return r1 / r0

    def sync(self, reserves0: int, reserves1: int):
        """emulates the sync event from the blockchain"""
        self.reserves0 = reserves0
        self.reserves1 = reserves1

    def set_reserves(self, reserves0: int, reserves1: int):
        self.reserves0 = reserves0
        self.reserves1 = reserves1

    def to_json(self) -> str:
        return json.dumps({
            "address": str(self.address),
            "token0": str(self.token0),
            "token1": str(self.token1),
            "reserves0": self.reserves0,
            "reserves1": self.reserves1,
            "type": "UniswapV2LP"
        })


def v2_from_json(json_str: str) -> UniswapV2LP:
    obj_dict = json.loads(json_str)
    return UniswapV2LP(Address(obj_dict["address"]),
                       RToken(obj_dict["token0"]),
                       RToken(obj_dict["token1"]),
                       obj_dict["reserves0"],
                       obj_dict["reserves1"])
