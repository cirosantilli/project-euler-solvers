#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0133.cpp"""


def powmod(base: int, exponent: int, modulo: int) -> int:
    return pow(base, exponent, modulo)


def solve(max_prime: int) -> int:
    digits = 10000000000000000000
    total = 0
    primes = []
    for i in range(2, max_prime):
        is_prime = True
        for p in primes:
            if p * p > i:
                break
            if i % p == 0:
                is_prime = False
                break
        if not is_prime:
            continue
        primes.append(i)

        modulo = 9 * i
        remainder = powmod(10, digits, modulo)
        if remainder != 1:
            total += i
    return total


def main() -> None:
    assert solve(100) == 918
    print(solve(100000))


if __name__ == "__main__":
    main()
