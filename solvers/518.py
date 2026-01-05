#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0518.cpp"""
import math

sieve = []


def is_prime(x):
    if (x & 1) == 0:
        return x == 2
    return sieve[x >> 1]


def fill_sieve(size):
    global sieve
    half = (size >> 1) + 1
    sieve = [True] * half
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


def gcd(a, b):
    while a != 0:
        a, b = b % a, a
    return b


def brute_force(limit):
    total = 0
    for a in range(2, limit):
        if not is_prime(a):
            continue
        for c in range(a + 4, limit):
            if not is_prime(c):
                continue
            b2 = (a + 1) * (c + 1)
            b = int(math.isqrt(b2))
            if b * b != b2:
                continue
            b -= 1
            if not is_prime(b):
                continue
            total += a + b + c
    return total


def count(limit):
    total = 0
    x = 2
    while x * x < limit:
        k = 1
        while k * x * x < limit:
            a = k * x * x - 1
            if not is_prime(a):
                k += 1
                continue

            if x & 1:
                y_range = range(1, x)
            else:
                y_range = range(1, x, 2)

            for y in y_range:
                b = k * x * y - 1
                c = k * y * y - 1
                if not is_prime(b):
                    continue
                if not is_prime(c):
                    continue
                if gcd(x, y) > 1:
                    continue
                total += a + b + c

            k += 1
        x += 1

    return total


def main():
    fill_sieve(100000000)
    assert count(100) == 1035
    print(count(100000000))


if __name__ == "__main__":
    main()
