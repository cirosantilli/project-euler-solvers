#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0313.cpp"""
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


def search(width, height):
    if width < height:
        width, height = height, width

    if width < 2:
        return 0
    if width == 2:
        return 5
    if width == 3:
        return 9 if height == 2 else 13

    two = 6 * width - 9
    full = two + 2 * height - 4
    if width == height:
        full += 2
    return full


def verify_example() -> None:
    assert search(5, 4) == 25


def solve(limit: int) -> int:
    fill_sieve(limit)

    total = 0
    for p in range(2, limit + 1):
        if not is_prime(p):
            continue
        square = p * p
        increment = (square - 1) // 12
        if p == 3:
            total += 2
        else:
            total += increment

    return total


def main():
    verify_example()
    print(solve(1000000))


if __name__ == "__main__":
    main()
