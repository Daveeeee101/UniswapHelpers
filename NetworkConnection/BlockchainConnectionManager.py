import asyncio

from NetworkConnection.BaseRPCRequests import *
from NetworkConnection.RPCConnection import HTTPRPCConnection
from typing import Union, Optional, Iterable, Set, Dict
from Web3Types.SimpleTypes import Address
import Utilities.FunctionCallBuilder as fcb
from UniswapTypes.UniswapV2LP import UniswapV2LP
from UniswapTypes.RToken import RToken
from UniswapTypes.UniswapV3LP import UniswapV3LP
from UniswapTypes.PancakeswapV2LP import PancakeswapV2LP
from UniswapTypes.ShibaswapV2LP import ShibaswapV2LP
from UniswapTypes.XchangeV2LP import XchangeV2LP
from Web3Types.TransactionLog import Log
from UniswapTypes.SushiswapV2LP import SushiswapV2LP

UNISWAP_V2_FACTORY = Address("0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f")
SUSHISWAP_V2_FACTORY = Address("0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac")
UNISWAP_V3_FACTORY = Address("0x1F98431c8aD98523631AE4a59f267346ea31F984")
PANCAKESWAP_V2_FACTORY = Address("0x1097053Fd2ea711dad45caCcc45EfF7548fCB362")
SHIBASWAP_V2_FACTORY = Address("0x115934131916C8b277DD010Ee02de363c09d037c")
XCHANGE_V2_FACTORY = Address("0x7de800467aFcE442019884f51A4A1B9143a34fAc")


class LPDoesNotExist(Exception):
    pass


class V3PoolProtocolFee(Exception):
    pass


class EventNotImplemented(Exception):
    pass


class FactoryAddressNotImplemented(Exception):
    pass


class MismatchAddress(Exception):
    pass


def create_v2_factory_lp(address: Address, token0: RToken, token1: RToken, reserves0: int, reserves1: int, factory: Address):
    if factory == SHIBASWAP_V2_FACTORY:
        return ShibaswapV2LP(address, token0, token1, reserves0, reserves1)
    elif factory == UNISWAP_V2_FACTORY:
        return UniswapV2LP(address, token0, token1, reserves0, reserves1)
    elif factory == SUSHISWAP_V2_FACTORY:
        return SushiswapV2LP(address, token0, token1, reserves0, reserves1)
    elif factory == PANCAKESWAP_V2_FACTORY:
        return PancakeswapV2LP(address, token0, token1, reserves0, reserves1)
    elif factory == XCHANGE_V2_FACTORY:
        return XchangeV2LP(address, token0, token1, reserves0, reserves1)
    else:
        raise NotImplementedError(f"Exchange type {factory} not yet implemented")


def create_v2_pool_from_factory_log(log: Log) -> UniswapV2LP:
    """Creates a v2 liquidity pool given a factory pairCreated log"""
    # need to convert addresses to 20 bytes long
    token0_addr = Address(log.topics[1][-20:])
    token1_addr = Address(log.topics[2][-20:])

    if log.address == UNISWAP_V2_FACTORY:
        return UniswapV2LP(log.decoded_data[0], RToken(token0_addr), RToken(token1_addr))
    elif log.address == SUSHISWAP_V2_FACTORY:
        return SushiswapV2LP(log.decoded_data[0], RToken(token0_addr), RToken(token1_addr))
    elif log.address == PANCAKESWAP_V2_FACTORY:
        return PancakeswapV2LP(log.decoded_data[0], RToken(token0_addr), RToken(token1_addr))
    elif log.address == SHIBASWAP_V2_FACTORY:
        return ShibaswapV2LP(log.decoded_data[0], RToken(token0_addr), RToken(token1_addr))
    elif log.address == XCHANGE_V2_FACTORY:
        return XchangeV2LP(log.decoded_data[0], RToken(token0_addr), RToken(token1_addr))
    else:
        raise FactoryAddressNotImplemented("Only Uniswap and Sushiswap V2 factory events are implemented")


def create_v3_pool_from_factory_log(log: Log) -> UniswapV3LP:
    """Creates a v3 liquidity pool given a factory pairCreated log"""
    # same as above
    token0_addr = Address(log.topics[1][-20:])
    token1_addr = Address(log.topics[2][-20:])

    if log.address == UNISWAP_V3_FACTORY:
        return UniswapV3LP(log.decoded_data[1],
                           RToken(token0_addr),
                           RToken(token1_addr),
                           log.decoded_data[0],
                           int(log.topics[3]))
    else:
        raise FactoryAddressNotImplemented("Only Uniswap V3 factory events are implemented")


def update_v2_pool_from_log(v2_liquidity_pool: UniswapV2LP, log: Log, event_topic: str):
    if v2_liquidity_pool.address != log.address:
        raise MismatchAddress("V2 liquidity pool address and log address don't match")
    sync_event = event_topic
    if log.topics[0] == sync_event:
        v2_liquidity_pool.sync(log.decoded_data[0],
                               log.decoded_data[1])
    else:
        raise EventNotImplemented("Only sync is implemented for uniswap V2 events")


def decode_v3_log_data(log: Log) -> str:
    swap_event = fcb.create_event_abi("Swap", fcb.get_abi("V3LiquidityPool"))
    mint_event = fcb.create_event_abi("Mint", fcb.get_abi("V3LiquidityPool"))
    burn_event = fcb.create_event_abi("Burn", fcb.get_abi("V3LiquidityPool"))
    flash_event = fcb.create_event_abi("Flash", fcb.get_abi("V3LiquidityPool"))
    collect_event = fcb.create_event_abi("Collect", fcb.get_abi("V3LiquidityPool"))
    initialize_event = fcb.create_event_abi("Initialize", fcb.get_abi("V3LiquidityPool"))
    if log.topics[0] == fcb.create_event_topic(swap_event):
        log.decode_data(swap_event)
        return "Swap"
    elif log.topics[0] == fcb.create_event_topic(mint_event):
        log.decode_data(mint_event)
        return "Mint"
    elif log.topics[0] == fcb.create_event_topic(burn_event):
        log.decode_data(burn_event)
        return "Burn"
    elif log.topics[0] == fcb.create_event_topic(flash_event):
        log.decode_data(flash_event)
        return "Flash"
    elif log.topics[0] == fcb.create_event_topic(collect_event):
        log.decode_data(collect_event)
        return "Collect"
    elif log.topics[0] == fcb.create_event_topic(initialize_event):
        log.decode_data(initialize_event)
        return "Initialize"
    else:
        raise EventNotImplemented("Couldn't find correct event to update")


def update_v3_pool_from_log(v3_liquidity_pool: UniswapV3LP, log: Log, swap_event: str, mint_event: str, burn_event: str, flash_event: str, collect_event: str, init_event: str):
    if v3_liquidity_pool.address != log.address:
        raise MismatchAddress("V3 liquidity pool address and log address don't match")
    initialize_event = init_event
    if log.topics[0] == swap_event:
        v3_liquidity_pool.swap_event(log.decoded_data[0],
                                     log.decoded_data[1],
                                     log.decoded_data[2],
                                     log.decoded_data[3],
                                     log.decoded_data[4])
    elif log.topics[0] == mint_event:
        v3_liquidity_pool.mint_event(log.decoded_topics[1],
                                     log.decoded_topics[2],
                                     log.decoded_data[1],
                                     log.decoded_data[2],
                                     log.decoded_data[3])
    elif log.topics[0] == burn_event:
        v3_liquidity_pool.burn_event(log.decoded_topics[1],
                                     log.decoded_topics[2],
                                     log.decoded_data[0],
                                     log.decoded_data[1],
                                     log.decoded_data[2])
    elif log.topics[0] == flash_event:
        v3_liquidity_pool.flash_event(log.decoded_data[2],
                                      log.decoded_data[3])
    elif log.topics[0] == collect_event:
        v3_liquidity_pool.collect_event(log.decoded_data[1],
                                        log.decoded_data[2])
    elif log.topics[0] == initialize_event:
        v3_liquidity_pool.initialize_event(log.decoded_data[0],
                                           log.decoded_data[1])
    else:
        raise EventNotImplemented("Couldn't find correct event to update")


class BlockchainConnectionManager:
    __slots__ = "connection"

    def __init__(self, connection: HTTPRPCConnection):
        self.connection = connection

    async def get_uniswap_v2_liquidity_pool(self, address: Union[str, Address],
                                            block_number: Optional[int] = None) -> UniswapV2LP:
        """gets a V2 liquidity pool from the blockchain - useful for small quantities of pools but will eat up requests
        if many pools are needed - try a different request. Can get historic values using block_number parameter."""
        if type(address) == str:
            address = Address(address)
        token0_transaction = CallRequest(
            SmartContractTransaction(fcb.get_abi_function("token0", "liquidityPool"), (), address, 0), block_number)
        token1_transaction = CallRequest(
            SmartContractTransaction(fcb.get_abi_function("token1", "liquidityPool"), (), address, 0), block_number)
        reserves_transaction = CallRequest(
            SmartContractTransaction(fcb.get_abi_function("getReserves", "liquidityPool"), (), address, 0),
            block_number)
        factory_transaction = CallRequest(
            SmartContractTransaction(fcb.get_abi_function("factory", "liquidityPool"), (), address, 0), block_number)
        batch = [token0_transaction, token1_transaction, reserves_transaction, factory_transaction]
        [token0, token1, reserves, factory] = await self.connection.send_batch_request(batch)
        if token0 is None or token1 is None or reserves is None:
            raise LPDoesNotExist(f"Return values unavailable on blockchain, most likely LP {address} doesn't exist")
        return create_v2_factory_lp(address, RToken(token0[0]), RToken(token1[0]), reserves[0], reserves[1], factory[0])

    async def fill_slots_and_bitmap(self, address: Address, starting_tick: int, spacing: int, number_of_ticks: int,
                                    block_number: Optional[int] = None):
        """helper function to fill out the slots and bitmap fields of a V3 liquidity pool. Assumes that if 5 bitmaps
        in a row are all zero's then no more ticks exist."""
        bitmap_dict = {}
        bitmap_tick_key = (starting_tick // spacing) // 256
        bitmap_tick_index = (starting_tick // spacing) % 256
        abi_function = fcb.get_abi_function("tickBitmap", "V3LiquidityPool")
        initial_bitmap_requests = [CallRequest(SmartContractTransaction(abi_function, (i,), address, 0), block_number)
                                   for i in range(bitmap_tick_key - 5, bitmap_tick_key + 5, 1)]
        initial_bitmap_indexes = [i for i in range(bitmap_tick_key - 5, bitmap_tick_key + 5, 1)]
        bitmaps = await self.connection.send_batch_request(initial_bitmap_requests)
        for index, value in zip(initial_bitmap_indexes, bitmaps):
            bitmap_dict[index] = value[0]
        ticks_to_get = []
        previous_len = 0

        current_bitmap_lower = bitmap_tick_key
        index_lower = bitmap_tick_index + 1

        current_bitmap_upper = bitmap_tick_key
        index_upper = bitmap_tick_index + 1

        while True:
            # get the lower ticks first
            loop_flag = True
            while current_bitmap_lower >= min(bitmap_dict.keys()):
                while index_lower > 0:
                    index_lower -= 1
                    t_lower = (1 << index_lower) & bitmap_dict[current_bitmap_lower]
                    if t_lower != 0:
                        ticks_to_get.append((index_lower * spacing) + (current_bitmap_lower * spacing * 256))
                        if len(ticks_to_get) >= number_of_ticks // 2:
                            loop_flag = False
                            break
                if not loop_flag:
                    break
                index_lower = 255
                current_bitmap_lower -= 1

            # now get the upper ticks
            loop_flag = True

            t_upper = (1 << index_upper) & bitmap_dict[current_bitmap_upper]
            while current_bitmap_upper <= max(bitmap_dict.keys()):
                while index_upper < 256:
                    if t_upper != 0:
                        ticks_to_get.append((index_upper * spacing) + (current_bitmap_upper * spacing * 256))
                        if len(ticks_to_get) >= number_of_ticks:
                            loop_flag = False
                            break
                    index_upper += 1
                    t_upper = (1 << index_upper) & bitmap_dict[current_bitmap_upper]
                if not loop_flag:
                    break
                index_upper = 0
                current_bitmap_upper += 1

            if len(ticks_to_get) < number_of_ticks and previous_len != len(ticks_to_get):
                min_bitmap = min(bitmap_dict.keys())
                max_bitmap = max(bitmap_dict.keys())
                new_bitmap_requests_lower = [
                    CallRequest(SmartContractTransaction(abi_function, (i,), address, 0), block_number)
                    for i in range(min_bitmap - 5, min_bitmap, 1)]
                new_bitmap_requests_upper = [
                    CallRequest(SmartContractTransaction(abi_function, (i,), address, 0), block_number)
                    for i in range(max_bitmap + 1, max_bitmap + 6, 1)]
                new_bitmap_indexes = [i for i in range(min_bitmap - 5, min_bitmap, 1)] + [i for i in
                                                                                          range(max_bitmap + 1,
                                                                                                max_bitmap + 6, 1)]

                bitmaps_lower = await self.connection.send_batch_request(new_bitmap_requests_lower)
                bitmaps_upper = await self.connection.send_batch_request(new_bitmap_requests_upper)

                bitmaps = bitmaps_lower + bitmaps_upper
                for index, value in zip(new_bitmap_indexes, bitmaps):
                    bitmap_dict[index] = value[0]
                previous_len = len(ticks_to_get)
            else:
                break

        # Finally get the slots information for the ticks we have found
        slots_abi = fcb.get_abi_function("ticks", "V3LiquidityPool")
        slots_batch_request = [CallRequest(SmartContractTransaction(slots_abi, (slot_index,), address, 0), block_number)
                               for slot_index in ticks_to_get]
        slots_response = await self.connection.send_batch_request(slots_batch_request)
        slots_dict = {key: (value[1], value[0]) for key, value in zip(ticks_to_get, slots_response)}
        return bitmap_dict, slots_dict

    async def get_uniswap_v3_liquidity_pool(self, address: Union[str, Address], number_of_ticks: int = 10,
                                            block_number: Optional[int] = None) -> UniswapV3LP:
        """gets a V3 liquidity pool from the blockchain - useful for small quantities of pools but will eat up requests
                if many pools are needed - try a different request. Can get historic values using block_number parameter.
                Can specify how many ticks above and below the current tick should be obtained from the blockchain using ticks_plus_and_minus
                """
        if type(address) == str:
            address = Address(address)
        token0_transaction = CallRequest(
            SmartContractTransaction(fcb.get_abi_function("token0", "V3LiquidityPool"), (), address, 0), block_number)
        token1_transaction = CallRequest(
            SmartContractTransaction(fcb.get_abi_function("token1", "V3LiquidityPool"), (), address, 0), block_number)
        abi_function = fcb.get_abi_function("tickSpacing", "V3LiquidityPool")
        tick_spacing_transaction = CallRequest(SmartContractTransaction(abi_function, (), address, 0), block_number)
        abi_function = fcb.get_abi_function("fee", "V3LiquidityPool")
        fee_transaction = CallRequest(SmartContractTransaction(abi_function, (), address, 0), block_number)
        abi_function = fcb.get_abi_function("liquidity", "V3LiquidityPool")
        liquidity_transaction = CallRequest(SmartContractTransaction(abi_function, (), address, 0), block_number)
        abi_function = fcb.get_abi_function("slot0", "V3LiquidityPool")
        slot0_transaction = CallRequest(SmartContractTransaction(abi_function, (), address, 0), block_number)
        batch = [token0_transaction, token1_transaction, tick_spacing_transaction, fee_transaction,
                 liquidity_transaction, slot0_transaction]
        [token0, token1, tick_spacing, fee, liquidity, slot0] = await self.connection.send_batch_request(batch)
        if token0 is None or token1 is None or tick_spacing is None or fee is None or slot0 is None:
            raise LPDoesNotExist(f"Return values unavailable on blockchain, most likely LP {address} doesn't exist")
        token0 = token0[0]
        token1 = token1[0]
        tick_spacing = tick_spacing[0]
        fee = fee[0]
        liquidity = liquidity[0]
        sqrtPriceX96 = slot0[0]
        current_tick = slot0[1]
        protocol_fee = slot0[5]
        if protocol_fee != 0:
            raise V3PoolProtocolFee(f"The liquidity pool {address} has a protocol fee!")
        reserves0_transaction = CallRequest(
            SmartContractTransaction(fcb.get_abi_function("balanceOf", "token"), (address,), token0, 0), block_number)
        reserves1_transaction = CallRequest(
            SmartContractTransaction(fcb.get_abi_function("balanceOf", "token"), (address,), token1, 0), block_number)
        bitmap_dict, slots_dict = await self.fill_slots_and_bitmap(address, current_tick, tick_spacing, number_of_ticks,
                                                                   block_number)
        batch = [reserves0_transaction, reserves1_transaction]
        [reserves0, reserves1] = await self.connection.send_batch_request(batch)
        reserves0 = reserves0[0]
        reserves1 = reserves1[0]
        return UniswapV3LP(
            address,
            RToken(token0),
            RToken(token1),
            tick_spacing,
            fee,
            current_tick,
            liquidity,
            sqrtPriceX96,
            reserves0,
            reserves1,
            slots_dict,
            bitmap_dict
        )

    async def get_v3_mint_logs(self, address: Address, block_start: Optional[int] = None,
                               block_end: Optional[int] = None) -> List[Log]:
        """gets all mint logs for an address between certain blocks, defaulting to the most recent block"""
        event_abi = fcb.create_event_abi("Mint", fcb.get_abi("V3LiquidityPool"))
        if block_start is None:
            block_start = "latest"
        if block_end is None:
            block_end = "latest"
        request = GetLogsRequest(block_start, block_end, [event_abi], address)
        result = await self.connection.send_request(request)
        return result

    async def get_v3_logs(self, event_abi: Dict, address: Address = None,
                          block_start: Optional[int] = None,
                          block_end: Optional[int] = None) -> List[Log]:
        """gets all v3 logs for an address (or all addresses) between certain blocks, defaulting to the most recent block, with specific log types given
        in the parameter event_types"""
        use_smart_logs = True
        if block_start is None and block_end is None:
            block_start = "latest"
            block_end = "latest"
            use_smart_logs = False
        elif block_start is None and block_end is not None or block_start is not None and block_end is None:
            raise ValueError("Either both blocks should be specified or neither")
        else:
            if block_end - block_start < 100:
                use_smart_logs = False
        request = GetLogsRequest(block_start, block_end, [event_abi], address)
        if use_smart_logs:
            result = await self.connection.smart_send_log_request(request)
        else:
            result = await self.connection.send_request(request)
        return result

    # TODO -- TEST
    async def get_v2_sync_logs(self, event_abi: Dict, address: Address = None, block_start: Optional[int] = None,
                               block_end: Optional[int] = None) -> List[Log]:
        """gets all v2 sync logs for an address (or all addresses) between certain blocks, defaulting to the most recent block."""
        if block_start is None:
            block_start = "latest"
        if block_end is None:
            block_end = "latest"
        request = GetLogsRequest(block_start, block_end, [event_abi], address)
        result = await self.connection.smart_send_log_request(request)
        return result

    # TODO -- TEST
    async def get_v2_factory_logs(self, address: Address, block_start: Optional[int] = None,
                                  block_end: Optional[int] = None) -> List[Log]:
        """gets all v2 factory logs for an address (or all addresses) between certain blocks, defaulting to the most recent block."""
        use_smart_logs = True
        if block_start is None and block_end is None:
            block_start = "latest"
            block_end = "latest"
            use_smart_logs = False
        elif block_start is None and block_end is not None or block_start is not None and block_end is None:
            raise ValueError("Either both blocks should be specified or neither")
        else:
            if block_end - block_start < 2000:
                use_smart_logs = False
        request = GetLogsRequest(block_start, block_end, [fcb.create_event_abi("PairCreated", fcb.get_abi("factory"))],
                                 address)
        if use_smart_logs:
            result = await self.connection.smart_send_log_request(request)
        else:
            result = await self.connection.send_request(request)
        return result

    # TODO -- TEST
    async def get_v3_factory_logs(self, address: Address, block_start: Optional[int] = None,
                                  block_end: Optional[int] = None) -> List[Log]:
        """gets all v3 factory logs for an address (or all addresses) between certain blocks, defaulting to the most recent block."""
        use_smart_logs = True
        if block_start is None and block_end is None:
            block_start = "latest"
            block_end = "latest"
            use_smart_logs = False
        elif block_start is None and block_end is not None or block_start is not None and block_end is None:
            raise ValueError("Either both blocks should be specified or neither")
        else:
            if block_end - block_start < 2000:
                use_smart_logs = False
        request = GetLogsRequest(block_start, block_end,
                                 [fcb.create_event_abi("PoolCreated", fcb.get_abi("factory_v3"))], address)
        if use_smart_logs:
            result = await self.connection.smart_send_log_request(request)
        else:
            result = await self.connection.send_request(request)
        return result

    # TODO -- TEST
    async def load_new_v2_pools_from_chain(self, block_start: int, block_end: int,
                                           factory_addresses: Optional[List[Address]] = None) -> Set[UniswapV2LP]:
        """Loads new v2 liquidity pools into a set from on-chain v2 factory data, only including pools initialized in the blocks between
        block_start and block_end."""
        if factory_addresses is None:
            factory_addresses = [UNISWAP_V2_FACTORY, SUSHISWAP_V2_FACTORY, PANCAKESWAP_V2_FACTORY, SHIBASWAP_V2_FACTORY,
                                 XCHANGE_V2_FACTORY]
        all_logs = []
        for address in factory_addresses:
            all_logs += await self.get_v2_factory_logs(address, block_start, block_end)
        return {create_v2_pool_from_factory_log(log) for log in all_logs}

    # TODO -- TEST
    async def load_new_v3_pools_from_chain(self, block_start: int, block_end: int,
                                           factory_addresses: Optional[List[Address]] = None) -> Set[UniswapV3LP]:
        """Loads new v3 liquidity pools into a set from on-chain v3 factory data, only including pools initialized in the blocks between
        block_start and block_end."""
        if factory_addresses is None:
            factory_addresses = [UNISWAP_V3_FACTORY]
        all_logs = []
        for address in factory_addresses:
            all_logs += await self.get_v3_factory_logs(address, block_start, block_end)
        return {create_v3_pool_from_factory_log(log) for log in all_logs}

    # TODO -- TEST
    async def update_v2_pools_from_chain(self, liquidity_pools: List[UniswapV2LP], block_end: Optional[int] = None):
        """Updates all v2 liquidity pools given using getReserves() method at block_end. Be careful that all liquidity pools
        are actually initialized on the blockchain at the block specified"""
        batch = []
        for lp in liquidity_pools:
            request = CallRequest(
                SmartContractTransaction(fcb.get_abi_function("getReserves", "liquidityPool"), (), lp.address, 0),
                block_end)
            batch.append(request)
        results = await self.connection.send_batch_request(batch)
        for lp, (res0, res1) in zip(liquidity_pools, results):
            lp.set_reserves(res0, res1)

    async def update_v2_pools_from_logs(self, liquidity_pools: Dict[Address, UniswapV2LP], block_start: int,
                                        block_end: int):
        """updates all the v2 liquidity pools using logs. This is the preferred method when updating already initialized liquidity pools."""
        sync_event_abi = fcb.create_event_abi("Sync", fcb.get_abi("liquidityPool"))
        sync_event_topic = fcb.create_event_topic(sync_event_abi)
        results = await self.get_v2_sync_logs(sync_event_abi, block_start=block_start, block_end=block_end)
        for log in results:
            if log.address in liquidity_pools:
                update_v2_pool_from_log(liquidity_pools[log.address], log, sync_event_topic)

    # TODO -- TEST
    async def update_v3_pools_from_chain(self, liquidity_pool_dict: Dict[Address, UniswapV3LP], block_start: int,
                                         block_end: int):
        """Updates all v3 liquidity pools given using logs from between block_start and block_end. Note this is inefficient for small numbers
                of liquidity pools as the method fetches all logs from the time period, not specific to the set content.
            WARNING: Use with care - if ANY blocks are missed between different updates the values will be incorrect. Therefore, it is recommended
            not to directly call this method and instead use a graph method."""
        all_events = ["Initialize", "Swap", "Mint", "Collect", "Flash", "Burn"]
        all_events_abi = [fcb.create_event_abi(t, fcb.get_abi("V3LiquidityPool")) for t in all_events]
        initialize_event = fcb.create_event_topic(fcb.create_event_abi("Initialize", fcb.get_abi("V3LiquidityPool")))
        swap_event = fcb.create_event_topic(fcb.create_event_abi("Swap", fcb.get_abi("V3LiquidityPool")))
        mint_event = fcb.create_event_topic(fcb.create_event_abi("Mint", fcb.get_abi("V3LiquidityPool")))
        burn_event = fcb.create_event_topic(fcb.create_event_abi("Burn", fcb.get_abi("V3LiquidityPool")))
        flash_event = fcb.create_event_topic(fcb.create_event_abi("Flash", fcb.get_abi("V3LiquidityPool")))
        collect_event = fcb.create_event_topic(fcb.create_event_abi("Collect", fcb.get_abi("V3LiquidityPool")))
        # get logs
        coros = [self.get_v3_logs(event_abi, block_start=block_start, block_end=block_end) for event_abi
                 in all_events_abi]
        all_logs = []
        results = await asyncio.gather(*coros)
        for logs in results:
            all_logs += logs
        # sort logs by block
        all_logs.sort(key=lambda log: (log.block_number, log.log_index))
        for curr_log in all_logs:
            curr_log: Log
            if curr_log.address in liquidity_pool_dict:
                try:
                    update_v3_pool_from_log(liquidity_pool_dict[curr_log.address], curr_log, swap_event, mint_event, burn_event, flash_event, collect_event, initialize_event)
                except Exception as e:
                    raise Exception(f"{e} on block {curr_log.block_number}")
