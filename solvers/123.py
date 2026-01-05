#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0123.cpp"""


def least_n_exceeding(limit: int) -> int:
    primes = [2]
    i = 3
    while True:
        is_prime = True
        for p in primes:
            if p * p > i:
                break
            if i % p == 0:
                is_prime = False
                break
        if not is_prime:
            i += 2
            continue

        primes.append(i)
        if len(primes) % 2 == 0:
            i += 2
            continue

        remainder = 2 * i * len(primes)
        if remainder >= limit:
            return len(primes)

        i += 2


def main() -> None:
    assert least_n_exceeding(1000000000) == 7037
    print(least_n_exceeding(10000000000))


if __name__ == "__main__":
    main()
