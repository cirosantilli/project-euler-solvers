#!/usr/bin/env python3
"""
Project Euler 389 - Platonic Dice

Compute Var(I) where:
T = roll 1d4
C = sum of T rolls of 1d6
O = sum of C rolls of 1d8
D = sum of O rolls of 1d12
I = sum of D rolls of 1d20

The program prints the variance of I rounded to 4 decimal places.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, Tuple


def die_moments(sides: int) -> Tuple[Fraction, Fraction]:
    """Return (mean, variance) for a fair die with faces 1..sides."""
    if sides <= 0:
        raise ValueError("sides must be positive")
    mean = Fraction(sides + 1, 2)
    var = Fraction(sides * sides - 1, 12)
    return mean, var


def compound_sum_moments(
    n_mean: Fraction, n_var: Fraction, die_sides: int
) -> Tuple[Fraction, Fraction]:
    """
    If X = sum_{k=1..N} Y_k, where Y_k are iid fair die(1..die_sides),
    independent of N, and (E[N], Var(N)) = (n_mean, n_var), then return
    (E[X], Var(X)).
    """
    y_mean, y_var = die_moments(die_sides)
    mean = n_mean * y_mean
    var = n_mean * y_var + n_var * (y_mean * y_mean)
    return mean, var


def _distribution_sum_of_n_dice(n: int, sides: int) -> Dict[int, Fraction]:
    """Exact pmf for the sum of n iid fair dice(1..sides). For small n in tests."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return {0: Fraction(1, 1)}
    pmf: Dict[int, Fraction] = {0: Fraction(1, 1)}
    face_p = Fraction(1, sides)
    for _ in range(n):
        nxt: Dict[int, Fraction] = {}
        for total, p in pmf.items():
            for face in range(1, sides + 1):
                nxt[total + face] = nxt.get(total + face, Fraction(0, 1)) + p * face_p
        pmf = nxt
    return pmf


def _compound_distribution(n_sides: int, die_sides: int) -> Dict[int, Fraction]:
    """Exact pmf for: N ~ die(1..n_sides), then sum of N dice(1..die_sides)."""
    pmf: Dict[int, Fraction] = {}
    p_n = Fraction(1, n_sides)
    for n in range(1, n_sides + 1):
        pmf_sum = _distribution_sum_of_n_dice(n, die_sides)
        for total, p in pmf_sum.items():
            pmf[total] = pmf.get(total, Fraction(0, 1)) + p_n * p
    return pmf


def _moments_from_pmf(pmf: Dict[int, Fraction]) -> Tuple[Fraction, Fraction]:
    """Return (mean, variance) from an exact pmf."""
    mean = sum(Fraction(x, 1) * p for x, p in pmf.items())
    second = sum(Fraction(x * x, 1) * p for x, p in pmf.items())
    var = second - mean * mean
    return mean, var


def format_fraction_fixed(x: Fraction, decimals: int = 4) -> str:
    """Round x to `decimals` places using half-up rounding, returning a fixed-point string."""
    if decimals < 0:
        raise ValueError("decimals must be non-negative")
    scale = 10**decimals
    scaled_num = x.numerator * scale
    den = x.denominator
    q, r = divmod(scaled_num, den)
    # half-up rounding
    if 2 * r >= den:
        q += 1
    int_part = q // scale
    frac_part = q % scale
    if decimals == 0:
        return str(int_part)
    return f"{int_part}.{frac_part:0{decimals}d}"


def solve() -> str:
    # Sanity checks on die moments (not from the problem statement; they validate formulas).
    m6, v6 = die_moments(6)
    assert m6 == Fraction(7, 2)
    assert v6 == Fraction(35, 12)

    # Cross-check the compound-sum variance law against a brute-force distribution (small case).
    # N ~ 1d2, Y ~ 1d2, X = sum_{k=1..N} Y_k
    n_mean, n_var = die_moments(2)
    x_mean, x_var = compound_sum_moments(n_mean, n_var, 2)
    pmf = _compound_distribution(2, 2)
    bf_mean, bf_var = _moments_from_pmf(pmf)
    assert x_mean == bf_mean and x_var == bf_var

    # Problem chain: 1d4 -> Nd6 -> Nd8 -> Nd12 -> Nd20
    mean, var = die_moments(4)  # T
    for sides in (6, 8, 12, 20):
        mean, var = compound_sum_moments(mean, var, sides)

    return format_fraction_fixed(var, 4)


if __name__ == "__main__":
    print(solve())
