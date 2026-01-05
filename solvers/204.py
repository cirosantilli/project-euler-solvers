#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0204.cpp"""
limit = 1000000000
hamming = 100
primes = []


def search(x: int = 1, index_min_prime: int = 0) -> int:
    result = 1
    for i in range(index_min_prime, len(primes)):
        product = primes[i] * x
        if product > limit:
            break
        result += search(product, i)
    return result


def solve(max_prime: int, limit_value: int) -> int:
    global limit, hamming, primes
    limit = limit_value
    hamming = max_prime
    primes = []

    for i in range(2, hamming + 1):
        is_prime = True
        for p in primes:
            if p * p > i:
                break
            if i % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(i)

    return search()


def main() -> None:
    assert solve(5, 100000000) == 1105
    print(solve(100, 1000000000))


if __name__ == "__main__":
    main()
