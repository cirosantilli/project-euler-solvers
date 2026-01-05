#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0145.cpp"""


def reverse_number(x: int) -> int:
    result = 0
    while x > 9:
        digit = x % 10
        result = result * 10 + digit
        x //= 10
    return result * 10 + x


def only_odd(x: int) -> bool:
    while x > 0:
        if x % 2 == 0:
            return False
        x //= 10
    return True


def count_reversible(limit: int) -> int:
    factor = 2
    count = 0
    upper = min(limit, 100_000_000)
    for i in range(11, upper, factor):
        if only_odd(i + reverse_number(i)):
            count += factor
    return count


def main() -> None:
    assert count_reversible(1000) == 120
    print(count_reversible(1_000_000_000))


if __name__ == "__main__":
    main()
