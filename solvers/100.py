from __future__ import annotations

from typing import Tuple


def next_solution(u: int, v: int) -> Tuple[int, int]:
    """
    Given (u, v) solving u^2 - 2*v^2 = -1, generate the next larger solution.
    Uses multiplication by (3 + 2*sqrt(2)).
    """
    return 3 * u + 4 * v, 2 * u + 3 * v


def blue_red_for_total_limit(limit_n: int) -> Tuple[int, int, int]:
    """
    Find the first arrangement with total discs n > limit_n such that:
        P(two blue) = b/n * (b-1)/(n-1) = 1/2
    Returns (b, r, n).
    """
    # Use u = 2n - 1, v = 2b - 1, then u^2 - 2*v^2 = -1.
    u, v = 1, 1  # corresponds to (n, b) = (1, 1), a valid Pell seed

    while True:
        n = (u + 1) // 2
        b = (v + 1) // 2
        if n > limit_n:
            r = n - b
            return b, r, n
        u, v = next_solution(u, v)


def _self_test() -> None:
    # Generate early known solutions:
    u, v = 1, 1
    sols = []
    for _ in range(4):
        n = (u + 1) // 2
        b = (v + 1) // 2
        sols.append((b, n))
        u, v = next_solution(u, v)

    # (b, n) sequence starts: (1,1), (3,4), (15,21), (85,120), ...
    assert sols[2] == (15, 21)
    assert sols[3] == (85, 120)

    b, r, n = blue_red_for_total_limit(10**12)
    assert n > 10**12


def main() -> None:
    _self_test()
    b, r, n = blue_red_for_total_limit(10**12)
    print(b)


if __name__ == "__main__":
    main()
