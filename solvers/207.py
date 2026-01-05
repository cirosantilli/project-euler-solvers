#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0207.cpp"""


def is_power_of_two(x: int) -> bool:
    return (x & (x - 1)) == 0


def solve(numerator: int, denominator: int) -> int:
    if numerator > denominator or numerator == 0:
        return 0

    total = 1
    perfect = 1
    x = 3

    while perfect * denominator > total * numerator:
        if is_power_of_two(x):
            perfect += 1
        total += 1
        x += 1

    k = x * (x - 1)
    return k


def main() -> None:
    print(solve(1, 12345))


if __name__ == "__main__":
    main()
