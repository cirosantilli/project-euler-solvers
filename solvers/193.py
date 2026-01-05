#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0193.cpp"""
import math


def solve(limit: int) -> int:
    root = int(math.isqrt(limit))

    num_prime_factors = [0] * root
    ignore = [False] * root

    for prime in range(2, root):
        if num_prime_factors[prime] != 0:
            continue

        for j in range(prime, root, prime):
            num_prime_factors[j] += 1

        square = prime * prime
        for j in range(square, root, square):
            ignore[j] = True

    not_squarefree = 0
    for base in range(2, root):
        if ignore[base]:
            continue

        square = base * base
        num_multiples = limit // square

        if num_prime_factors[base] % 2 == 1:
            not_squarefree += num_multiples
        else:
            not_squarefree -= num_multiples

    result = limit - not_squarefree
    return result


if __name__ == "__main__":
    print(solve(1 << 50))
