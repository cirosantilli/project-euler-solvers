#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0216.cpp"""


def mulmod(a: int, b: int, modulo: int) -> int:
    return (a * b) % modulo


def powmod(base: int, exponent: int, modulo: int) -> int:
    result = 1
    while exponent > 0:
        if exponent & 1:
            result = mulmod(result, base, modulo)
        base = mulmod(base, base, modulo)
        exponent >>= 1
    return result


def is_prime(p: int) -> bool:
    small_mask = (
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
        return (small_mask & (1 << p)) != 0

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

    test_against1 = (377687, 0)
    test_against2 = (31, 73, 0)
    test_against3 = (2, 7, 61, 0)
    test_against4 = (2, 13, 23, 1662803, 0)
    test_against7 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022, 0)

    if p < 5329:
        test_against = test_against1
    elif p < 9080191:
        test_against = test_against2
    elif p < 4759123141:
        test_against = test_against3
    elif p < 1122004669633:
        test_against = test_against4
    else:
        test_against = test_against7

    d = p - 1
    shift = 0
    while d % 2 == 0:
        d //= 2
        shift += 1

    for base in test_against:
        if base == 0:
            break
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


def solve(limit: int) -> int:
    count = 0
    candidate = [True] * (limit + 1)

    max_sieve_prime = max(limit // 50, 10000)
    small_primes = []
    for p in range(3, max_sieve_prime + 1):
        if is_prime(p):
            small_primes.append(p)
    filter_threshold = 2 * max_sieve_prime

    for n in range(2, limit + 1):
        if not candidate[n]:
            continue

        p = 2 * n * n - 1
        if is_prime(p):
            count += 1
            continue

        if n < filter_threshold:
            for s in small_primes:
                if p > s and p % s == 0:
                    for i in range(n, limit + 1, s):
                        candidate[i] = False

    return count


if __name__ == "__main__":
    assert solve(10000) == 2202
    print(solve(50000000))
