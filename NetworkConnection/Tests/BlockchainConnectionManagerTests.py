import time
import unittest

from Web3Types.Transaction import SmartContractTransaction
from NetworkConnection.AlchemyRPCRequests import AlchemyCallRequest
from NetworkConnection.RPCConnection import HTTPRPCConnection
from Definitions import config_load
from NetworkConnection.BlockchainConnectionManager import BlockchainConnectionManager, LPDoesNotExist
from UniswapTypes.UniswapV2LP import UniswapV2LP
from UniswapTypes.RToken import RToken
from Web3Types.SimpleTypes import Address, HexBytes
from Web3Types.TransactionLog import Log
import Utilities.FunctionCallBuilder as fcb


class BlockchainConnectionManagerTests(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        http_url = config_load()["test_infura_http"]
        http_url = config_load()["test_alchemy_http"]
        connection = HTTPRPCConnection(http_url)
        connection.enter()
        self.mgr = BlockchainConnectionManager(connection)

    async def asyncTearDown(self):
        await self.mgr.connection.clean_up()

    async def test_gets_latest_lp(self):
        _ = await self.mgr.get_uniswap_v2_liquidity_pool("0xCbF35A6130eE786BD0fE955f0F36a22f59Bfbd4C")

    async def test_historic_lp_correct_1(self):
        block = 17507897
        lp_actual = UniswapV2LP("0xCbF35A6130eE786BD0fE955f0F36a22f59Bfbd4C",
                                RToken("0x3F17f64F682019599ba51638f74E4b6C127FE725"),
                                RToken("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"),
                                694824967645553686087549594,
                                27938609010183341897)
        lp_test = await self.mgr.get_uniswap_v2_liquidity_pool("0xCbF35A6130eE786BD0fE955f0F36a22f59Bfbd4C", block)
        self.assertEqual(lp_actual.address, lp_test.address)
        self.assertEqual(lp_actual.token0, lp_test.token0)
        self.assertEqual(lp_actual.token1, lp_test.token1)
        self.assertEqual(lp_actual.reserves0, lp_actual.reserves0)
        self.assertEqual(lp_actual.reserves1, lp_actual.reserves1)

    async def test_historic_lp_correct_2(self):
        pass

    async def test_null_address_error_v2(self):
        with self.assertRaises(LPDoesNotExist):
            block = 17507897
            _ = await self.mgr.get_uniswap_v2_liquidity_pool("0x0000000000000000000000000000000000000000", block)

    async def test_fill_slots_and_bitmap(self):
        actual_bitmap_dict = {-1085: 0, -1084: 0, -1083: 0, -1082: 0, -1081: 0, -1080: 97277612540743419483661303981731463519712739955048448, -1079: 0, -1078: 0, -1077: 0, -1076: 0, -1090: 0, -1089: 0, -1088: 0, -1087: 0, -1086: 0, -1075: 0, -1074: 0, -1073: 0, -1072: 0, -1071: 0}
        actual_slots_dict = {-276335: (21060899169008559, 21060899169008559), -276339: (13722657657928712149, 13722657657928712149), -276344: (72761643254310, 72761643254310), -276331: (4261793027292301978684, 4261793027292301978684), -276328: (-691032471859547363301, 691032471859547363301), -276327: (-3542300605843963954965, 3542300605843963954965), -276325: (-28481010487959668977, 28481010487959668977), -276310: (-13722657657928712149, 13722657657928712149), -276304: (-72761643254310, 72761643254310)}

        block_number = 17506153
        address = Address("0x9A834b70C07C81a9fcD6F22E842BF002fBfFbe4D")
        start_tick = -276334
        spacing = 1

        bitmap_dict, slots_dict = await self.mgr.fill_slots_and_bitmap(address, start_tick, spacing, 10, block_number)
        for (k1, v1), (k2, v2) in zip(actual_bitmap_dict.items(), bitmap_dict.items()):
            self.assertEqual(k1, k2)
            self.assertEqual(v1, v2)
        for (k1, v1), (k2, v2) in zip(actual_slots_dict.items(), slots_dict.items()):
            self.assertEqual(k1, k2)
            self.assertEqual(v1, v2)

    async def test_historic_lpV3_correct_1(self):
        block_number = 17507076
        lp = await self.mgr.get_uniswap_v3_liquidity_pool("0x9A834b70C07C81a9fcD6F22E842BF002fBfFbe4D", 10, block_number)
        self.assertEqual(lp.token0, RToken("0x853d955aCEf822Db058eb8505911ED77F175b99e"))
        self.assertEqual(lp.token1, RToken("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"))
        self.assertEqual(lp.liquidity, 13743791318740975018)
        self.assertEqual(lp.sqrtPriceX96, 79191246464685355724344)
        self.assertEqual(lp.current_tick, -276334)
        self.assertEqual(lp.tick_spacing, 1)
        self.assertEqual(lp.fee, 100)
        self.assertEqual(lp.reserves1, 8769408447)
        self.assertEqual(lp.reserves0, 838494288263123713799215)
        self.assertEqual(lp.slots_dict[-276335][0], 21060899169008559)

    async def test_get_v3_mint_logs_default(self):
        address = Address("0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640")
        _ = await self.mgr.get_v3_mint_logs(address)

    async def test_get_v3_mint_logs_1(self):
        block_start = 17514235
        block_end = 17514237
        address = Address("0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640")
        actual_result = Log(HexBytes("0x11ef69c33d1720ea554e185b290b563163174fd625ef14aa6c1e3d0fdfeb9dd1"),
                            17514236,
                            6,
                            Address("0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"),
                            39,
                            HexBytes("0x0000000000000000000000009a5f2e0db22ff289d0cc40ef654a19a5b012d8aa00000000000000000000000000000000000000000000005dd876011a0fe8929c00000000000000000000000000000000000000000000000000000eaa2899960600000000000000000000000000000000000000000000026ec43859697da54064"),
                            False,
                            [HexBytes("0x7a53080ba414158be7ec69b987b5fb7d07dee101fe85488f0853ae16239d0bde"), HexBytes("0x000000000000000000000000a69babef1ca67a37ffaf7a485dfff3382056e78c"), HexBytes("0x000000000000000000000000000000000000000000000000000000000003142a"), HexBytes("0x0000000000000000000000000000000000000000000000000000000000031434")],
                            HexBytes("0xf858a2cf5f3e4333ef91276f7c1a4c8a3e3bd078d9fc6aacd51e775ff5304c54"))
        result = await self.mgr.get_v3_mint_logs(address, block_start, block_end)
        result = result[0]
        self.assertEqual(actual_result.address, result.address)
        self.assertEqual(actual_result.data, result.data)
        self.assertEqual(actual_result.log_index, result.log_index)
        self.assertEqual(actual_result.transaction_hash, result.transaction_hash)
        self.assertEqual(actual_result.block_number, result.block_number)
        self.assertEqual(actual_result.block_hash, result.block_hash)
        self.assertEqual(actual_result.transaction_index, result.transaction_index)
        self.assertEqual(actual_result.transaction_hash, result.transaction_hash)
        for ar, r in zip(actual_result.topics, result.topics):
            self.assertEqual(ar, r)

    async def test_get_v3_all_logs_swap(self):
        block_start = 17514396
        block_end = 17514398
        address = Address("0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640")
        actual_result = Log(HexBytes("0x06ce1c2a2bf4be3cc7f8cfbde9b29b3035dd35f551aea177e829905f0423f899"),
                            17514397,
                            114,
                            Address("0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"),
                            226,
                            HexBytes("0x0000000000000000000000000000000000000000000000000000000077359400ffffffffffffffffffffffffffffffffffffffffffffffffefdf78616e9e6a8c0000000000000000000000000000000000005e2ec01dc1bd773f69f88e02cb360000000000000000000000000000000000000000000000012e2b29926a2e7ded000000000000000000000000000000000000000000000000000000000003145a"),
                            False,
                            [HexBytes("0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"), HexBytes("0x000000000000000000000000def1c0ded9bec7f1a1670819833240f027b25eff"), HexBytes("0x000000000000000000000000def1c0ded9bec7f1a1670819833240f027b25eff")],
                            HexBytes("0x437f02b06f96645e6ec3a7f6f8b6638bc9bcab3a8f33cd8d453b6ebbb197055b"))
        result = await self.mgr.get_v3_logs(address, ["Swap"], block_start, block_end)
        result = result[0]
        self.assertEqual(actual_result.address, result.address)
        self.assertEqual(actual_result.data, result.data)
        self.assertEqual(actual_result.log_index, result.log_index)
        self.assertEqual(actual_result.transaction_hash, result.transaction_hash)
        self.assertEqual(actual_result.block_number, result.block_number)
        self.assertEqual(actual_result.block_hash, result.block_hash)
        self.assertEqual(actual_result.transaction_index, result.transaction_index)
        self.assertEqual(actual_result.transaction_hash, result.transaction_hash)
        for ar, r in zip(actual_result.topics, result.topics):
            self.assertEqual(ar, r)

    async def test_get_v2_factory_logs_stress_test(self):
        block_start = 11000000
        block_end = 15000000
        address = Address("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")
        t1 = time.perf_counter()
        results = await self.mgr.get_v2_factory_logs(address, block_start, block_end)
        t2 = time.perf_counter()
        print(len(results))
        print(t2 - t1)

    async def test_validate_pool(self):
        amount_in = 1000000000000000
        test_lp_1 = await self.mgr.get_uniswap_v2_liquidity_pool("0xed06839ED05219b87CBd39dd8F9495e02497bc10")
        first_out = test_lp_1.simulate_swap(amount_in, 0)
        tokens_out = [first_out]
        exchange_types = [0]
        lp_path = [str(test_lp_1.address)]
        directions = [True]
        configs = config_load()
        address = configs['validate_graph_address']
        bytecode = configs['validate_graph_bytecode']
        eth_address = Address(address)
        print(first_out)
        test_transaction = AlchemyCallRequest(
            SmartContractTransaction(fcb.get_abi_function("get_path_token_output", "validateGraph"),
                                     (lp_path, directions, exchange_types, tokens_out, amount_in), eth_address, 0,
                                     eth_address), bytecode, eth_address)
        result = await self.mgr.connection.send_request(test_transaction)
        print(result)


if __name__ == '__main__':
    unittest.main()
