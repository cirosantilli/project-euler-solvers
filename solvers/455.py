#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0455.cpp"""


def search(n, modulo):
    exponent = n
    while True:
        next_value = pow(n, exponent, modulo)
        if next_value == 0 or next_value == exponent:
            return next_value
        exponent = next_value


def solve(limit=1000000, modulo=1000000000):
    total = 0
    for i in range(2, limit + 1):
        total += search(i, modulo)

    return total


def main():
    assert search(4, 1000000000) == 411728896
    assert search(10, 1000000000) == 0
    assert search(157, 1000000000) == 743757
    assert solve(1000, 1000000000) == 442530011399
    print(solve())


if __name__ == "__main__":
    main()
