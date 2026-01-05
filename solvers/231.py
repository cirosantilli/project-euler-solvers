#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0231.cpp"""
sieve = bytearray()
primes = [2]


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


def add(n: int) -> int:
    total = 0
    for p in primes:
        if p > n:
            return total

        multiple = p
        count = n // multiple
        while count > 0:
            total += p * count
            multiple *= p
            count = n // multiple

    return total


def solve(n: int, k: int) -> int:
    primes.clear()
    primes.append(2)
    fill_sieve(n)
    for i in range(3, n + 1, 2):
        if is_prime(i):
            primes.append(i)

    return add(n) - (add(n - k) + add(k))


def main() -> None:
    assert solve(10, 3) == 14
    print(solve(20000000, 15000000))


if __name__ == "__main__":
    main()
