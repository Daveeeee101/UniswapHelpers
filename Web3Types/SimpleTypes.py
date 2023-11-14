from __future__ import annotations
from web3 import Web3


class HexError(Exception):
    pass


class HexBytes:
    """A class that represents bytes as a hex object"""

    __slots__ = "__hex_bytes"

    def __init__(self, hex_in: str | bytes | int):
        if type(hex_in) == int:
            self.__hex_bytes: bytes = bytes(hex_in)
        elif type(hex_in) == bytes:
            self.__hex_bytes: bytes = hex_in
        elif hex_in[:2] == "0x":
            if len(hex_in) % 2 != 0:
                raise HexError("Hex string should have even length to represent full bytes")
            self.__hex_bytes: bytes = bytes.fromhex(hex_in[2:])
        else:
            raise HexError("Hex string should start with 0x identifier")

    def __repr__(self):
        return "0x" + self.__hex_bytes.hex()

    def __str__(self):
        return "0x" + self.__hex_bytes.hex()

    def __eq__(self, other):
        return self.__hex_bytes == other.__hex_bytes

    def __len__(self):
        return len(self.__hex_bytes)

    def __hash__(self):
        return int.from_bytes(self.__hex_bytes, "big")

    def __getitem__(self, item):
        if isinstance(item, slice):
            return HexBytes(self.__hex_bytes[item.start:item.stop:item.step])
        else:
            return HexBytes(self.__hex_bytes[item:item+1])

    def __bytes__(self):
        return self.__hex_bytes

    def __int__(self):
        return int.from_bytes(self.__hex_bytes, "big")


class InvalidAddress(Exception):
    pass


class Address:
    """A class for storing address data from Ethereum"""
    __slots__ = "__hex_bytes"

    def __init__(self, hex_string: str | HexBytes):
        if type(hex_string) == str:
            self.__hex_bytes: HexBytes = HexBytes(hex_string)
        elif type(hex_string) == HexBytes:
            self.__hex_bytes: HexBytes = hex_string
        if len(self.__hex_bytes) != 20:
            raise InvalidAddress(f"Addresses are 20 bytes long, given address = {len(self.__hex_bytes)} bytes!")

    def __repr__(self):
        return Web3.to_checksum_address(str(self.__hex_bytes))

    def __str__(self):
        return str(Web3.to_checksum_address(str(self.__hex_bytes)))

    def __eq__(self, other):
        return self.__hex_bytes == other.__hex_bytes

    def __hash__(self):
        return hash(self.__hex_bytes)


NULL_ADDRESS = Address("0x0000000000000000000000000000000000000000")
