#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0291.cpp"""
import math


def is_prime(p):
    bitmask_primes_2_to_31 = (
        (1 << 2)
        | (1 << 3)
        | (1 << 5)
        | (1 << 7)
        | (1 << 11)
        | (1 << 13)
        | (1 << 17)
        | (1 << 19)
        | (1 << 23)
        | (1 << 29)
    )
    if p < 31:
        return (bitmask_primes_2_to_31 & (1 << p)) != 0

    if (
        p % 2 == 0
        or p % 3 == 0
        or p % 5 == 0
        or p % 7 == 0
        or p % 11 == 0
        or p % 13 == 0
        or p % 17 == 0
    ):
        return False

    if p < 17 * 19:
        return True

    test_against_1 = [377687]
    test_against_2 = [31, 73]
    test_against_3 = [2, 7, 61]
    test_against_4 = [2, 13, 23, 1662803]
    test_against_7 = [2, 325, 9375, 28178, 450775, 9780504, 1795265022]

    if p < 5329:
        test_against = test_against_1
    elif p < 9080191:
        test_against = test_against_2
    elif p < 4759123141:
        test_against = test_against_3
    elif p < 1122004669633:
        test_against = test_against_4
    else:
        test_against = test_against_7

    d = p - 1
    d >>= 1
    shift = 0
    while (d & 1) == 0:
        shift += 1
        d >>= 1

    for base in test_against:
        x = pow(base, d, p)
        if x == 1 or x == p - 1:
            continue

        maybe_prime = False
        for _ in range(shift):
            x = (x * x) % p
            if x == 1:
                return False
            if x == p - 1:
                maybe_prime = True
                break

        if not maybe_prime:
            return False

    return True


def solve(limit: int) -> int:
    last = int(math.isqrt(limit // 2))
    count = 0
    for n in range(1, last + 1):
        current = n * n + (n + 1) * (n + 1)
        if current <= limit and is_prime(current):
            count += 1

    return count


if __name__ == "__main__":
    print(solve(5000000000000000))
