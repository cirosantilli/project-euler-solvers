#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0278.cpp"""


def f(p: int, q: int, r: int) -> int:
    return 2 * p * q * r - p * q - p * r - q * r


def solve(limit: int) -> int:
    primes = [2]
    i = 3
    while i <= limit:
        is_prime = True
        for x in primes:
            if x * x > i:
                break
            if i % x == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(i)
        i += 2

    total = 0
    for i in range(len(primes)):
        for j in range(i + 1, len(primes)):
            for k in range(j + 1, len(primes)):
                p = primes[i]
                q = primes[j]
                r = primes[k]
                total += 2 * p * q * r - p * q - p * r - q * r

    return total


if __name__ == "__main__":
    assert f(2, 3, 5) == 29
    assert f(2, 7, 11) == 195
    print(solve(5000))
