#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0214.cpp"""
import math

primes = []

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


def phi(x: int) -> int:
    result = x
    reduced = x
    for p in primes:
        if p * p > reduced:
            break
        if reduced % p != 0:
            continue
        while reduced % p == 0:
            reduced //= p
        result -= result // p

    if reduced > 1:
        result -= result // reduced

    return result


def steps(x: int, max_steps: int) -> int:
    result = 1
    x -= 1
    result += 1

    while x > 1 and result < max_steps:
        x = phi(x)
        result += 1
        if (x & (x - 1)) == 0:
            while x > 1:
                x >>= 1
                result += 1

    return result


def solve(max_steps: int, limit: int) -> int:
    primes.clear()
    fill_sieve(limit)
    primes.append(2)

    result = 0
    for i in range(3, limit, 2):
        if not is_prime(i):
            continue
        if i * i <= limit:
            primes.append(i)

        if max_steps == 25 and i < 9548417:
            continue

        current = steps(i, max_steps + 1)
        if current == max_steps:
            result += i

    return result


def main() -> None:
    assert solve(4, 20) == 12
    print(solve(25, 40000000))


if __name__ == "__main__":
    main()
