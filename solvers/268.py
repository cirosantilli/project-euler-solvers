#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0268.cpp"""
PRIMES = [
    2,
    3,
    5,
    7,
    11,
    13,
    17,
    19,
    23,
    29,
    31,
    37,
    41,
    43,
    47,
    53,
    59,
    61,
    67,
    71,
    73,
    79,
    83,
    89,
    97,
]


def tetrahedral(n):
    return n * (n + 1) * (n + 2) // 6


def solve(min_primes: int, num_primes: int, limit: int) -> int:
    primes = PRIMES[:num_primes]

    count = [0] * (num_primes + 1)
    for i in range(min_primes, len(count)):
        count[i] = tetrahedral(i - min_primes + 1)

    total = 0
    max_mask = (1 << num_primes) - 1
    mask = 0
    while mask < max_mask:
        product = 1
        too_large = False
        num_bits = 0
        for current in range(num_primes):
            bitpos = 1 << current
            if (mask & bitpos) == 0:
                continue

            num_bits += 1
            product *= primes[current]

            if product > limit:
                too_large = True
                with_lowest = mask & (mask - 1)
                lowest = mask - with_lowest
                mask += lowest
                while mask & (lowest << 1):
                    lowest <<= 1
                    mask += lowest
                mask -= 1
                break

        if not too_large and num_bits >= min_primes:
            divisible = limit // product
            divisible *= count[num_bits]
            if num_bits & 1:
                total -= divisible
            else:
                total += divisible

        mask += 1

    return total


if __name__ == "__main__":
    assert solve(4, len(PRIMES), 1000) == 23
    print(solve(4, len(PRIMES), 10000000000000000))
