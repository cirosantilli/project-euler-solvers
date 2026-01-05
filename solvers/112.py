#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0112.cpp"""


def is_bouncy(x: int) -> bool:
    ascending = True
    descending = True

    previous = x % 10
    x //= 10

    while x > 0:
        current = x % 10
        descending = descending and previous >= current
        ascending = ascending and previous <= current

        if not ascending and not descending:
            return True

        x //= 10
        previous = current

    return False


def count_bouncy_below(limit: int) -> int:
    count = 0
    for value in range(1, limit):
        if is_bouncy(value):
            count += 1
    return count


def least_for_ratio(p: int, q: int) -> int:
    current = 100
    num_bouncy = 0
    while True:
        current += 1
        if is_bouncy(current):
            num_bouncy += 1
        if num_bouncy * q >= current * p:
            return current


def main() -> None:
    assert count_bouncy_below(1000) == 525
    assert least_for_ratio(1, 2) == 538
    assert least_for_ratio(9, 10) == 21780
    print(least_for_ratio(99, 100))


if __name__ == "__main__":
    main()
