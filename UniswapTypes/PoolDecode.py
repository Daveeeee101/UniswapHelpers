import json
from UniswapTypes.PancakeswapV2LP import pancake_v2_from_json
from UniswapTypes.ShibaswapV2LP import shiba_v2_from_json
from UniswapTypes.SushiswapV2LP import sushi_v2_from_json
from UniswapTypes.UniswapV2LP import v2_from_json
from UniswapTypes.UniswapV3LP import v3_from_json
from UniswapTypes.XchangeV2LP import xchange_v2_from_json


def decode_json_lp(lp_str: str):
    lp_json = json.loads(lp_str)
    if lp_json['type'] == "UniswapV2LP":
        lp = v2_from_json(lp_str)
    elif lp_json['type'] == "PancakeswapV2LP":
        lp = pancake_v2_from_json(lp_str)
    elif lp_json['type'] == "ShibaswapV2LP":
        lp = shiba_v2_from_json(lp_str)
    elif lp_json['type'] == "SushiswapV2LP":
        lp = sushi_v2_from_json(lp_str)
    elif lp_json['type'] == "XchangeV2LP":
        lp = xchange_v2_from_json(lp_str)
    elif lp_json['type'] == "UniswapV3LP":
        lp = v3_from_json(lp_str)
    else:
        raise NotImplementedError(f"Exchange type {lp_json['type']} not yet implemented!")
    return lp
