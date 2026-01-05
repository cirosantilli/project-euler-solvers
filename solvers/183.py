#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0183.cpp"""
import math


def solve(limit: int) -> int:
    cache = [0] * 5
    result = cache[-1]

    for n in range(len(cache), limit + 1):
        k = int(round(n / 2.718281828))

        tmp = k
        while tmp % 5 == 0:
            tmp //= 5
        while tmp % 2 == 0:
            tmp //= 2

        if n % tmp == 0:
            result -= n
        else:
            result += n

        cache.append(result)

    return cache[limit]


if __name__ == "__main__":
    assert solve(100) == 2438
    print(solve(10000))
