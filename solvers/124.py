#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0124.cpp"""


def solve(limit: int, pos: int) -> int:
    products = [1] * (limit + 1)
    products[0] = 999999999

    for i in range(2, limit + 1):
        if products[i] > 1:
            continue
        for j in range(i, limit + 1, i):
            products[j] *= i

    radicals = [(products[n], n) for n in range(limit + 1)]
    radicals.sort()

    return radicals[pos - 1][1]


def main() -> None:
    assert solve(10, 4) == 8
    assert solve(10, 6) == 9
    print(solve(100000, 10000))


if __name__ == "__main__":
    main()
