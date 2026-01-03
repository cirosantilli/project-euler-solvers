#!/usr/bin/env python3
"""
Project Euler 498: Remainder of Polynomial Division

We need C(n, m, d) mod P where:
- F_n(x) = x^n
- G_m(x) = (x-1)^m
- R_{n,m}(x) is the remainder of F_n(x) / G_m(x)
- C(n,m,d) = abs(coefficient of x^d in R_{n,m}(x))
"""

from __future__ import annotations

import math

MOD = 999_999_937

# Given target
N_TARGET = 10**13
M_TARGET = 10**12
D_TARGET = 10**4


def signed_coeff_exact(n: int, m: int, d: int) -> int:
    """
    Exact signed coefficient of x^d in R_{n,m}(x), as a Python integer.

    For 0 <= d < m:
        coeff = (-1)^(m-1-d) * C(n, d) * C(n-d-1, m-d-1)
    Otherwise coeff = 0.

    (Derived from the truncated binomial expansion around x=1 and a partial
    alternating binomial sum identity.)
    """
    if d < 0 or d >= m:
        return 0
    # If m-d-1 is outside range [0, n-d-1], the binomial is 0 => coeff 0.
    top2 = n - d - 1
    bot2 = m - d - 1
    if bot2 < 0 or bot2 > top2:
        return 0
    sign = -1 if ((m - 1 - d) & 1) else 1
    return sign * math.comb(n, d) * math.comb(top2, bot2)


def C_exact(n: int, m: int, d: int) -> int:
    """Exact C(n,m,d) = abs(signed_coeff_exact)."""
    return abs(signed_coeff_exact(n, m, d))


def _max_lucas_digit(pairs: list[tuple[int, int]], p: int) -> int:
    """Find the maximum base-p digit (n_i) encountered across Lucas decompositions."""
    mx = 0
    for n, k in pairs:
        nn, kk = n, k
        while nn > 0 or kk > 0:
            ni = nn % p
            # ki is irrelevant for max size, but we still update digits for loop
            mx = max(mx, ni)
            nn //= p
            kk //= p
    return mx


def _build_factorials(max_n: int, p: int) -> tuple[list[int], list[int]]:
    """Precompute factorials and inverse factorials modulo prime p up to max_n."""
    fact = [1] * (max_n + 1)
    for i in range(1, max_n + 1):
        fact[i] = (fact[i - 1] * i) % p

    invfact = [1] * (max_n + 1)
    invfact[max_n] = pow(fact[max_n], p - 2, p)
    for i in range(max_n, 0, -1):
        invfact[i - 1] = (invfact[i] * i) % p

    return fact, invfact


def solve() -> int:
    # Asserts from the problem statement (and its worked example polynomial)
    assert signed_coeff_exact(6, 3, 0) == 10
    assert signed_coeff_exact(6, 3, 1) == -24
    assert signed_coeff_exact(6, 3, 2) == 15
    assert C_exact(6, 3, 1) == 24
    assert C_exact(100, 10, 4) == 227_197_811_615_775

    # We need:
    #   answer = C(n,m,d) mod MOD
    # Using the closed-form:
    #   C(n,m,d) = binom(n,d) * binom(n-d-1, m-d-1)
    n, m, d, p = N_TARGET, M_TARGET, D_TARGET, MOD

    pairs = [
        (n, d),
        (n - d - 1, m - d - 1),
    ]
    max_digit = _max_lucas_digit(pairs, p)
    fact, invfact = _build_factorials(max_digit, p)

    def nCk_small(nn: int, kk: int) -> int:
        if kk < 0 or kk > nn:
            return 0
        return (fact[nn] * invfact[kk] % p) * invfact[nn - kk] % p

    def nCk_lucas(nn: int, kk: int) -> int:
        res = 1
        while nn > 0 or kk > 0:
            ni = nn % p
            ki = kk % p
            if ki > ni:
                return 0
            res = (res * nCk_small(ni, ki)) % p
            nn //= p
            kk //= p
        return res

    part1 = nCk_lucas(n, d)
    part2 = nCk_lucas(n - d - 1, m - d - 1)
    return (part1 * part2) % p


if __name__ == "__main__":
    print(solve())
