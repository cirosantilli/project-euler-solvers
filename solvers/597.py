#!/usr/bin/env python3
"""
Project Euler 597 - Torpids

We compute p(n, L): the probability that the final ordering is an even permutation.

Key trick:
Let each boat i have speed V_i ~ Exp(1) (because V_i = -log(U_i), U_i uniform).
For a "target" located at coordinate t (in boat-index units), boat i's "relative speed"
to that target is W_i = V_i / (t - i).  Then W_i ~ Exp(rate = t - i).

The slowest boat relative to the current target is the one with minimal W_i.
That boat cannot bump anyone and becomes the lowest boat in the resulting order.
Conditioning on which boat is minimal allows a recursive decomposition of the race.

We only track the *parity* of the final permutation using the expected sign (+1 even, -1 odd).
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from typing import Tuple


def _round_fraction(x: Fraction, digits: int) -> str:
    """
    Round a non-negative Fraction to `digits` digits after the decimal point
    using standard half-up rounding, returning a decimal string.
    """
    assert digits >= 0
    num, den = x.numerator, x.denominator
    # Work with one extra digit for rounding
    scale = 10 ** (digits + 1)
    q, r = divmod(num * scale, den)  # floor(x * 10^(digits+1))
    last = q % 10
    q //= 10  # now q = floor(x * 10^digits)
    if last >= 5:
        q += 1
    int_part = q // (10 ** digits)
    frac_part = q % (10 ** digits)
    if digits == 0:
        return str(int_part)
    return f"{int_part}.{frac_part:0{digits}d}"


def probability_even(n: int, L: int, spacing: int = 40) -> Fraction:
    """
    Return p(n, L) exactly as a Fraction.

    Boats are 1..n (1 is lowest). Finish line is L metres upstream from boat 1's start.
    Adjacent starts are `spacing` metres apart.
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if L <= 0 or spacing <= 0:
        raise ValueError("L and spacing must be positive")
    alpha = Fraction(L, spacing)  # finish line coordinate in "gap" units
    t0 = alpha + 1  # target coordinate: distance for boat i is (t0 - i)

    @lru_cache(maxsize=None)
    def expected_sign(l: int, r: int, t: Fraction) -> Fraction:
        """
        Expected permutation sign (+1 even, -1 odd) produced by boats [l..r]
        when the current target coordinate is t (> r).
        """
        if l >= r:
            return Fraction(1, 1)  # empty or single boat -> even

        # S = sum_{j=l}^r (t - j)
        count = r - l + 1
        sum_j = (l + r) * count // 2  # arithmetic progression sum (integer)
        S = Fraction(count, 1) * t - sum_j

        total = Fraction(0, 1)
        for m in range(l, r + 1):
            pm = (t - m) / S  # probability m is the (unique) minimum
            sign_flip = -1 if ((m - l) & 1) else 1  # moving m to the front swaps (m-l) times

            left = expected_sign(l, m - 1, Fraction(m, 1))      # target becomes boat m
            right = expected_sign(m + 1, r, t)                  # target unchanged
            total += pm * sign_flip * left * right
        return total

    e = expected_sign(1, n, t0)
    return (Fraction(1, 1) + e) / 2


def solve() -> str:
    p = probability_even(13, 1800)
    return _round_fraction(p, 10)


def _self_test() -> None:
    # From the problem statement:
    assert probability_even(3, 160) == Fraction(56, 135)
    assert _round_fraction(probability_even(4, 400), 10) == "0.5107843137"


if __name__ == "__main__":
    _self_test()
    print(solve())
