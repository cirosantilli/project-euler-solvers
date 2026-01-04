from __future__ import annotations

from math import gcd
from typing import Tuple


def best_fraction_left_of(target_n: int, target_d: int, max_d: int) -> Tuple[int, int]:
    """
    Returns (n, d) = reduced proper fraction with d <= max_d, n/d < target_n/target_d,
    and n/d as large as possible.
    """
    best_n, best_d = 0, 1

    for d in range(1, max_d + 1):
        # Largest n such that n/d < target_n/target_d  =>  n < target_n*d/target_d
        n = (target_n * d - 1) // target_d
        if n <= 0:
            continue

        if gcd(n, d) != 1:
            continue

        # Compare n/d > best_n/best_d via cross-multiplication
        if n * best_d > best_n * d:
            best_n, best_d = n, d

    return best_n, best_d


def solve(max_d: int) -> int:
    n, d = best_fraction_left_of(3, 7, max_d)
    return n


if __name__ == "__main__":
    # Test from the statement: for d <= 8, fraction immediately left of 3/7 is 2/5
    assert best_fraction_left_of(3, 7, 8) == (2, 5)

    ans = solve(1_000_000)

    print(ans)
