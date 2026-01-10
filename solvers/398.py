#!/usr/bin/env python3
"""
Project Euler 398 - Cutting Rope

We choose m-1 cut points uniformly among the n-1 integer points inside a rope of length n.
This is equivalent to choosing a uniformly random ordered composition of n into m positive
integers (segment lengths).

Let Y be the length of the second-shortest segment (ties allowed: if multiple shortest
segments exist, Y equals that shortest length).

We compute E(n,m) = E[Y] via the tail-sum formula:
    E[Y] = sum_{k>=1} P(Y >= k)

For integers, Y >= k  <=>  at most one segment has length < k.
That event can be counted with stars-and-bars / binomial coefficients and simplified
using a hockey-stick identity.

For the large target (n=10^7, m=100) we avoid huge integers by evaluating binomial
*ratios* using products of small fractions.
"""

from __future__ import annotations

from fractions import Fraction
from math import comb


def _count_y2_ge_k_exact(n: int, m: int, k: int) -> int:
    """
    Exact count of ordered compositions of n into m positive parts where
    the second-shortest part is >= k.
    """
    r = m - 1  # binomial parameter
    # Derived parameters:
    # N2 = n - (m-1)k + (m-2)
    # N1 = n - mk + (m-1)
    N2 = n - (m - 1) * k + (m - 2)
    N1 = n - m * k + (m - 1)

    c2 = comb(N2, r) if N2 >= r else 0
    c1 = comb(N1, r) if N1 >= r else 0
    return m * c2 - (m - 1) * c1


def expected_second_shortest_exact(n: int, m: int) -> Fraction:
    """
    Exact E(n,m) as a Fraction. Intended for small test cases only.
    """
    if not (1 <= m <= n):
        raise ValueError("Require 1 <= m <= n")
    if m == 1:
        return Fraction(n, 1)

    r = m - 1
    total = comb(n - 1, r)
    kmax = (n - 1) // (m - 1)

    acc = Fraction(0, 1)
    for k in range(1, kmax + 1):
        cnt = _count_y2_ge_k_exact(n, m, k)
        if cnt == 0:
            break
        acc += Fraction(cnt, total)
    return acc


def _binom_ratio(top_n: int, bot_n: int, r: int) -> float:
    """
    Return C(top_n, r) / C(bot_n, r) as a float using a stable product:
        Π_{i=0..r-1} (top_n - i) / (bot_n - i)

    Assumes bot_n >= r.
    """
    if top_n < r:
        return 0.0
    prod = 1.0
    for i in range(r):
        prod *= (top_n - i) / (bot_n - i)
    return prod


def expected_second_shortest(n: int, m: int) -> float:
    """
    Fast floating-point computation of E(n,m).
    Works well for the Euler target (n=10^7, m=100).
    """
    if not (1 <= m <= n):
        raise ValueError("Require 1 <= m <= n")
    if m == 1:
        return float(n)

    r = m - 1
    n_total = n - 1  # denominator uses C(n-1, r)
    # Precompute inverses for the fixed denominator terms to save divisions in base ratio
    inv_den = [1.0 / (n_total - i) for i in range(r)]

    # Iterate k = 1..kmax implicitly by decrementing N2 and N1 each time:
    # N2(k) = n - (m-1)k + (m-2) starts at n-1 and decreases by (m-1)
    # N1(k) = n - mk + (m-1)      starts at n-1 and decreases by m
    N2 = n_total
    N1 = n_total

    acc = 0.0
    while N2 >= r:
        # base = C(N2,r)/C(n_total,r)
        base = 1.0
        for i in range(r):
            base *= (N2 - i) * inv_den[i]

        if N1 >= r:
            # ratio = C(N1,r)/C(N2,r)
            ratio = _binom_ratio(N1, N2, r)
            factor = m - (m - 1) * ratio
        else:
            factor = float(m)

        acc += base * factor

        N2 -= m - 1
        N1 -= m

    return acc


def solve() -> None:
    ans = expected_second_shortest(10_000_000, 100)
    print(f"{ans:.5f}")


if __name__ == "__main__":
    # Test values from the problem statement:
    assert expected_second_shortest_exact(3, 2) == 2
    assert expected_second_shortest_exact(8, 3) == Fraction(16, 7)

    solve()
