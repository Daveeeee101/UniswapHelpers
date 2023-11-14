import json

from UniswapTypes.RToken import RToken
from UniswapTypes.UniswapV2LP import UniswapV2LP
from Web3Types.SimpleTypes import Address


class SushiswapV2LP(UniswapV2LP):

    __slots__ = ("reserves0", "reserves1", "fees_as_fraction")

    def to_json(self) -> str:
        return json.dumps({
            "address": str(self.address),
            "token0": str(self.token0),
            "token1": str(self.token1),
            "reserves0": self.reserves0,
            "reserves1": self.reserves1,
            "type": "SushiswapV2LP"
        })


def sushi_v2_from_json(json_str: str) -> SushiswapV2LP:
    obj_dict = json.loads(json_str)
    return SushiswapV2LP(Address(obj_dict["address"]),
                         RToken(obj_dict["token0"]),
                         RToken(obj_dict["token1"]),
                         obj_dict["reserves0"],
                         obj_dict["reserves1"])
