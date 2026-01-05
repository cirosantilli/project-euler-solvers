from __future__ import annotations

import math
from typing import Optional


def minimal_pell_x(D: int) -> Optional[int]:
    """
    Returns the minimal x > 0 solving x^2 - D*y^2 = 1 for some y > 0,
    or None if D is a perfect square.
    """
    a0 = math.isqrt(D)
    if a0 * a0 == D:
        return None

    m = 0
    d = 1
    a = a0

    # Convergents for continued fraction of sqrt(D):
    # h/k approximates sqrt(D)
    h_m2, h_m1 = 0, 1
    k_m2, k_m1 = 1, 0

    while True:
        h = a * h_m1 + h_m2
        k = a * k_m1 + k_m2

        if h * h - D * k * k == 1:
            return h

        h_m2, h_m1 = h_m1, h
        k_m2, k_m1 = k_m1, k

        m = d * a - m
        d = (D - m * m) // d
        a = (a0 + m) // d


def solve(limit: int = 1000) -> int:
    best_d = -1
    best_x = -1

    for D in range(2, limit + 1):
        x = minimal_pell_x(D)
        if x is None:
            continue
        if x > best_x:
            best_x = x
            best_d = D

    return best_d


def _tests() -> None:
    # From the statement/example
    assert minimal_pell_x(13) == 649


def main() -> None:
    _tests()
    print(solve(1000))


if __name__ == "__main__":
    main()
