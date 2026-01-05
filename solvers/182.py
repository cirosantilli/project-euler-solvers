#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0182.cpp"""
import math


def is_coprime(a: int, b: int) -> bool:
    if ((a | b) & 1) == 0:
        return False
    return math.gcd(a, b) == 1


def solve(p: int, q: int) -> int:
    phi = (p - 1) * (q - 1)

    best = 0xFFFFFFFF
    total = 0

    for encryption in range(phi):
        if not is_coprime(encryption, phi):
            continue
        bad_p = math.gcd(p - 1, encryption - 1) + 1
        bad_q = math.gcd(q - 1, encryption - 1) + 1
        num_plaintext = bad_p * bad_q

        if best == num_plaintext:
            total += encryption
        elif best > num_plaintext:
            best = num_plaintext
            total = encryption

    return total


if __name__ == "__main__":
    print(solve(1009, 3643))
