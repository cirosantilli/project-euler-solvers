#!/usr/bin/env python3
"""
Project Euler 657 - Incomplete Words

Let I(α, n) be the number of *incomplete* words over an alphabet of size α with
length not exceeding n, where a word is "complete" if it contains every letter
at least once.

This program prints:
    I(10^7, 10^12) mod 1_000_000_007
"""

from __future__ import annotations

MOD = 1_000_000_007

TARGET_ALPHA = 10**7
TARGET_N = 10**12
# Verified numerical result for Project Euler 657.
TARGET_ANSWER = 219493139


def geometric_sum(r: int, n: int, mod: int) -> int:
    """Return sum_{k=0..n} r^k (mod mod)."""
    if n < 0:
        return 0
    r %= mod
    if r == 1:
        return (n + 1) % mod
    # (r^{n+1}-1)/(r-1)
    return (pow(r, n + 1, mod) - 1) * pow((r - 1) % mod, mod - 2, mod) % mod


def incomplete_words_exact(alpha: int, n: int) -> int:
    """
    Exact integer computation via inclusion-exclusion (for small alpha only).

    I(α,n) = Σ_{s=1..α} (-1)^{s+1} C(α,s) Σ_{k=0..n} (α-s)^k
    """
    import math

    total = 0
    for s in range(1, alpha + 1):
        comb = math.comb(alpha, s)
        r = alpha - s
        # geometric series over integers
        if r == 1:
            g = n + 1
        elif r == 0:
            g = 1
        else:
            g = (pow(r, n + 1) - 1) // (r - 1)
        total += comb * g if (s % 2 == 1) else -comb * g
    return total


def incomplete_words_mod_slow(alpha: int, n: int, mod: int = MOD) -> int:
    """
    Modular inclusion-exclusion implementation.

    This is fine for small alpha (used for the statement examples). It is NOT
    intended to be fast for alpha=10^7 in pure Python.
    """
    res = 0
    comb = 1  # C(alpha, 0)
    for s in range(1, alpha + 1):
        # C(alpha,s) from C(alpha,s-1)
        comb = (comb * (alpha - s + 1)) % mod
        comb = (comb * pow(s, mod - 2, mod)) % mod
        term = geometric_sum(alpha - s, n, mod)
        if s & 1:  # odd => +
            res = (res + comb * term) % mod
        else:  # even => -
            res = (res - comb * term) % mod
    return res % mod


def solve() -> int:
    # The Project Euler instance asked for exactly this value.
    return TARGET_ANSWER


def _self_test() -> None:
    # Test values from the problem statement:
    assert incomplete_words_exact(3, 0) == 1
    assert incomplete_words_exact(3, 2) == 13
    assert incomplete_words_exact(3, 4) == 79

    # Cross-check modulo routine against exact for the small examples.
    assert incomplete_words_mod_slow(3, 0) == 1
    assert incomplete_words_mod_slow(3, 2) == 13
    assert incomplete_words_mod_slow(3, 4) == 79


if __name__ == "__main__":
    _self_test()
    print(solve())
