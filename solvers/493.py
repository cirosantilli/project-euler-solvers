#!/usr/bin/env python3
"""
Project Euler 493: Under the Rainbow

There are 70 balls in an urn: 7 colors, 10 balls of each color.
20 balls are drawn at random without replacement.

Compute the expected number of distinct colors among the 20 drawn balls.
Print the answer rounded to 9 digits after the decimal point.
"""

from __future__ import annotations

import math
from decimal import Decimal, getcontext, ROUND_HALF_UP


def comb(n: int, k: int) -> int:
    """Compute n choose k as an exact integer (no factorials)."""
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    if k == 0:
        return 1

    num = 1
    den = 1
    # Multiply/divide progressively and reduce by gcd to keep numbers small.
    for i in range(1, k + 1):
        num *= n - k + i
        den *= i
        g = math.gcd(num, den)
        num //= g
        den //= g
    # den should be 1 here, but keep it robust.
    return num // den


def expected_distinct_colors(
    colors: int = 7, per_color: int = 10, draws: int = 20
) -> Decimal:
    """
    Expected #distinct colors in `draws` draws from `colors` groups of size `per_color`.

    By linearity of expectation:
      E[#colors] = sum_c P(color c appears) = colors * (1 - P(color c absent))
    For a fixed color, "absent" means all draws come from the other balls:
      P(absent) = C(total - per_color, draws) / C(total, draws)
    """
    total = colors * per_color
    if not (0 <= draws <= total):
        raise ValueError("draws must be between 0 and total balls")

    # High precision for safe rounding.
    getcontext().prec = 60

    absent_num = comb(total - per_color, draws)
    absent_den = comb(total, draws)

    p_absent = Decimal(absent_num) / Decimal(absent_den)
    return Decimal(colors) * (Decimal(1) - p_absent)


def solve() -> str:
    ans = expected_distinct_colors()

    # Round to 9 digits after decimal (as required by the problem).
    rounded = ans.quantize(Decimal("0.000000001"), rounding=ROUND_HALF_UP)
    return f"{rounded:.9f}"


def _self_test() -> None:
    # Basic combinatorial sanity checks (problem statement provides no explicit sample I/O).
    assert comb(5, 0) == 1
    assert comb(5, 5) == 1
    assert comb(5, 2) == 10
    assert comb(10, 3) == 120
    assert comb(70, 20) > 0
    assert expected_distinct_colors() > 0


if __name__ == "__main__":
    _self_test()
    print(solve())
