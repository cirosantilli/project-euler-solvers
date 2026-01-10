#!/usr/bin/env python3
"""
Project Euler 687 - Shuffling Cards

We work with rank-strings of length 52 containing 13 ranks each repeated 4 times.
A rank is "perfect" if none of its four occurrences are adjacent.

Because suits only permute within ranks, every rank-string corresponds to exactly (4!)^13
distinct shuffles, so probabilities can be computed on rank-strings directly.
"""

from __future__ import annotations

from decimal import Decimal, getcontext, ROUND_HALF_UP
from math import comb, factorial, gcd


def poly_mul(a: list[int], b: list[int]) -> list[int]:
    """Multiply two integer polynomials given as coefficient lists."""
    res = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            if bj == 0:
                continue
            res[i + j] += ai * bj
    return res


def solve() -> str:
    RANKS = 13
    COPIES = 4
    N = RANKS * COPIES  # 52
    BASE = factorial(COPIES)  # 4! = 24

    # Inclusion-exclusion per rank uses the polynomial:
    #   P(x) = sum_{t=0..3} (-1)^t * C(3,t) / (4-t)! * x^t
    # To avoid fractions, scale by 24:
    #   Q(x) = 24*P(x) = 1 - 12x + 36x^2 - 24x^3
    Q = [1, -12, 36, -24]

    # Precompute factorials up to 52
    fact = [1] * (N + 1)
    for i in range(2, N + 1):
        fact[i] = fact[i - 1] * i

    # Qpow[m] = Q(x)^m as integer coefficients, degree 3m
    Qpow: list[list[int]] = [[1]]
    for m in range(1, RANKS + 1):
        Qpow.append(poly_mul(Qpow[-1], Q))

    # n[m] = number of rank-strings where a fixed set of m ranks are perfect.
    # Derived formula:
    #   n[m] = (1 / 24^13) * sum_{B=0..3m} (52-B)! * coeff(Q^m, x^B)
    denom = BASE**RANKS  # 24^13
    n = [0] * (RANKS + 1)
    for m in range(RANKS + 1):
        coeff = Qpow[m]
        num = 0
        for B, c in enumerate(coeff):
            num += fact[N - B] * c
        # Should be exactly divisible (n[m] is an integer count).
        assert num % denom == 0
        n[m] = num // denom
        assert n[m] >= 0

    total = n[0]

    # Binomial inversion:
    # n[m] = sum_{k=m..13} C(13-m, k-m) * z[k],
    # where z[k] = number of rank-strings whose perfect-set equals a particular
    # fixed subset of size k. Hence:
    # z[k] = sum_{m=k..13} (-1)^(m-k) * C(13-k, m-k) * n[m]
    z = [0] * (RANKS + 1)
    for k in range(RANKS + 1):
        s = 0
        for m in range(k, RANKS + 1):
            s += ((-1) ** (m - k)) * comb(RANKS - k, m - k) * n[m]
        z[k] = s
        assert z[k] >= 0

    # x[k] = number of rank-strings with exactly k perfect ranks (any choice).
    x = [0] * (RANKS + 1)
    for k in range(RANKS + 1):
        x[k] = comb(RANKS, k) * z[k]
    assert sum(x) == total

    # Test value from the problem statement:
    # Expected number of perfect ranks = 4324/425.
    exp_num = sum(k * x[k] for k in range(RANKS + 1))
    exp_den = total
    g = gcd(exp_num, exp_den)
    exp_num //= g
    exp_den //= g
    assert (exp_num, exp_den) == (4324, 425)

    # Probability that the number of perfect ranks is prime.
    primes = {2, 3, 5, 7, 11, 13}
    good = sum(x[k] for k in primes)

    # Decimal rounding to 10 places.
    getcontext().prec = 60
    ans = (Decimal(good) / Decimal(total)).quantize(
        Decimal("0.0000000000"), rounding=ROUND_HALF_UP
    )
    return format(ans, "f")


if __name__ == "__main__":
    print(solve())
