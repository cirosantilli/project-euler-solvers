#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0249.cpp"""
MODULO = 10000000000000000
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


def solve(limit: int) -> int:
    fill_sieve(limit)
    max_sum = 2
    i = 3
    while i <= limit:
        if is_prime(i):
            max_sum += i
        i += 2

    count = [0] * (max_sum + 1)
    largest = 0
    count[largest] = 1

    for i in range(2, limit):
        if is_prime(i):
            largest += i
            for j in range(largest, i - 1, -1):
                count[j] = (count[j] + count[j - i]) % MODULO

    fill_sieve(max_sum)
    result = 0
    for i, value in enumerate(count):
        if is_prime(i):
            result = (result + value) % MODULO

    return result


if __name__ == "__main__":
    print(solve(5000))
