import json
from collections import defaultdict
from typing import Union, Optional, Dict, Tuple, List
from UniswapTypes.ILiquidityPool import ILiquidityPool
from UniswapTypes.RToken import RToken
from Web3Types.SimpleTypes import Address
import Utilities.EthereumMaths as em


class UninitialisedBitmapError(Exception):
    pass


class UninitialisedSlotError(Exception):
    pass


class UninitialisedMutableError(Exception):
    pass


class NoLiquidity(Exception):
    pass


def calculate_virtual_reserves(liquidity, sqrtPriceX96):
    y_reserves = (sqrtPriceX96 * liquidity) >> 96
    x_reserves = (liquidity << 96) // sqrtPriceX96
    return x_reserves, y_reserves


class UniswapV3LP(ILiquidityPool):
    """Class representing an Uniswap V3 liquidity pool. Note mutable variables should only be interacted with by using the
    set mutable variable's method. Also note that while pretty accurate, attributes reserves0 and reserves1 can get slightly
    out after repeated updates - need to fix - probably impossible though"""

    __slots__ = ("current_tick", "slots_dict", "slot_bitmap", "reserves0", "reserves1", "sqrtPriceX96", "liquidity",
                 "tick_spacing", "fee")

    def __init__(self, address: Union[str, Address], token0: RToken, token1: RToken,
                 tick_spacing: int, fee: int,
                 current_tick: Optional[int] = None,
                 liquidity: Optional[int] = None,
                 sqrtPriceX96: Optional[int] = None,
                 reserves0: Optional[int] = None,
                 reserves1: Optional[int] = None,
                 initial_slots: Optional[Dict[int, Tuple[int, int]]] = None,
                 slot_bitmap: Optional[Dict[int, int]] = None):
        super().__init__(address, token0, token1)
        self.current_tick: Optional[int] = current_tick
        self.tick_spacing: int = tick_spacing
        self.fee: int = fee
        self.liquidity: Optional[int] = liquidity
        self.sqrtPriceX96: Optional[int] = sqrtPriceX96
        self.reserves0: Optional[int] = reserves0
        self.reserves1: Optional[int] = reserves1
        if initial_slots is None:
            self.slots_dict: Dict[int, Tuple[int, int]] = {}
        else:
            self.slots_dict: Dict[int, (int, int)] = initial_slots.copy()
        if slot_bitmap is None:
            self.slot_bitmap: Dict[int, int] = {}
        else:
            self.slot_bitmap: Dict[int, int] = slot_bitmap.copy()

    def __str__(self):
        return str(self.address)

    def __eq__(self, other):
        return self.address == other.address

    def __hash__(self):
        return hash(self.address)

    def deep_eq(self, other):
        return (self.address == other.address and
                self.token0 == other.token0 and
                self.token1 == other.token1 and
                self.current_tick == other.current_tick and
                self.tick_spacing == other.tick_spacing and
                self.fee == other.fee and
                self.liquidity == other.liquidity and
                self.sqrtPriceX96 == other.sqrtPriceX96 and
                self.reserves0 == other.reserves0 and
                self.reserves1 == other.reserves1)

    def set_mutable_values(self, current_tick: int, liquidity: int, sqrtPriceX96: int, reserves0: int, reserves1: int):
        self.current_tick = current_tick
        self.liquidity = liquidity
        self.sqrtPriceX96 = sqrtPriceX96
        self.reserves0 = reserves0
        self.reserves1 = reserves1

    def check_mutable_init(self) -> bool:
        return type(self.current_tick) == int and type(self.liquidity) == int and type(
            self.sqrtPriceX96) == int and type(self.reserves0) == int and type(self.reserves1) == int

    def set_slot_value(self, slot_num: int, net_liquidity: int, gross_liquidity: int):
        self.slots_dict[slot_num] = (net_liquidity, gross_liquidity)

    def set_bitmap_value(self, bitmap_num: int, bitmap_value: int):
        self.slot_bitmap[bitmap_num] = bitmap_value

    def get_current_tick(self) -> int:
        return self.current_tick

    def get_reserves(self) -> Tuple[int, int]:
        return self.reserves0, self.reserves1

    def get_liquidity(self) -> int:
        return self.liquidity

    # TODO TEST
    def get_tick(self, tick_value: int) -> Tuple[int, int]:
        bitmap_tick_key = (tick_value // self.tick_spacing) // 256
        bitmap_tick_index = (tick_value // self.tick_spacing) % 256
        try:
            bitmap = self.slot_bitmap[bitmap_tick_key]
        except KeyError:
            raise UninitialisedBitmapError(f"Attempted to get an uninitialised bitmap for lp {self.address}")
        initialized = (pow(2, bitmap_tick_index) & bitmap)
        if initialized == 0:
            return 0, 0
        else:
            try:
                tick = self.slots_dict[tick_value]
            except KeyError:
                raise UninitialisedSlotError("Attempted to get an uninitialised slot")
            return tick

    # TODO TEST
    def toggle_bitmap_tick(self, tick_value: int):
        bitmap_tick_key = (tick_value // self.tick_spacing) // 256
        bitmap_tick_index = (tick_value // self.tick_spacing) % 256
        try:
            bitmap = self.slot_bitmap[bitmap_tick_key]
        except KeyError:
            raise UninitialisedBitmapError(f"Attempted to get an uninitialised bitmap for lp {self.address}")
        self.slot_bitmap[bitmap_tick_key] = bitmap ^ (1 << bitmap_tick_index)

    # TODO TEST
    def get_price(self) -> float:
        """gets the current pool price from the sqrtX96 representation - loses precision due to float conversion"""
        return self.sqrtPriceX96 ** 2 / 2 ** 192

    # TODO TEST
    def get_virtual_reserves(self) -> Tuple[int, int]:
        """Gets the current virtual reserves in the tick range"""
        # Remember that sqrt(P) is X96 format. sqrtPX96 = sqrtP * 2**96
        y_reserves = (self.sqrtPriceX96 * self.liquidity) >> 96
        x_reserves = (self.liquidity << 96) // self.sqrtPriceX96
        return x_reserves, y_reserves

    # TODO TEST
    def get_next_tick(self, current_tick: int, spacing: int, direction: bool) -> int:
        """gets the next initialised tick from the current tick in the direction given by 'direction' - True = Right,
        False = Left"""
        min_tick_to_use = min(self.slots_dict.keys())
        max_tick_to_use = max(self.slots_dict.keys())
        if current_tick >= max_tick_to_use:
            raise UninitialisedSlotError("No tick above current_tick exists in this liquidity pool!")
        if current_tick <= min_tick_to_use:
            raise UninitialisedSlotError("No tick below current_tick exists in this liquidity pool!")
        bitmap_tick_key = (current_tick // spacing) // 256
        bitmap_tick_index = (current_tick // spacing) % 256
        if direction:
            bitmap_tick_index += 1
        else:
            bitmap_tick_index -= 1
        while True:
            if bitmap_tick_key not in self.slot_bitmap:
                raise UninitialisedBitmapError(f"Attempted to get an uninitialised bitmap for lp {self.address}")
            else:
                current_bitmap = self.slot_bitmap[bitmap_tick_key]
            t = (1 << bitmap_tick_index) & current_bitmap
            while (t == 0 and bitmap_tick_index > 0 and not direction) or (
                    t == 0 and bitmap_tick_index < 255 and direction):
                if direction:
                    bitmap_tick_index += 1
                else:
                    bitmap_tick_index -= 1
                t = (1 << bitmap_tick_index) & current_bitmap
            if t != 0:
                return (bitmap_tick_index * spacing) + (bitmap_tick_key * spacing * 256)
            else:
                if direction:
                    bitmap_tick_index = 0
                    bitmap_tick_key += 1
                else:
                    bitmap_tick_index = 255
                    bitmap_tick_key -= 1

    # -- TODO Test
    def get_virtual_reserves_with_bounds(self, direction: bool, max_input: int) -> List[Tuple[int, Tuple[int, int]]]:
        """from the current price, gets a list of tuples with first element being the lower bound input amount needed to get
         to that tick, and the second element being the virtual reserves between the lower bound and the next bound in the list
         (or the max input if last element in the list). The direction parameter specifies whether we are swapping token0
         for token1 (True) or token1 for token0 (False)"""
        price_at_current_tick = self.sqrtPriceX96
        current_slot = self.current_tick
        current_change = 0
        out_list = []
        current_liquidity = self.liquidity
        direction = not direction

        while current_change < max_input:
            next_tick = self.get_next_tick(current_slot, self.tick_spacing, direction)
            price_at_next_tick = em.getSqrtRatioAtTick(next_tick)
            # Maybe roundup is required for this part
            if direction:
                amount_one_delta = em.getAmount1Delta(price_at_current_tick, price_at_next_tick, current_liquidity, True)
                amount_one_delta_with_fee = (amount_one_delta * 1000000) // (1000000 - self.fee)
                res0, res1 = calculate_virtual_reserves(current_liquidity, price_at_current_tick)
                out_list.append((current_change, (res1, res0)))
                current_change += amount_one_delta_with_fee
                price_at_current_tick = price_at_next_tick
                # change liquidity
                current_liquidity += self.get_tick(next_tick)[0]
                current_slot = next_tick

            else:
                amount_zero_delta = em.getAmount0Delta(price_at_next_tick, price_at_current_tick, current_liquidity, True)
                amount_zero_delta_with_fee = (amount_zero_delta * 1000000) // (1000000 - self.fee)
                out_list.append((current_change, calculate_virtual_reserves(current_liquidity, price_at_current_tick)))
                current_change += amount_zero_delta_with_fee
                price_at_current_tick = price_at_next_tick
                # change liquidity
                current_liquidity -= self.get_tick(next_tick)[0]
                current_slot = next_tick
        return out_list

    def swap(self, token0_in: int, token1_in: int) -> int:
        pass

    def simulate_swap(self, token0_in: int, token1_in: int) -> int:
        # first get price at next tick
        if token0_in == 0 and token1_in == 0:
            return 0
        if token0_in <= 0 and token1_in <= 0:
            raise NotImplementedError("Only supports positive swaps!")
        direction = token1_in > 0
        amount_remaining = token1_in if direction else token0_in
        current_tick = self.current_tick
        current_price = self.sqrtPriceX96
        current_liquidity = self.liquidity
        if current_liquidity == 0:
            raise NoLiquidity("Zero liquidity available for the swap")
        total_out = 0
        skip = False
        while amount_remaining > 0:
            try:
                tick_above = self.get_next_tick(current_tick, self.tick_spacing, direction)
            except UninitialisedSlotError:
                tick_above = 887272 if direction else -887272
                skip = True
            price_above = em.getSqrtRatioAtTick(tick_above)
            amount_in, amount_out, new_price, fee = em.computeSwapStep(current_price, price_above, current_liquidity, amount_remaining, self.fee)
            amount_remaining -= (amount_in + fee)
            total_out += amount_out
            if skip:
                break
            current_tick = tick_above
            current_price = new_price
            current_liquidity = current_liquidity + self.slots_dict[tick_above][0] if direction else current_liquidity - self.slots_dict[tick_above][0]
        return total_out

    def simulate_swap_price(self, token0_in: int, token1_in: int) -> int:
        if token0_in == 0 and token1_in == 0:
            return 0
        if token0_in <= 0 and token1_in <= 0:
            raise NotImplementedError("Only supports positive swaps!")
        direction = token1_in > 0
        amount_remaining = token1_in if direction else token0_in
        current_tick = self.current_tick
        current_price = self.sqrtPriceX96
        current_liquidity = self.liquidity
        new_price = current_price
        skip = False
        while amount_remaining > 0:
            try:
                tick_above = self.get_next_tick(current_tick, self.tick_spacing, direction)
            except UninitialisedSlotError:
                tick_above = 887272 if direction else -887272
                skip = True
            price_above = em.getSqrtRatioAtTick(tick_above)
            amount_in, amount_out, new_price, fee = em.computeSwapStep(current_price, price_above, current_liquidity, amount_remaining, self.fee)
            amount_remaining -= (amount_in + fee)
            if skip:
                break
            current_tick = tick_above
            current_price = new_price
            current_liquidity = current_liquidity + self.slots_dict[tick_above][0] if direction else current_liquidity - self.slots_dict[tick_above][0]
        return current_price

    def initialize_event(self, sqrtPriceX96: int, tick: int):
        """Update the liquidity pool based on an initialize event. Note that this initializes the bitmap to a default dict so no errors
        will be thrown when entering an uninitialized bitmap. Therefore, this pool should be carefully updated."""
        self.sqrtPriceX96 = sqrtPriceX96
        self.current_tick = tick
        self.reserves0 = 0
        self.reserves1 = 0
        self.liquidity = 0
        self.slot_bitmap = defaultdict(int)

    def mint_event(self, tick_lower: int, tick_upper: int, liquidity: int, amount0: int, amount1: int):
        """Update the liquidity pool based on a mint event"""
        if not self.check_mutable_init():
            raise UninitialisedMutableError("Mutable variables are not set for mint event")
        self.reserves0 += amount0
        self.reserves1 += amount1
        tick_lower_values = self.get_tick(tick_lower)
        tick_upper_values = self.get_tick(tick_upper)
        if tick_upper > self.current_tick >= tick_lower:
            self.liquidity += liquidity
        if tick_lower_values[1] == 0:
            self.slots_dict[tick_lower] = (liquidity, liquidity)
            self.toggle_bitmap_tick(tick_lower)
        else:
            self.slots_dict[tick_lower] = (tick_lower_values[0] + liquidity, tick_lower_values[1] + liquidity)
        if tick_upper_values[1] == 0:
            self.slots_dict[tick_upper] = (-liquidity, liquidity)
            self.toggle_bitmap_tick(tick_upper)
        else:
            self.slots_dict[tick_upper] = (tick_upper_values[0] - liquidity, tick_upper_values[1] + liquidity)

    def burn_event(self, tick_lower: int, tick_upper: int, liquidity: int, amount0: int, amount1: int):
        """Update the liquidity pool based on a burn event"""
        if not self.check_mutable_init():
            raise UninitialisedMutableError("Mutable variables are not set for mint event")
        # self.reserves0 -= amount0
        # self.reserves1 -= amount1
        tick_lower_values = self.get_tick(tick_lower)
        tick_upper_values = self.get_tick(tick_upper)
        if tick_upper > self.current_tick >= tick_lower:
            self.liquidity -= liquidity
        if tick_lower_values[1] == 0 or tick_upper_values[1] == 0:
            raise UninitialisedSlotError("Attempted to burn an uninitialised tick")
        if tick_lower_values[1] - liquidity == 0:
            self.slots_dict.pop(tick_lower)
            self.toggle_bitmap_tick(tick_lower)
        else:
            self.slots_dict[tick_lower] = (tick_lower_values[0] - liquidity, tick_lower_values[1] - liquidity)
        if tick_upper_values[1] - liquidity == 0:
            self.slots_dict.pop(tick_upper)
            self.toggle_bitmap_tick(tick_upper)
        else:
            self.slots_dict[tick_upper] = (tick_upper_values[0] + liquidity, tick_upper_values[1] - liquidity)

    def swap_event(self, amount0: int, amount1: int, sqrtPriceX96: int, liquidity: int, tick: int):
        """Update the liquidity pool based on a swap event"""
        self.reserves0 += amount0
        self.reserves1 += amount1
        self.sqrtPriceX96 = sqrtPriceX96
        self.liquidity = liquidity
        self.current_tick = tick

    def flash_event(self, paid0: int, paid1: int):
        self.reserves0 += paid0
        self.reserves1 += paid1

    def collect_event(self, reserves0: int, reserves1: int):
        self.reserves0 -= reserves0
        self.reserves1 -= reserves1

    def to_json(self) -> str:
        return json.dumps({
            "address": str(self.address),
            "token0": str(self.token0),
            "token1": str(self.token1),
            "current_tick": self.current_tick,
            "sqrtPriceX96": self.sqrtPriceX96,
            "liquidity": self.liquidity,
            "reserves0": self.reserves0,
            "reserves1": self.reserves1,
            "slot_bitmap": self.slot_bitmap,
            "slots_dict": self.slots_dict,
            "fee": self.fee,
            "tick_spacing": self.tick_spacing,
            "type": "UniswapV3LP"
        })


def v3_from_json(json_str: str) -> UniswapV3LP:
    jd = json.loads(json_str)
    slot_bitmap = jd["slot_bitmap"]
    slot_bitmap = {int(k): v for k, v in slot_bitmap.items()}
    slots_dict = jd["slots_dict"]
    slots_dict = {int(k): tuple(v) for k, v in slots_dict.items()}
    slot_bitmap = defaultdict(int, slot_bitmap)
    return UniswapV3LP(Address(jd["address"]),
                       RToken(jd["token0"]),
                       RToken(jd["token1"]),
                       jd["tick_spacing"],
                       jd["fee"],
                       jd["current_tick"],
                       jd["liquidity"],
                       jd["sqrtPriceX96"],
                       jd["reserves0"],
                       jd["reserves1"],
                       slots_dict,
                       slot_bitmap)

