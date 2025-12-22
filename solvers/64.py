from __future__ import annotations

from math import isqrt
from typing import Final


def period_length_sqrt(n: int) -> int:
    """
    Return the period length of the continued fraction for sqrt(n),
    assuming n is a positive non-square integer.
    """
    a0 = isqrt(n)
    if a0 * a0 == n:
        return 0  # perfect square -> no periodic continued fraction part

    m = 0
    d = 1
    a = a0

    period = 0
    while True:
        m = d * a - m
        d = (n - m * m) // d
        a = (a0 + m) // d
        period += 1
        # For sqrt(n), the period ends when a hits 2*a0.
        if a == 2 * a0:
            return period


def count_odd_periods(limit: int) -> int:
    cnt = 0
    for n in range(2, limit + 1):
        r = isqrt(n)
        if r * r == n:
            continue
        if period_length_sqrt(n) % 2 == 1:
            cnt += 1
    return cnt


def main() -> None:
    # Test from the statement: N <= 13 has exactly four odd periods.
    assert count_odd_periods(13) == 4

    LIMIT: Final[int] = 10_000
    result = count_odd_periods(LIMIT)
    print(result)


if __name__ == "__main__":
    main()
