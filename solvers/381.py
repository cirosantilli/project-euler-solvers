#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0381.cpp"""
sieve = []


def is_prime(x):
    if (x & 1) == 0:
        return x == 2
    return sieve[x >> 1]


def fill_sieve(size):
    global sieve
    half = (size >> 1) + 1
    sieve = [True] * half
    if half > 0:
        sieve[0] = False

    i = 1
    while 2 * i * i < half:
        if sieve[i]:
            current = 3 * i + 1
            step = 2 * i + 1
            while current < half:
                sieve[current] = False
                current += step
        i += 1


def modular_inverse(a, modulo):
    original_modulo = modulo
    s = 0
    t = 1
    while a > 1:
        tmp = modulo
        quotient = a // modulo
        modulo = a % modulo
        a = tmp

        tmp2 = s
        s = t - quotient * s
        t = tmp2

    if t < 0:
        t += original_modulo
    return t


def facmod(n, modulo):
    if n >= modulo:
        return 0

    result = modulo - 1
    i = modulo - 1
    while i > n:
        result = (result * modular_inverse(i, modulo)) % modulo
        i -= 1

    return result


def s_value(p):
    minus5 = facmod(p - 5, p)
    minus4 = (minus5 * (p - 4)) % p
    minus3 = (minus4 * (p - 3)) % p
    minus2 = (minus3 * (p - 2)) % p
    minus1 = p - 1
    return (minus1 + minus2 + minus3 + minus4 + minus5) % p


def solve(limit=100000000):
    fill_sieve(limit)

    total = 0
    for i in range(5, limit):
        if not is_prime(i):
            continue
        total += s_value(i)

    return total


def main():
    assert s_value(7) == 4
    assert solve(100) == 480
    print(solve())


if __name__ == "__main__":
    main()
