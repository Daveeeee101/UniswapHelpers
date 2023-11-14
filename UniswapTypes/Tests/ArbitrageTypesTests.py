import unittest
from UniswapTypes.RToken import *
from UniswapTypes.UniswapV2LP import *
from UniswapTypes.UniswapV3LP import *
from UniswapTypes.SushiswapV2LP import *
from Web3Types.TransactionLog import *
from NetworkConnection.BlockchainConnectionManager import decode_v3_log_data, update_v3_pool_from_log


class RTokenTests(unittest.TestCase):
    def test_initialization(self):
        token1 = WETH_TOKEN
        token2 = RToken("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
        self.assertEqual(token1, token2)

    def test_ne(self):
        token1 = RToken("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
        token2 = RToken("0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48")
        self.assertNotEqual(token1, token2)

    def test_bad_instantiation(self):
        with self.assertRaises(BadTokenAddressError):
            _ = RToken(512)

    def test_repr(self):
        token1 = RToken("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
        self.assertEqual(token1.__repr__(), "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")

    def test_get_address(self):
        token1 = RToken("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
        self.assertEqual(token1.get_address(), Address("0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"))


class UniswapV2LPTests(unittest.TestCase):

    def test_eq(self):
        lp_1 = UniswapV2LP("0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852", WETH_TOKEN, USDC_TOKEN)
        lp_2 = UniswapV2LP("0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852", WETH_TOKEN, USDC_TOKEN)
        self.assertEqual(lp_1, lp_2)

    def test_simulate_swap_dir1(self):
        actual_result = 1642335
        amount_in = 1000000000000000
        lp = UniswapV2LP("0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852", WETH_TOKEN, USDC_TOKEN,
                         17184584621057525854377, 28307786847252)
        self.assertEqual(lp.simulate_swap(amount_in, 0), actual_result)

    def test_simulate_swap_dir2(self):
        actual_result = 605240895595919
        amount_in = 1000000
        lp = UniswapV2LP("0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852", WETH_TOKEN, USDC_TOKEN,
                         17184584621057525854377, 28307786847252)
        self.assertEqual(actual_result, lp.simulate_swap(0, amount_in))

    def test_swap_excess_reserves(self):
        with self.assertRaises(InsufficientReserves):
            lp = UniswapV2LP("0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852", WETH_TOKEN, USDC_TOKEN,
                             17184584621057525854377, 28307786847252)
            lp.simulate_swap(0, 30000000000000)

    def test_swap_reserves_correct(self):
        amount_in = 1000000000000000000
        final_reserves0 = 17194441560087687074744
        final_reserves1 = 28291644039496
        lp = UniswapV2LP("0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852", WETH_TOKEN, USDC_TOKEN,
                         17193441560087687074744, 28293284593483)
        lp.swap(amount_in, 0)
        self.assertEqual(final_reserves0, lp.reserves0)
        self.assertEqual(final_reserves1, lp.reserves1)

    def test_simulate_swap_large_number_dir1(self):
        actual_result = 10393406447036
        amount_in = 10000000000000000000000
        lp = UniswapV2LP("0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852", WETH_TOKEN, USDC_TOKEN,
                         17184584621057525854377, 28307786847252)
        self.assertEqual(lp.simulate_swap(amount_in, 0), actual_result)

    def test_simulate_swap_large_number_dir2(self):
        actual_result = 4475972170377543765760
        amount_in = 10000000000000
        lp = UniswapV2LP("0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852", WETH_TOKEN, USDC_TOKEN,
                         17184584621057525854377, 28307786847252)
        self.assertEqual(lp.simulate_swap(0, amount_in), actual_result)

    def test_save_and_load_to_json_v2(self):
        lp = UniswapV2LP("0x0d4a11d5EEaaC28EC3F61d100daF4d40471f1852", WETH_TOKEN, USDC_TOKEN,
                         17184584621057525854377, 28307786847252)
        str_json = lp.to_json()
        lp_from_json = v2_from_json(str_json)
        self.assertEqual(lp.address, lp_from_json.address)
        self.assertEqual(lp.token0, lp_from_json.token0)
        self.assertEqual(lp.token1, lp_from_json.token1)
        self.assertEqual(lp.reserves0, lp_from_json.reserves0)
        self.assertEqual(lp.reserves1, lp_from_json.reserves1)


class UniswapV3LPTests(unittest.TestCase):

    def setUp(self):
        with open("UniswapTypesTestCases.json", "r") as f:
            json_tests = json.loads(f.read())
            self.lp_1 = v3_from_json(json_tests["test_1"])

            self.test_2_json = json_tests["test_2"]

            self.test_3_json = json_tests["test_3"]

            self.test_4_json = json_tests["test_4"]

            self.test_5_json = json_tests["test_5"]

            self.test_6_lp = v3_from_json(json_tests["test_6"])

            self.test_7_lp = v3_from_json(json_tests["test_7"])

    def test_save_and_load_to_json_v3(self):
        orig = self.lp_1
        reconstruct = v3_from_json(orig.to_json())
        self.assertTrue(orig.deep_eq(reconstruct))
        for (k0, v0), (k1, v1) in zip(orig.slots_dict.items(), reconstruct.slots_dict.items()):
            self.assertEqual(k0, k1)
            self.assertEqual(v0, v1)
        for (k0, v0), (k1, v1) in zip(orig.slot_bitmap.items(), reconstruct.slot_bitmap.items()):
            self.assertEqual(k0, k1)
            self.assertEqual(v0, v1)

    def test_swap_event_update(self):
        before = v3_from_json(self.test_2_json["initial_state"])
        after = v3_from_json(self.test_2_json["final_state"])
        log_to_append = log_from_json(self.test_2_json["logs"][0])
        decode_v3_log_data(log_to_append)
        update_v3_pool_from_log(before, log_to_append)
        self.assertTrue(before.deep_eq(after))

    """def test_mint_event_update(self):
        before = v3_from_json(self.test_4_json["initial_state"])
        after = v3_from_json(self.test_4_json["final_state"])
        log_to_append = log_from_json(self.test_4_json["logs"][0])
        decode_v3_log_data(log_to_append)
        print(before.slots_dict)
        update_v3_pool_from_log(before, log_to_append)
        self.assertTrue(before.deep_eq(after))
"""

    def test_burn_collect_event_update(self):
        before = v3_from_json(self.test_5_json["initial_state"])
        after = v3_from_json(self.test_5_json["final_state"])
        logs_to_append = [log_from_json(l) for l in self.test_5_json["logs"]]
        for log in logs_to_append:
            decode_v3_log_data(log)
            update_v3_pool_from_log(before, log)
        print(before.reserves0, after.reserves0)
        print(before.reserves1, after.reserves1)
        self.assertTrue(before.deep_eq(after))

    def test_all_events_update(self):
        before = v3_from_json(self.test_3_json["initial_state"])
        after = v3_from_json(self.test_3_json["final_state"])
        logs_to_append = [log_from_json(l) for l in self.test_3_json["logs"]]
        for log in logs_to_append:
            t = decode_v3_log_data(log)
            if t == "Flash":
                print("flash swap")
            update_v3_pool_from_log(before, log)
        for i in after.slots_dict.keys():
            try:
                self.assertEqual(before.slots_dict[i], after.slots_dict[i])
            except KeyError:
                continue
        for i in after.slot_bitmap.keys():
            try:
                self.assertEqual(before.slot_bitmap[i], after.slot_bitmap[i])
            except KeyError:
                continue
        self.assertEqual(before.liquidity, after.liquidity)
        self.assertEqual(before.sqrtPriceX96, after.sqrtPriceX96)

    def test_virtual_reserves(self):
        test_lp = v3_from_json(self.test_5_json["final_state"])
        print(test_lp.get_virtual_reserves())
        print(test_lp.reserves0, test_lp.reserves1)

    def test_input_to_next_slot(self):
        test_lp = self.lp_1
        print(test_lp.address)
        out_list = test_lp.get_virtual_reserves_with_bounds(True, 3000000000)
        for bound, res in out_list:
            print(bound, res)

    def test_simulate_swap_1(self):
        amount_0_out = 992376978037097702003
        amount_1_in = 991250000
        before = v3_from_json(self.test_2_json["initial_state"])
        res = before.simulate_swap(0, amount_1_in)
        self.assertEqual(amount_0_out, res)

    def test_simulate_swap_2(self):
        lp = self.test_6_lp
        amount_0_out = 349234389104819421
        amount_1_in = 3107197391672937590
        res = lp.simulate_swap(0, amount_1_in)
        self.assertEqual(amount_0_out, res)

    def test_simulate_swap_3(self):
        lp = self.test_7_lp
        amount_0_in = 17058203424908115968
        amount_1_out = 41620918200879006630039
        res = lp.simulate_swap(amount_0_in, 0)
        self.assertEqual(amount_1_out, res)


if __name__ == '__main__':
    unittest.main()
