import json
from typing import List
from Utilities.FunctionCallBuilder import decode_event_output, decode_topic_data
from Web3Types.SimpleTypes import HexBytes, Address


class Log:

    def __init__(self, block_hash: HexBytes, block_number: int, transaction_index: int, address: Address,
                 log_index: int, data: HexBytes, removed: bool, topics: List, transaction_hash: HexBytes):
        self.block_hash: HexBytes = block_hash
        self.block_number: int = block_number
        self.transaction_index: int = transaction_index
        self.address: Address = address
        self.log_index: int = log_index
        self.removed: bool = removed
        self.topics: List = topics
        self.transaction_hash: HexBytes = transaction_hash
        self.data: HexBytes = data
        self.decoded_data = None
        self.decoded_topics = None

    def decode_data(self, event_abi):
        self.decoded_data = decode_event_output(self.data, event_abi)
        self.decoded_topics = decode_topic_data(self.topics, event_abi)
        return self.decoded_data

    def get_topic(self):
        return self.topics[0]

    def __str__(self):
        return f"{self.block_number}, {self.transaction_hash}, {self.decoded_data}"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return self.transaction_hash == other.transaction_hash and self.log_index == other.log_index

    def __hash__(self):
        return hash(hash(self.transaction_hash) + hash(self.log_index))

    def to_json(self) -> str:
        """Note that saving and loading a log to json will lose its decoded_data which will need to be re-initialised"""
        return json.dumps({
            "block_hash": str(self.block_hash),
            "block_number": self.block_number,
            "transaction_index": self.transaction_index,
            "address": str(self.address),
            "log_index": self.log_index,
            "removed": self.removed,
            "topics": [str(t) for t in self.topics],
            "transaction_hash": str(self.transaction_hash),
            "data": str(self.data)
        })


def log_from_json(json_str: str) -> Log:
    """Note that saving and loading a log to json will lose its decoded_data which will need to be re-initialised"""
    obj_dict = json.loads(json_str)
    return Log(
        HexBytes(obj_dict["block_hash"]),
        obj_dict["block_number"],
        obj_dict["transaction_index"],
        Address(obj_dict["address"]),
        obj_dict["log_index"],
        HexBytes(obj_dict["data"]),
        obj_dict["removed"],
        [HexBytes(f) for f in obj_dict["topics"]],
        HexBytes(obj_dict["transaction_hash"])
    )

