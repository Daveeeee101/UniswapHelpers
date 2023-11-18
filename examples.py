import asyncio
from typing import Tuple

from UniswapTypes.UniswapV2LP import UniswapV2LP
from UniswapTypes.UniswapV3LP import UniswapV3LP
from NetworkConnection.RPCConnection import HTTPRPCConnection
from NetworkConnection.BlockchainConnectionManager import BlockchainConnectionManager
from Definitions import config_load
from Web3Types.SimpleTypes import Address
from Web3Types.Transaction import SmartContractTransaction
import Utilities.FunctionCallBuilder as fcb
from Definitions import NONE_ADDRESS
from NetworkConnection.BaseRPCRequests import CallRequest


async def get_a_single_uniswap_v2_and_v3_pool() -> Tuple[UniswapV2LP, UniswapV3LP]:

    # ----------------------
    # SETUP FOR CONNECTION
    config = config_load()
    async with HTTPRPCConnection(config["test_infura_http"]) as conn:
        mgr = BlockchainConnectionManager(conn)
    # ----------------------

        # ------------------
        # GET LIQUIDITY POOLS
        lp_address_v2 = Address("0xB4e16d0168e52d35CaCD2c6185b44281Ec28C9Dc")  # Uniswap V2: USDC pool
        lp_address_v3 = Address("0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640")  # Uniswap V3: USDC pool
        block_number_to_get_pool_info_for = 18566245

        v2_lp = await mgr.get_uniswap_v2_liquidity_pool(lp_address_v2, block_number_to_get_pool_info_for)
        v3_lp = await mgr.get_uniswap_v3_liquidity_pool(lp_address_v3, number_of_ticks=20, block_number=block_number_to_get_pool_info_for)
        # ------------------

        # ------------------
        # PRINT OUT SOME POOL INFO
        print(f"v2 lp reserves = {v2_lp.get_reserves()}")
        weth_out_for_usdc = v2_lp.simulate_swap(10_000_000_000_000, 0)  # be careful here with which token is token0 and which is token1
        print(f"swapping 10,000,000 USDC yields {weth_out_for_usdc / 1e18} WETH")  # recall that we don't care about decimals so these are large numbers
        print(f"Current v2 price is: {(cur_price := v2_lp.get_price())}")

        v2_price_after_swap = v2_lp.simulate_swap_price(10_000_000_000_000, 0)
        print(f"v2 price after swap is: {v2_price_after_swap}")

        print(f"v2 price impact was: {1 - (v2_price_after_swap / cur_price)}")

        print(f"v3 lp liquidity = {v3_lp.liquidity}, current tick = {v3_lp.current_tick}")
        weth_out_for_usdc = v3_lp.simulate_swap(10_000_000_000_000, 0)  # be careful here with which token is token0 and which is token1
        print(f"swapping 10,000,000 USDC yields {weth_out_for_usdc / 1e18} WETH")  # recall that we don't care about decimals so these are large numbers

        print(f"v3 price before swap was: {(cur_price := v3_lp.get_price())}")

        v3_price_after_swap = v3_lp.simulate_swap_price(10_000_000_000_000, 0)
        print(f"v3 price after swap is: {(v3_price_after_swap  ** 2 / 2 ** 192)}")

        print(f"v3 price impact was: {1 - ((v3_price_after_swap  ** 2 / 2 ** 192) / cur_price)}")
        # ------------------

        return v2_lp, v3_lp


async def get_uniswap_v3_price_from_smart_contract():
    config = config_load()
    async with HTTPRPCConnection(config["test_infura_http"]) as conn:

        block_number_to_test = 18566245
        lp_address_v3 = Address("0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640")  # Uniswap V3: USDC pool

        # --------------------
        # CREATE THE TRANSACTION AND THE REQUEST
        abi_function = fcb.get_abi_function("slot0", "V3LiquidityPool")

        transaction = SmartContractTransaction(abi_function, (), lp_address_v3, 0)
        request = CallRequest(transaction, block_number_to_test)
        # --------------------

        # --------------------
        # SEND THE TRANSACTION AND GET THE RESPONSE
        sqrtPriceX96, tick, observationIndex, ObservationCardinality, observationCardinalityNext, feeProtocol, unlocked = await conn.send_request(request)
        actual_price = sqrtPriceX96 ** 2 / 2 ** 192
        print(actual_price)
        return actual_price
        # --------------------


if __name__ == '__main__':
    asyncio.run(get_a_single_uniswap_v2_and_v3_pool())
