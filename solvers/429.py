#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0429.cpp"""
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


def solve(limit, modulo):
    result = 1

    fill_sieve(limit)
    for p in range(2, limit + 1):
        if not is_prime(p):
            continue

        power = p
        count = 0
        while power <= limit:
            if 2 * power > limit:
                count += 1
                break
            multiples = limit // power
            count += multiples
            power *= p

        result = (result * (1 + pow(p, 2 * count, modulo))) % modulo

    return result


def main():
    assert solve(4, 1000000009) == 650
    print(solve(100000000, 1000000009))


if __name__ == "__main__":
    main()
