#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0274.cpp"""
SLOW = False
TRICK7 = True


def find_m(p):
    for m in range(1, p):
        at_least_multiples = 10
        ok = True
        for k in range(1, at_least_multiples):
            current = k * p
            a = current // 10
            b = current % 10
            if (a + m * b) % p != 0:
                ok = False
                break
        if ok:
            return m
    return 0


def powmod(base, exponent, modulo):
    result = 1
    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulo
        base = (base * base) % modulo
        exponent >>= 1
    return result


def solve(limit: int) -> int:
    sieve = [True] * limit

    total = 0
    n = 3
    while n < limit:
        if not sieve[n >> 1]:
            n += 2
            continue

        if n * n < limit:
            step = 2 * n
            i = n * n
            while i < limit:
                sieve[i >> 1] = False
                i += step

        if n == 5:
            n += 2
            continue

        last_digit = n % 10
        first_digits = n // 10

        if SLOW:
            total += find_m(n)
            n += 2
            continue

        if TRICK7:
            reduced = (n - first_digits) // last_digit
            if last_digit != 7:
                total += reduced
                n += 2
                continue

        modular_inverse = powmod(10, n - 2, n)
        total += modular_inverse
        n += 2

    return total


if __name__ == "__main__":
    assert solve(1000) == 39517
    print(solve(10000000))
