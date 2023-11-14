import json
from typing import Union, Optional
from UniswapTypes.RToken import RToken
from UniswapTypes.UniswapV2LP import UniswapV2LP
from Web3Types.SimpleTypes import Address


class ShibaswapV2LP(UniswapV2LP):

    __slots__ = ("reserves0", "reserves1", "fees_as_fraction")

    def __init__(self, address: Union[str, Address], token0: RToken, token1: RToken, reserves0: Optional[int] = None, reserves1: Optional[int] = None):
        super().__init__(address, token0, token1, reserves0, reserves1)
        self.fees_as_fraction = (997, 1000)

    def to_json(self) -> str:
        return json.dumps({
            "address": str(self.address),
            "token0": str(self.token0),
            "token1": str(self.token1),
            "reserves0": self.reserves0,
            "reserves1": self.reserves1,
            "type": "ShibaswapV2LP"
        })


def shiba_v2_from_json(json_str: str) -> ShibaswapV2LP:
    obj_dict = json.loads(json_str)
    return ShibaswapV2LP(Address(obj_dict["address"]),
                         RToken(obj_dict["token0"]),
                         RToken(obj_dict["token1"]),
                         obj_dict["reserves0"],
                         obj_dict["reserves1"])
