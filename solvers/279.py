#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0279.cpp"""
import math


def gcd(a, b):
    while a != 0:
        a, b = b % a, a
    return b


def search90(limit):
    result = 0
    last = int(math.sqrt(limit / 2))
    for m in range(2, last):
        n = (m & 1) + 1
        while n < m:
            if gcd(m, n) != 1:
                n += 2
                continue

            a = m * m - n * n
            b = 2 * m * n
            c = m * m + n * n

            total = a + b + c
            if total > limit:
                break

            result += limit // total
            n += 2

    return result


def search60(limit):
    last = int(math.sqrt(limit * 3 / 2))
    result = 0
    for m in range(2, last):
        n = 1
        while 2 * n <= m:
            if gcd(m, n) != 1:
                n += 1
                continue

            a = m * m - m * n + n * n
            b = 2 * m * n - n * n
            c = m * m - n * n

            total = a + b + c
            if a % 3 == 0 and b % 3 == 0 and c % 3 == 0:
                total //= 3
            if total > 3 * limit:
                break

            if total <= limit:
                result += limit // total

            n += 1

    return result


def search120(limit):
    result = 0
    last = int(math.sqrt(limit * 3 / 2))
    for m in range(2, last):
        n = 1
        while 2 * n <= m:
            if gcd(m, n) != 1:
                n += 1
                continue

            a = m * m + m * n + n * n
            b = 2 * m * n + n * n
            c = m * m - n * n

            if b > c:
                break

            total = a + b + c
            if a % 3 == 0 and b % 3 == 0 and c % 3 == 0:
                total //= 3
            if total > 3 * limit:
                break

            result += limit // total
            n += 1

    return result


def solve(limit: int) -> int:
    num60 = search60(limit)
    num90 = search90(limit)
    num120 = search120(limit)
    return num60 + num90 + num120


if __name__ == "__main__":
    print(solve(100000000))
