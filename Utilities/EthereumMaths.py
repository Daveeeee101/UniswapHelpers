from typing import Tuple

max_256_bits = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff


class MathError(Exception):
    pass


def getSqrtRatioAtTick(tick: int) -> int:
    absTick = abs(tick)
    ratio = 0xfffcb933bd6fad37aa2d162d1a594001 if absTick & 0x1 != 0 else 0x100000000000000000000000000000000
    if absTick & 0x2 != 0:
        ratio = (ratio * 0xfff97272373d413259a46990580e213a) >> 128
    if absTick & 0x4 != 0:
        ratio = (ratio * 0xfff2e50f5f656932ef12357cf3c7fdcc) >> 128
    if absTick & 0x8 != 0:
        ratio = (ratio * 0xffe5caca7e10e4e61c3624eaa0941cd0) >> 128
    if absTick & 0x10 != 0:
        ratio = (ratio * 0xffcb9843d60f6159c9db58835c926644) >> 128
    if absTick & 0x20 != 0:
        ratio = (ratio * 0xff973b41fa98c081472e6896dfb254c0) >> 128
    if absTick & 0x40 != 0:
        ratio = (ratio * 0xff2ea16466c96a3843ec78b326b52861) >> 128
    if absTick & 0x80 != 0:
        ratio = (ratio * 0xfe5dee046a99a2a811c461f1969c3053) >> 128
    if absTick & 0x100 != 0:
        ratio = (ratio * 0xfcbe86c7900a88aedcffc83b479aa3a4) >> 128
    if absTick & 0x200 != 0:
        ratio = (ratio * 0xf987a7253ac413176f2b074cf7815e54) >> 128
    if absTick & 0x400 != 0:
        ratio = (ratio * 0xf3392b0822b70005940c7a398e4b70f3) >> 128
    if absTick & 0x800 != 0:
        ratio = (ratio * 0xe7159475a2c29b7443b29c7fa6e889d9) >> 128
    if absTick & 0x1000 != 0:
        ratio = (ratio * 0xd097f3bdfd2022b8845ad8f792aa5825) >> 128
    if absTick & 0x2000 != 0:
        ratio = (ratio * 0xa9f746462d870fdf8a65dc1f90e061e5) >> 128
    if absTick & 0x4000 != 0:
        ratio = (ratio * 0x70d869a156d2a1b890bb3df62baf32f7) >> 128
    if absTick & 0x8000 != 0:
        ratio = (ratio * 0x31be135f97d08fd981231505542fcfa6) >> 128
    if absTick & 0x10000 != 0:
        ratio = (ratio * 0x9aa508b5b7a84e1c677de54f3e99bc9) >> 128
    if absTick & 0x20000 != 0:
        ratio = (ratio * 0x5d6af8dedb81196699c329225ee604) >> 128
    if absTick & 0x40000 != 0:
        ratio = (ratio * 0x2216e584f5fa1ea926041bedfe98) >> 128
    if absTick & 0x80000 != 0:
        ratio = (ratio * 0x48a170391f7dc42444e8fa2) >> 128

    if tick > 0:
        ratio = max_256_bits // ratio

    sqrtPriceX96 = (ratio >> 32) + (0 if ratio % (1 << 32) == 0 else 1)

    return sqrtPriceX96


def div_round_up(num1: int, num2: int):
    res = num1 // num2
    return res + 1 if num1 % num2 != 0 else res


# --TODO TEST
def getAmount0Delta(sqrtRatioAX96: int, sqrtRatioBX96: int, liquidity: int, roundup: bool) -> int:
    if sqrtRatioAX96 > sqrtRatioBX96:
        sqrtRatioAX96, sqrtRatioBX96 = (sqrtRatioBX96, sqrtRatioAX96)
    numerator1 = liquidity << 96
    numerator2 = sqrtRatioBX96 - sqrtRatioAX96
    if sqrtRatioAX96 <= 0:
        raise MathError()
    if roundup:
        r1 = (numerator1 * numerator2)
        r2 = r1 // sqrtRatioBX96
        r2 = r2 + 1 if r1 % sqrtRatioBX96 != 0 else r2
        r3 = r2 // sqrtRatioAX96
        r3 = r3 + 1 if r2 % sqrtRatioAX96 != 0 else r3
        return r3
    else:
        return ((numerator1 * numerator2) // sqrtRatioBX96) // sqrtRatioAX96


# --TODO TEST
def getAmount1Delta(sqrtRatioAX96: int, sqrtRatioBX96: int, liquidity: int, roundup: bool) -> int:
    if sqrtRatioAX96 > sqrtRatioBX96:
        sqrtRatioAX96, sqrtRatioBX96 = (sqrtRatioBX96, sqrtRatioAX96)
    if roundup:
        r1 = (liquidity * (sqrtRatioBX96 - sqrtRatioAX96))
        r2 = r1 // 0x1000000000000000000000000
        r2 = r2 + 1 if r1 % 0x1000000000000000000000000 != 0 else r2
        return r2
    else:
        return (liquidity * (sqrtRatioBX96 - sqrtRatioAX96)) // 0x1000000000000000000000000


def getNextSqrtPriceFromAmount0RoundingUp(sqrtPX96: int, liquidity: int, amount: int, add: bool) -> int:
    # we short circuit amount == 0 because the result is otherwise not guaranteed to equal the input price
    if amount == 0:
        return sqrtPX96
    numerator1 = liquidity << 96
    if add:
        product = amount * sqrtPX96
        if (product // amount) == sqrtPX96:
            denominator = numerator1 + product
            if denominator >= numerator1:
                res_num = numerator1 * sqrtPX96
                res_den = denominator
                res = res_num // res_den
                res = res + 1 if res_num % res_den != 0 else res
                return res
        res_num = numerator1
        res_den = (numerator1 // sqrtPX96) + amount
        res = res_num // res_den
        res = res + 1 if res_num % res_den != 0 else res
        return res
    else:
        product = amount * sqrtPX96
        denominator = numerator1 - product
        res_num = numerator1 * sqrtPX96
        res_den = denominator
        res = res_num // res_den
        res = res + 1 if res_num % res_den != 0 else res
        return res


def getNextSqrtPriceFromAmount1RoundingDown(sqrtPX96: int, liquidity: int, amount: int, add: bool) -> int:
    # if we're adding (subtracting), rounding down requires rounding the quotient down (up)
    # in both cases, avoid a mulDiv for most inputs
    if add:
        quotient = (amount << 96) // liquidity
        return sqrtPX96 + quotient
    else:
        numerator = amount << 96
        denominator = liquidity
        res = numerator // denominator
        quotient = res + 1 if numerator % denominator != 0 else res
        return sqrtPX96 - quotient


def getNextSqrtPriceFromInput(currentPrice: int, liquidity: int, amount_in: int, direction: bool) -> int:
    return getNextSqrtPriceFromAmount0RoundingUp(currentPrice, liquidity, amount_in, True) \
        if direction else getNextSqrtPriceFromAmount1RoundingDown(currentPrice, liquidity, amount_in, True)


def computeSwapStep(sqrtRatioCurrentX96: int, sqrtRatioTargetX96: int, liquidity: int, amountRemaining: int,
                    feePips: int) -> Tuple[int, int, int, int]:
    zeroForOne = sqrtRatioCurrentX96 >= sqrtRatioTargetX96
    amountRemainingLessFee = (amountRemaining * (1000000 - feePips)) // 1000000
    amountIn = getAmount0Delta(sqrtRatioTargetX96, sqrtRatioCurrentX96, liquidity, True) if zeroForOne else \
        getAmount1Delta(sqrtRatioCurrentX96, sqrtRatioTargetX96, liquidity, True)
    if amountRemainingLessFee >= amountIn:
        sqrtRatioNextX96 = sqrtRatioTargetX96
    else:
        sqrtRatioNextX96 = getNextSqrtPriceFromInput(
            sqrtRatioCurrentX96,
            liquidity,
            amountRemainingLessFee,
            zeroForOne)
    amount_in = amountIn
    if zeroForOne:
        amount_out = getAmount1Delta(sqrtRatioNextX96, sqrtRatioCurrentX96, liquidity, False)
        if sqrtRatioNextX96 != sqrtRatioTargetX96:
            amount_in = getAmount0Delta(sqrtRatioNextX96, sqrtRatioCurrentX96, liquidity, True)
    else:
        amount_out = getAmount0Delta(sqrtRatioCurrentX96, sqrtRatioNextX96, liquidity, False)
        if sqrtRatioNextX96 != sqrtRatioTargetX96:
            amount_in = getAmount1Delta(sqrtRatioCurrentX96, sqrtRatioNextX96, liquidity, True)
    if sqrtRatioNextX96 != sqrtRatioTargetX96:
        feeAmount = amountRemaining - amount_in
    else:
        feeAmount = div_round_up((amount_in * feePips), 1000000 - feePips)
    return amount_in, amount_out, sqrtRatioNextX96, feeAmount
