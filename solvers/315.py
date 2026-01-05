#!/usr/bin/env python3
"""Project Euler 315: Digital Root Clocks.

We compare two 7-segment display strategies while repeatedly summing digits
until a single digit (digital root process):

- Sam: Shows each intermediate value, then turns the entire panel off before
  showing the next value.
- Max: Keeps segments on when possible, only toggling segments that differ
  between consecutive displayed values.

Task
----
Feed both clocks all prime numbers p with 10^7 <= p <= 2*10^7 and compute:

    (total transitions used by Sam) - (total transitions used by Max)

A "transition" is turning one segment on or off.

This program prints the required difference.
"""

from __future__ import annotations

import argparse
import math
from typing import List, Tuple


# 7-segment digit encoding as bitmasks, where bit i means segment i is lit.
# Segment numbering scheme:
#
#  000
# 1   2
# 1   2
#  333
# 4   5
# 4   5
#  666
#
# This encoding matches the Euler problem statement's example, notably:
# digit '7' uses 4 segments.
DIGIT_MASKS: List[int] = [
    0x77,  # 0
    0x24,  # 1
    0x5D,  # 2
    0x6D,  # 3
    0x2E,  # 4
    0x6B,  # 5
    0x7B,  # 6
    0x27,  # 7
    0x7F,  # 8
    0x6F,  # 9
]


def digit_sum(n: int) -> int:
    """Return the sum of decimal digits of n (n >= 0)."""
    s = 0
    while n:
        s += n % 10
        n //= 10
    return s


def segments_of_number(n: int) -> int:
    """Return a bitmask representing all lit segments for the whole number.

    Digits are right-aligned: the least significant digit occupies the lowest byte,
    the next digit the next byte, etc. Each byte stores a 7-bit digit mask.
    """
    if n == 0:
        return DIGIT_MASKS[0]

    out = 0
    shift = 0
    while n:
        out |= DIGIT_MASKS[n % 10] << shift
        n //= 10
        shift += 8
    return out


def sam_total(n: int) -> int:
    """Total transitions for Sam's clock when fed n."""
    total = 0
    while True:
        seg = segments_of_number(n)
        total += 2 * seg.bit_count()  # on + off
        if n < 10:
            return total
        n = digit_sum(n)


def max_total(n: int) -> int:
    """Total transitions for Max's clock when fed n."""
    total = 0
    prev = 0
    while True:
        seg = segments_of_number(n)
        total += (seg ^ prev).bit_count()
        if n < 10:
            total += seg.bit_count()  # fade to black
            return total
        prev = seg
        n = digit_sum(n)


def _precompute_small(
    max_digit_sum: int = 72,
) -> Tuple[List[int], List[int], List[int]]:
    """Precompute helpers for numbers up to max_digit_sum.

    Returns:
      seg_small[v]         : segments_of_number(v)
      sam_from_blank[v]    : Sam total transitions when fed v (starting from blank)
      max_from_displayed[v]: Max transitions from state 'v is already displayed' until black
    """
    seg_small = [segments_of_number(v) for v in range(max_digit_sum + 1)]
    dsum_small = [digit_sum(v) for v in range(max_digit_sum + 1)]

    # Sam totals starting from blank.
    sam_from_blank = [-1] * (max_digit_sum + 1)

    def sam_rec(v: int) -> int:
        if sam_from_blank[v] != -1:
            return sam_from_blank[v]
        res = 2 * seg_small[v].bit_count()
        if v >= 10:
            res += sam_rec(dsum_small[v])
        sam_from_blank[v] = res
        return res

    for v in range(max_digit_sum + 1):
        sam_rec(v)

    # Max transitions assuming v is already displayed correctly.
    max_from_displayed = [-1] * (max_digit_sum + 1)

    def max_rec(v: int) -> int:
        if max_from_displayed[v] != -1:
            return max_from_displayed[v]
        if v < 10:
            res = seg_small[v].bit_count()  # just turn it off
        else:
            nxt = dsum_small[v]
            res = (seg_small[v] ^ seg_small[nxt]).bit_count() + max_rec(nxt)
        max_from_displayed[v] = res
        return res

    for v in range(max_digit_sum + 1):
        max_rec(v)

    return seg_small, sam_from_blank, max_from_displayed


def prime_sieve_odd(limit: int) -> bytearray:
    """Odd-only sieve of Eratosthenes up to 'limit' (inclusive).

    The returned bytearray 'is_prime' is indexed by i = n//2 for odd n.
    is_prime[i] == 1 means (2*i+1) is prime.

    Memory: O(limit/2).
    """
    size = limit // 2 + 1
    is_prime = bytearray(b"\x01") * size
    is_prime[0] = 0  # 1 is not prime

    max_i = (math.isqrt(limit) - 1) // 2
    for i in range(1, max_i + 1):
        if is_prime[i]:
            p = 2 * i + 1
            start = (p * p) // 2
            step = p
            count = (size - start - 1) // step + 1
            is_prime[start::step] = b"\x00" * count
    return is_prime


def solve(a: int = 10_000_000, b: int = 20_000_000) -> int:
    """Return the required transition difference for primes in [a, b]."""
    if a > b:
        a, b = b, a

    # For 8-digit numbers, max digit sum is 8*9=72.
    seg_small, sam_small, max_small_displayed = _precompute_small(72)

    is_prime = prime_sieve_odd(b)

    total_diff = 0

    # Iterate over odd primes in range.
    n = a | 1
    if n < 3:
        n = 3

    for p in range(n, b + 1, 2):
        if not is_prime[p // 2]:
            continue

        seg_p = segments_of_number(p)
        pop_p = seg_p.bit_count()
        sd = digit_sum(p)  # 1..72

        # Sam: 2*pop_p + sam_small[sd]
        # Max: pop_p + popcount(seg_p ^ seg_small[sd]) + max_small_displayed[sd]
        total_diff += (
            pop_p
            + sam_small[sd]
            - (seg_p ^ seg_small[sd]).bit_count()
            - max_small_displayed[sd]
        )

    return total_diff


def _run_tests() -> None:
    # Facts explicitly given in the problem statement.
    assert DIGIT_MASKS[1].bit_count() == 2  # digit "1" uses two segments
    assert DIGIT_MASKS[4].bit_count() == 4  # digit "4" uses four segments
    assert DIGIT_MASKS[8].bit_count() == 7  # digit "8" uses all segments
    assert DIGIT_MASKS[2].bit_count() == 5  # "To turn on a '2' will cost 5 transitions"
    assert (
        DIGIT_MASKS[7].bit_count() == 4
    )  # "...while a '7' will cost only 4 transitions"

    # Example with number 137.
    assert sam_total(137) == 40
    assert max_total(137) == 30
    assert sam_total(137) - max_total(137) == 10


def main() -> None:
    parser = argparse.ArgumentParser(description="Solve Project Euler 315")
    parser.add_argument(
        "--a", type=int, default=10_000_000, help="Range start (inclusive)"
    )
    parser.add_argument(
        "--b", type=int, default=20_000_000, help="Range end (inclusive)"
    )
    args = parser.parse_args()

    _run_tests()
    print(solve(args.a, args.b))


if __name__ == "__main__":
    main()
