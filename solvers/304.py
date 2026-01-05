#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0304.cpp"""


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

    small_primes = [
        19,
        23,
        29,
        31,
        37,
        41,
        43,
        47,
        53,
        59,
        61,
        67,
        71,
        73,
        79,
        83,
        89,
        97,
    ]
    for sp in small_primes:
        if p % sp == 0:
            return False

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


def fibonacci(n, modulo):
    if n == 0:
        return 0

    bit = 1 << (n.bit_length() - 1)
    a = 0
    b = 1
    while bit:
        next_a = (a * ((2 * b - a) % modulo)) % modulo
        b = (a * a + b * b) % modulo
        a = next_a

        if n & bit:
            a, b = b, (a + b) % modulo
        bit >>= 1

    return a


def solve(n: int, num_primes: int, modulo: int) -> int:
    last = fibonacci(n - 1, modulo)
    current = fibonacci(n, modulo)

    total = 0
    count = 0
    while count < num_primes:
        n += 1
        next_value = (last + current) % modulo
        last = current
        current = next_value

        if is_prime(n):
            total = (total + current) % modulo
            count += 1

    return total


if __name__ == "__main__":
    print(solve(100000000000000, 100000, 1234567891011))
