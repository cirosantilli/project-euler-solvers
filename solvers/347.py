#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0347.cpp"""
sieve = []


def is_prime(x):
    if (x & 1) == 0:
        return x == 2
    return sieve[x >> 1]


def fill_sieve(size):
    global sieve
    half = size >> 1
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


def solve(limit=10000000):
    fill_sieve(limit // 2)

    total = 0
    i = 2
    while i * i <= limit:
        if not is_prime(i):
            i = 3 if i == 2 else i + 2
            continue

        j = 3 if i == 2 else i + 2
        while i * j <= limit:
            if not is_prime(j):
                j += 2
                continue

            max_product = 0
            product = i * j
            while product <= limit:
                current = product
                while current * j <= limit:
                    current *= j
                if max_product < current:
                    max_product = current
                product *= i

            total += max_product
            j += 2

        i = 3 if i == 2 else i + 2

    return total


def main():
    assert solve(100) == 2262
    print(solve())


if __name__ == "__main__":
    main()
