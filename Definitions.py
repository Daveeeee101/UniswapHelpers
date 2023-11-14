import json
import os

from UniswapTypes.ILiquidityPool import ILiquidityPool
from UniswapTypes.PoolDecode import decode_json_lp
from UniswapTypes.RToken import RToken
from Web3Types.SimpleTypes import Address

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

WETH_TOKEN = RToken("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
NONE_ADDRESS = Address("0x0000000000000000000000000000000000000000")

TEST_BLOCK_NUMBER = 18041496


def config_load():
    with open(ROOT_DIR + "/Files/config.json") as f:
        return json.loads(f.read())


def get_test_liquidity_pool(pool_name: str) -> ILiquidityPool:
    with open(ROOT_DIR + "/Files/test_liquidity_pools.json") as f:
        liquidity_pools = json.loads(f.read())
        lp_str = liquidity_pools[pool_name]
        return decode_json_lp(lp_str)


def get_all_test_lp_names():
    with open(ROOT_DIR + "/Files/test_liquidity_pools.json") as f:
        liquidity_pools = json.loads(f.read())
        for lp in liquidity_pools:
            print(lp)

