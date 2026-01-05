#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0132.cpp"""


def powmod(base: int, exponent: int, modulo: int) -> int:
    return pow(base, exponent, modulo)


def solve(digits: int, num_factors: int) -> int:
    total = 0
    primes = [2]
    i = 3
    while num_factors > 0:
        is_prime = True
        for p in primes:
            if p * p > i:
                break
            if i % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(i)
            modulo = 9 * i
            if powmod(10, digits, modulo) == 1:
                total += i
                num_factors -= 1
            if i > 1111111:
                break
        i += 2

    return total


def main() -> None:
    assert solve(10, 4) == 9414
    print(solve(1000000000, 40))


if __name__ == "__main__":
    main()
