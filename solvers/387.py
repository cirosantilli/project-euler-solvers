#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0387.cpp"""
import bisect


def mulmod(a, b, modulo):
    return (a * b) % modulo


def powmod(base, exponent, modulo):
    result = 1
    while exponent > 0:
        if exponent & 1:
            result = mulmod(result, base, modulo)
        base = mulmod(base, base, modulo)
        exponent >>= 1
    return result


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
        x = powmod(base, d, p)
        if x == 1 or x == p - 1:
            continue

        maybe_prime = False
        for _ in range(shift):
            x = mulmod(x, x, p)
            if x == 1:
                return False
            if x == p - 1:
                maybe_prime = True
                break

        if not maybe_prime:
            return False

    return True


def digit_sum(x):
    result = 0
    while x >= 10:
        result += x % 10
        x //= 10
    return result + x


def solve(max_digits=14):
    result = 0
    todo = [1, 2, 3, 4, 5, 6, 7, 8, 9]
    strong = set()

    num_digits = 1
    while num_digits < max_digits:
        num_digits += 1
        next_values = []

        for x in todo:
            is_strong_parent = x in strong

            for digit in range(10):
                current = x * 10 + digit
                if is_strong_parent and is_prime(current):
                    result += current

                reduced = digit_sum(current)
                if current % reduced == 0:
                    next_values.append(current)
                    if is_prime(current // reduced):
                        strong.add(current)

        todo = next_values

    return result


def main():
    assert solve(4) == 90619
    print(solve())


if __name__ == "__main__":
    main()
