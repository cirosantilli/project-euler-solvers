#!/usr/bin/env python3
"""
Project Euler 527: Randomized Binary Search

Compute R(10^10) - B(10^10) rounded to 8 decimal places.

- B(n): expected guesses for standard binary search using g=floor((L+H)/2)
- R(n): expected guesses for randomized variant choosing uniform g in [L,H]

No external libraries are used.
"""

from __future__ import annotations

import math
from functools import lru_cache


# Euler–Mascheroni constant (hard-coded; Python's math module doesn't expose it in all versions)
EULER_GAMMA = 0.57721566490153286060651209008240243104215933593992


def harmonic_number(n: int) -> float:
    """Return H_n = 1 + 1/2 + ... + 1/n.

    For large n, uses the asymptotic expansion:
      H_n = ln(n) + gamma + 1/(2n) - 1/(12n^2) + 1/(120n^4) - 1/(252n^6) + 1/(240n^8) + ...
    """
    if n <= 0:
        return 0.0
    # Exact summation for small n (good for tests and keeps the code simple).
    if n < 2_000_000:
        s = 0.0
        for k in range(1, n + 1):
            s += 1.0 / k
        return s

    inv = 1.0 / n
    inv2 = inv * inv
    inv4 = inv2 * inv2
    inv6 = inv4 * inv2
    inv8 = inv4 * inv4
    return (
        math.log(n)
        + EULER_GAMMA
        + 0.5 * inv
        - (1.0 / 12.0) * inv2
        + (1.0 / 120.0) * inv4
        - (1.0 / 252.0) * inv6
        + (1.0 / 240.0) * inv8
    )


def expected_random_binary_search(n: int) -> float:
    """R(n): expected number of guesses for random binary search.

    Closed form derived from a recurrence:
        R(n) = 2*(n+1)/n * H_n - 3
    """
    hn = harmonic_number(n)
    return 2.0 * (n + 1) / n * hn - 3.0


@lru_cache(maxsize=None)
def expected_standard_binary_search(n: int) -> float:
    """B(n): expected number of guesses for standard binary search.

    Recurrence for interval size n:
      pick g = floor((1+n)/2), left=g-1, right=n-g
      B(n) = 1 + (left/n)*B(left) + (right/n)*B(right)
    """
    if n <= 1:
        # B(0)=0 (degenerate), B(1)=1
        return float(n)

    g = (n + 1) // 2
    left = g - 1
    right = n - g
    return (
        1.0
        + (left / n) * expected_standard_binary_search(left)
        + (right / n) * expected_standard_binary_search(right)
    )


def solve() -> str:
    # Tests from the problem statement (rounded to 8 decimal places)
    assert round(expected_standard_binary_search(6), 8) == 2.33333333
    assert round(expected_random_binary_search(6), 8) == 2.71666667

    n = 10**10
    ans = expected_random_binary_search(n) - expected_standard_binary_search(n)
    return f"{ans:.8f}"


if __name__ == "__main__":
    print(solve())
