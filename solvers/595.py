#!/usr/bin/env python3
"""
Project Euler 595 - Incremental Random Sort

Compute S(52) rounded to 8 decimal places.

No external libraries are used (only Python standard library).
"""

from fractions import Fraction
from decimal import Decimal, getcontext, ROUND_HALF_UP


def _build_factorials(n: int) -> list[int]:
    fact = [1] * (n + 1)
    for i in range(2, n + 1):
        fact[i] = fact[i - 1] * i
    return fact


def _comb(n: int, k: int, fact: list[int]) -> int:
    if k < 0 or k > n:
        return 0
    if k > n - k:
        k = n - k
    return fact[n] // (fact[k] * fact[n - k])


def _succession_counts_upto(n: int, fact: list[int]) -> list[list[int]]:
    """
    a[m][r] = number of permutations of {1..m} with exactly r 'successions',
    i.e. occurrences of i immediately followed by i+1.
    """
    a: list[list[int]] = [[] for _ in range(n + 1)]
    a[1] = [1]
    for m in range(2, n + 1):
        row = [0] * m  # r = 0..m-1
        for r in range(0, m):
            # Inclusion–exclusion, using the fact that requiring any k particular successions
            # glues elements into m-k blocks -> (m-k)! permutations.
            c1 = _comb(m - 1, r, fact)
            s = 0
            # j counts additional forced successions beyond the r that will remain "exactly"
            for j in range(0, m - r):
                k = m - r - j  # factorial argument
                term = _comb(m - 1 - r, j, fact) * fact[k]
                if j & 1:
                    s -= term
                else:
                    s += term
            row[r] = c1 * s
        a[m] = row
    return a


def expected_shuffles(n: int) -> Fraction:
    """
    Return S(n) exactly as a Fraction.
    """
    if n <= 1:
        return Fraction(0, 1)

    fact = _build_factorials(n)
    a = _succession_counts_upto(n, fact)

    # T[m] = expected shuffles to finish starting from a "fixed" state with m blocks.
    T = [Fraction(0, 1)] * (n + 1)
    T[1] = Fraction(0, 1)

    for m in range(2, n + 1):
        denom = fact[m] - a[m][0]  # 1 - P(no successions) scaled by m!
        num = Fraction(fact[m], 1)  # the "+1" shuffle, scaled by m!
        for r in range(1, m):
            # after shuffle, r successions => m-r blocks
            num += Fraction(a[m][r], 1) * T[m - r]
        T[m] = num / denom

    # Initial permutation is uniform on n!, then immediately "fixed" into n-r blocks.
    Sn = Fraction(0, 1)
    for r in range(0, n):
        Sn += Fraction(a[n][r], fact[n]) * T[n - r]
    return Sn


def solve() -> str:
    # Problem statement test values
    assert expected_shuffles(1) == 0
    assert expected_shuffles(2) == 1
    assert expected_shuffles(5) == Fraction(4213, 871)

    # Compute S(52) and round to 8 decimal places
    Sn = expected_shuffles(52)
    getcontext().prec = 80
    d = Decimal(Sn.numerator) / Decimal(Sn.denominator)
    ans = d.quantize(Decimal("0.00000001"), rounding=ROUND_HALF_UP)
    return format(ans, "f")


if __name__ == "__main__":
    print(solve())
