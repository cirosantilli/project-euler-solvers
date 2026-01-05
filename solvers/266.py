#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0266.cpp"""
import bisect
import math

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
    101,
    103,
    107,
    109,
    113,
    127,
    131,
    137,
    139,
    149,
    151,
    157,
    163,
    167,
    173,
    179,
    181,
]


def pseudo_square_root(n: int) -> int:
    limit = int(math.isqrt(n))
    best = 1
    for d in range(1, limit + 1):
        if n % d == 0:
            best = d
    return best


def solve(max_prime: int) -> int:
    primes = list(PRIMES)
    while primes and primes[-1] > max_prime:
        primes.pop()

    log_primes = []
    log_product = 0.0
    for p in primes:
        current = math.log(p)
        log_primes.append(current)
        log_product += current

    log_root = log_product / 2.0
    half = len(primes) // 2

    right = []
    for bitmask in range(1 << half):
        log_right = 0.0
        for pos in range(half):
            if bitmask & (1 << pos):
                log_right += log_primes[pos + half]
        if log_right <= log_root:
            right.append((log_right, bitmask))

    right.sort()

    best = 0.0
    left_mask = 0
    right_mask = 0
    for bitmask in range(1 << half):
        log_left = 0.0
        for pos in range(half):
            if bitmask & (1 << pos):
                log_left += log_primes[pos]

        missing = log_root - log_left
        pos = bisect.bisect_right(right, (missing, float("inf"))) - 1
        log_right, candidate_mask = right[pos]

        if best < log_left + log_right:
            best = log_left + log_right
            left_mask = bitmask
            right_mask = candidate_mask

    modulo = 10000000000000000
    result = 1
    current_prime = 0

    while current_prime < half:
        if left_mask & 1:
            result = (result * primes[current_prime]) % modulo
        left_mask >>= 1
        current_prime += 1

    while current_prime < len(primes):
        if right_mask & 1:
            result = (result * primes[current_prime]) % modulo
        right_mask >>= 1
        current_prime += 1

    return result


def main():
    assert pseudo_square_root(3102) == 47
    print(solve(190))


if __name__ == "__main__":
    main()
