#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0234.cpp"""
import math

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
    fill_sieve(int(math.isqrt(limit)) + 100)

    total = 0
    last = 2
    while last * last <= limit:
        nxt = last + 1
        while not is_prime(nxt):
            nxt += 1

        start = last * last
        end = nxt * nxt

        i = start + last
        while i < end and i <= limit:
            total += i
            i += last

        while end - nxt > limit:
            end -= nxt

        i = end - nxt
        while i > start:
            total += i
            i -= nxt

        step = last * nxt
        i = start - (start % step)
        while i < end and i <= limit:
            if i > start:
                total -= i + i
            i += step

        last = nxt

    return total


def main() -> None:
    assert solve(15) == 30
    assert solve(1000) == 34825
    print(solve(999966663333))


if __name__ == "__main__":
    main()
