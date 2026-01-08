#!/usr/bin/env python3
"""
Project Euler 600: Integer Sided Equiangular Hexagons

We count (up to congruence) integer-sided equiangular *convex* hexagons
with perimeter <= n.

The derivation (sketched in README.md) reduces the problem to counting
nonnegative integer solutions to:

    s + 2z + 3t + 4y + 6b = n - 6

So H(n) is the coefficient of x^(n-6) in:
    1 / ((1-x)(1-x^2)(1-x^3)(1-x^4)(1-x^6))

We compute that coefficient with a classic "coin change" DP.
"""

from __future__ import annotations

import sys


def H(n: int) -> int:
    """Return H(n) as defined in Project Euler 600."""
    m = n - 6
    if m < 0:
        return 0

    coins = (1, 2, 3, 4, 6)
    dp = [0] * (m + 1)
    dp[0] = 1
    for c in coins:
        for i in range(c, m + 1):
            dp[i] += dp[i - c]
    return dp[m]


def main() -> None:
    # Test values given in the problem statement
    assert H(6) == 1
    assert H(12) == 10
    assert H(100) == 31248

    if len(sys.argv) >= 2:
        n = int(sys.argv[1])
        print(H(n))
    else:
        print(H(55106))


if __name__ == "__main__":
    main()
