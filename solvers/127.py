#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0127.cpp"""


def gcd(a: int, b: int) -> int:
    while a:
        a, b = b % a, a
    return b


def solve(limit: int) -> int:
    rad = [1] * limit
    for i in range(2, limit):
        if rad[i] > 1:
            continue
        for j in range(i, limit, i):
            rad[j] *= i

    total = 0
    for a in range(1, limit // 2):
        increment_b = 2 if a % 2 == 0 else 1
        b = a + 1
        while a + b < limit:
            c = a + b
            prod_rad = rad[a] * rad[b] * rad[c]
            if prod_rad < c:
                if gcd(rad[a], rad[b]) == 1:
                    total += c
            b += increment_b
    return total


def main() -> None:
    assert solve(1000) == 12523
    print(solve(120000))


if __name__ == "__main__":
    main()
