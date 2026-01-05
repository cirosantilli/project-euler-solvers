#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0243.cpp"""
import sys

primes = []


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


def is_less(a1: int, b1: int, a2: int, b2: int) -> bool:
    return a1 * b2 < a2 * b1


def main() -> None:
    numerator = 15499
    denominator = 94744

    current = 1
    i = 2
    while True:
        is_prime = True
        for p in primes:
            if p * p > i:
                break
            if i % p == 0:
                is_prime = False
                break
        if not is_prime:
            i += 1
            continue

        primes.append(i)
        current *= i
        if is_less(phi(current), current - 1, numerator, denominator):
            break
        i += 1

    current //= primes[-1]

    i = 1
    while True:
        nxt = current * i
        if is_less(phi(nxt), nxt - 1, numerator, denominator):
            print(nxt)
            break
        i += 1


if __name__ == "__main__":
    main()
