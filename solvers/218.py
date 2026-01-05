#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0218.cpp"""
import math


def count_not_mod_42() -> int:
    result = 0
    multiplier = 1
    for x in range(42 * multiplier):
        for y in range(42 * multiplier):
            zero = (
                ((x * x - y * y) * (x * x - y * y) - 2 * x * y * 2 * x * y)
                * (x * x - y * y)
                * x
                * y
            )
            if zero % 42 != 0:
                result += 1
    return result


def main() -> None:
    print(count_not_mod_42())


if __name__ == "__main__":
    main()
