import asyncio
from NetworkConnection.BlockchainConnectionManager import BlockchainConnectionManager
from UniswapTypes.UniswapV3LP import *
from NetworkConnection.RPCConnection import HTTPRPCConnection
from Definitions import config_load


async def generate_v3_log_test_case(mgr: BlockchainConnectionManager, start_block: int, stop_block: int, address: Address, tick_number: int, log_types: List[str]):
    initial_state = await mgr.get_uniswap_v3_liquidity_pool(address, tick_number, start_block)
    final_state = await mgr.get_uniswap_v3_liquidity_pool(address, tick_number, stop_block)
    all_logs = []
    for log_type in log_types:
        logs = await mgr.get_v3_logs(address, [log_type], start_block + 1, stop_block)
        all_logs += logs
    print(len(all_logs))
    all_logs.sort(key=lambda log: (log.block_number, log.log_index))
    print(all_logs)
    return {
        "initial_state": initial_state.to_json(),
        "final_state": final_state.to_json(),
        "logs": [log.to_json() for log in all_logs]
    }


async def generate_v3_test_lp(mgr: BlockchainConnectionManager, address: Address, block_number: int, tick_number: int):
    test_lp = await mgr.get_uniswap_v3_liquidity_pool(address, tick_number, block_number)
    return test_lp.to_json()


async def generate_test_file():
    configs = config_load()
    with open("ArbitrageTypesTestCases.json", "w") as f:
        async with HTTPRPCConnection(configs["test_infura_http"]) as conn:
            mgr = BlockchainConnectionManager(conn)

            address_1 = Address("0x9A834b70C07C81a9fcD6F22E842BF002fBfFbe4D")
            block_number_1 = 17507076

            block_number_before_1 = 17514402
            block_number_after_1 = 17514403
            events_1 = ["Swap"]

            address_2 = Address("0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640")
            block_number_before_2 = 17510000
            block_number_after_2 = 17510669
            events_2 = ["Swap", "Mint", "Collect", "Flash", "Burn"]

            test_1 = await generate_v3_test_lp(mgr, address_1, block_number_1, 10)
            print("test_1 generated")

            test_2 = await generate_v3_log_test_case(mgr, block_number_before_1, block_number_after_1, address_1, 10, events_1)
            print("test_2 generated")

            test_3 = await generate_v3_log_test_case(mgr, block_number_before_2, block_number_after_2, address_2, 1000, events_2)
            print("test_3 generated")

            f.write(json.dumps({
                "test_1": test_1,
                "test_2": test_2,
                "test_3": test_3
            }))


async def add_to_test_file():
    configs = config_load()
    with open("ArbitrageTypesTestCases.json", "r+") as f:
        async with HTTPRPCConnection(configs["test_infura_http"]) as conn:
            mgr = BlockchainConnectionManager(conn)
            current_tests = f.read()
            current_file = json.loads(current_tests)

            address_2 = Address("0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640")
            block_number_before_1 = 17515484
            block_number_after_1 = 17515485
            events_1 = ["Mint"]

            test_4 = await generate_v3_log_test_case(mgr, block_number_before_1, block_number_after_1, address_2, 100,
                                                     events_1)
            print("test_4 generated")

            current_file["test_4"] = test_4

            f.seek(0)
            f.write(json.dumps(current_file))
            f.truncate()


async def test_5_generator():
    configs = config_load()
    with open("ArbitrageTypesTestCases.json", "r+") as f:
        async with HTTPRPCConnection(configs["test_infura_http"]) as conn:
            mgr = BlockchainConnectionManager(conn)
            current_tests = f.read()
            current_file = json.loads(current_tests)

            address_2 = Address("0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640")

            block_number_before_1 = 17515432
            block_number_after_1 = 17515433
            events_1 = ["Burn", "Collect"]

            test_5 = await generate_v3_log_test_case(mgr, block_number_before_1, block_number_after_1, address_2, 500,
                                                     events_1)
            print("test_5 generated")

            current_file["test_5"] = test_5

            f.seek(0)
            f.write(json.dumps(current_file))
            f.truncate()


async def test_6_generator():
    configs = config_load()
    with open("ArbitrageTypesTestCases.json", "r+") as f:
        async with HTTPRPCConnection(configs["test_infura_http"]) as conn:
            mgr = BlockchainConnectionManager(conn)
            current_tests = f.read()
            current_file = json.loads(current_tests)

            address = Address("0xa87De12EA019B7b55772BbFFc0d9a844F7327Ef9")
            block_number = 17633713

            test_6 = await mgr.get_uniswap_v3_liquidity_pool(address, 50, block_number)
            print("test_6 generated")

            current_file["test_6"] = test_6.to_json()

            f.seek(0)
            f.write(json.dumps(current_file))
            f.truncate()


async def test_7_generator():
    configs = config_load()
    with open("ArbitrageTypesTestCases.json", "r+") as f:
        async with HTTPRPCConnection(configs["test_infura_http"]) as conn:
            mgr = BlockchainConnectionManager(conn)
            current_tests = f.read()
            current_file = json.loads(current_tests)

            address = Address("0x919Fa96e88d67499339577Fa202345436bcDaf79")
            block_number = 17641814

            test_7 = await mgr.get_uniswap_v3_liquidity_pool(address, 50, block_number)
            print("test_7 generated")

            current_file["test_7"] = test_7.to_json()

            f.seek(0)
            f.write(json.dumps(current_file))
            f.truncate()


if __name__ == '__main__':
    asyncio.run(test_7_generator())
