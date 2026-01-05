#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0187.cpp"""
sieve = bytearray()


def fill_sieve(size: int) -> None:
    half = size >> 1
    global sieve
    sieve = bytearray([1]) * half
    sieve[0] = 0

    i = 1
    while 2 * i * i < half:
        if sieve[i]:
            current = 3 * i + 1
            step = 2 * i + 1
            while current < half:
                sieve[current] = 0
                current += step
        i += 1


def is_prime(x: int) -> bool:
    if x % 2 == 0:
        return x == 2
    return bool(sieve[x >> 1])


def solve(limit: int) -> int:
    largest_prime = limit // 2 + 100
    fill_sieve(largest_prime)

    primes = [2]
    for i in range(3, largest_prime, 2):
        if is_prime(i):
            primes.append(i)

    count = 0
    i = 0
    while i < len(primes) and primes[i] * primes[i] < limit:
        j = i
        while j < len(primes) and primes[i] * primes[j] < limit:
            count += 1
            j += 1
        i += 1

    return count


if __name__ == "__main__":
    assert solve(30) == 10
    print(solve(100000000))
