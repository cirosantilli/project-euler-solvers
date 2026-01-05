#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0179.cpp"""


def solve(limit: int) -> int:
    limit += 1
    divisors = [0] * (limit + 1)

    for i in range(1, limit // 2 + 1):
        for j in range(i, limit + 1, i):
            divisors[j] += 1

    result = 0
    for i in range(2, limit):
        if divisors[i] == divisors[i + 1]:
            result += 1
    return result


if __name__ == "__main__":
    print(solve(10000000))
