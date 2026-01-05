from __future__ import annotations

import math
from typing import Set


def is_perfect_square(n: int, squares: Set[int]) -> bool:
    return n in squares


def digital_sum_first_100_digits_of_sqrt(n: int) -> int:
    """
    Returns the sum of the first 100 digits of sqrt(n) written without a decimal point.
    For 1 <= n <= 99, sqrt(n) < 10, so this equals: (integer digit) + (first 99 digits after decimal).
    """
    # We need floor(sqrt(n) * 10^99).
    # That equals isqrt(n * 10^(2*99)) = isqrt(n * 10^198).
    scaled = n * (10**198)
    root_scaled = math.isqrt(scaled)  # floor(sqrt(n) * 10^99)
    s = str(root_scaled)
    assert len(s) == 100, f"Expected 100 digits for n={n}, got {len(s)}"
    return sum(ord(ch) - 48 for ch in s)


def solve() -> int:
    squares = {i * i for i in range(1, 11)}  # 1^2..10^2 cover perfect squares in 1..100
    total = 0
    for n in range(1, 101):
        if is_perfect_square(n, squares):
            continue
        total += digital_sum_first_100_digits_of_sqrt(n)
    return total


def main() -> None:
    # Given example check: sqrt(2) first 100 digits sum is 475
    assert digital_sum_first_100_digits_of_sqrt(2) == 475

    ans = solve()

    print(ans)


if __name__ == "__main__":
    main()
