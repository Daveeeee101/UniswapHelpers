import unittest
from Web3Types.SimpleTypes import *
from Web3Types.Block import *
from Web3Types.TransactionLog import *


class TestSimpleTypes(unittest.TestCase):
    def test_hex_eq(self):
        hex_test = HexBytes("0x24365783")
        hex_test_2 = HexBytes("0x24365783")
        self.assertEqual(hex_test, hex_test_2)

    def test_hex_index(self):
        hex_test = HexBytes("0x123456789a")
        hex_test_2 = HexBytes("0x12")
        self.assertEqual(hex_test[0], hex_test_2)

    def test_hex_int(self):
        hex_test = HexBytes("0x123456789a")
        self.assertEqual(78187493530, int(hex_test))

    def test_hex_slice(self):
        hex_test = HexBytes("0x123456789a")
        hex_test_2 = HexBytes("0x3456")
        self.assertEqual(hex_test_2, hex_test[1:3])

    def test_address_length(self):
        with self.assertRaises(InvalidAddress):
            _ = Address("0x5234")

    def test_address_checksum(self):
        address = Address("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")
        self.assertEqual(str(address), "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")


class TestBlockType(unittest.TestCase):

    test_block_1 = Block(
        HexBytes("0xbe21d4c0526d83786540d98ddb24ff41867a3497d28bd3f644e5f4c1e7ea0090"),
        12420075,
        HexBytes("0x"),
        Address("0x4675C7e5BaAFBFFbca748158bEcBA61ef3b0a263"),
        17487971,
        HexBytes("0x9660b8a1ce762bf846d2d6641a5baef0b1c44592faa0d8ebc1ee0e3dd459660d"),
        1686865056
        )

    def test_block_equal(self):
        b1 = self.test_block_1
        b2 = self.test_block_1
        b2.number += 1
        self.assertEqual(b1, b2)


class TestLogType(unittest.TestCase):

    log_1 = Log(HexBytes("0x06ce1c2a2bf4be3cc7f8cfbde9b29b3035dd35f551aea177e829905f0423f899"),
                        17514397,
                        114,
                        Address("0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"),
                        226,
                        HexBytes(
                            "0x0000000000000000000000000000000000000000000000000000000077359400ffffffffffffffffffffffffffffffffffffffffffffffffefdf78616e9e6a8c0000000000000000000000000000000000005e2ec01dc1bd773f69f88e02cb360000000000000000000000000000000000000000000000012e2b29926a2e7ded000000000000000000000000000000000000000000000000000000000003145a"),
                        False,
                        [HexBytes("0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"),
                         HexBytes("0x000000000000000000000000def1c0ded9bec7f1a1670819833240f027b25eff"),
                         HexBytes("0x000000000000000000000000def1c0ded9bec7f1a1670819833240f027b25eff")],
                        HexBytes("0x437f02b06f96645e6ec3a7f6f8b6638bc9bcab3a8f33cd8d453b6ebbb197055b"))

    log1_dup = Log(HexBytes("0x06ce1c2a2bf4be3cc7f8cfbde9b29b3035dd35f551aea177e829905f0423f899"),
                            17514397,
                            114,
                            Address("0x88e6A0c2dDD26FEEb64F039a2c41296FcB3f5640"),
                            226,
                            HexBytes("0x0000000000000000000000000000000000000000000000000000000077359400ffffffffffffffffffffffffffffffffffffffffffffffffefdf78616e9e6a8c0000000000000000000000000000000000005e2ec01dc1bd773f69f88e02cb360000000000000000000000000000000000000000000000012e2b29926a2e7ded000000000000000000000000000000000000000000000000000000000003145a"),
                            False,
                            [HexBytes("0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"), HexBytes("0x000000000000000000000000def1c0ded9bec7f1a1670819833240f027b25eff"), HexBytes("0x000000000000000000000000def1c0ded9bec7f1a1670819833240f027b25eff")],
                            HexBytes("0x437f02b06f96645e6ec3a7f6f8b6638bc9bcab3a8f33cd8d453b6ebbb197055b"))

    def test_log_eq(self):
        self.assertEqual(self.log_1, self.log1_dup)

    def test_log_get_topic(self):
        self.assertEqual(HexBytes("0xc42079f94a6350d7e6235f29174924f928cc2ac818eb64fed8004e115fbcca67"), self.log_1.get_topic())

    def test_log_to_and_from_json(self):
        result = log_from_json(self.log_1.to_json())
        actual_result = self.log_1
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


if __name__ == '__main__':
    unittest.main()
