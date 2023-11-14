from Web3Types.SimpleTypes import HexBytes, Address


class Block:
    """Class representing an Ethereum Block"""

    __slots__ = ("block_hash", "gas_used", "logs_bloom", "miner", "number", "parent_hash", "timestamp")

    def __init__(self, block_hash: HexBytes, gasUsed: int, logsBloom: HexBytes, miner: Address, number: int, parent_hash: HexBytes, timestamp: int):
        self.block_hash: HexBytes = block_hash
        self.gas_used: int = gasUsed
        self.logs_bloom: HexBytes = logsBloom
        self.miner: Address = miner
        self.number: int = number
        self.parent_hash: HexBytes = parent_hash
        self.timestamp: int = timestamp

    def __repr__(self):
        return f"block {self.number} at {self.timestamp} with hash {self.block_hash}"

    def __str__(self):
        return str(self.block_hash)

    def __eq__(self, other):
        return self.block_hash == other.block_hash

    def __hash__(self):
        return hash(self.block_hash)


