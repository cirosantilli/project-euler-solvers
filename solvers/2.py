from __future__ import annotations

from typing import Tuple


def sum_even_fibonacci(limit: int) -> int:
    """
    Returns the sum of even Fibonacci numbers not exceeding `limit`,
    with Fibonacci starting at 1, 2, ...
    """
    a, b = 1, 2
    total = 0
    while a <= limit:
        if a % 2 == 0:
            total += a
        a, b = b, a + b
    return total


def main() -> None:
    # Known Project Euler #2 result for limit = 4_000_000
    assert sum_even_fibonacci(4_000_000) == 4_613_732

    result = sum_even_fibonacci(4_000_000)
    print(result)


if __name__ == "__main__":
    main()
