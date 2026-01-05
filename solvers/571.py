#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0571.cpp"""
import itertools


def is_pandigital(number, base):
    used = 0
    all_bits = (1 << base) - 1

    while number >= base:
        digit = number % base
        used |= 1 << digit
        number //= base

    used |= 1 << number
    return used == all_bits


def solve(base=12, num_results=10):
    digits = list(range(12))
    digits[0] = 1
    digits[1] = 0
    digits = digits[:base]

    num_found = 0
    total = 0

    for perm in itertools.permutations(digits):
        if perm[0] == 0:
            continue

        current = 0
        for digit in perm:
            current = current * base + digit

        if base >= 8 and not is_pandigital(current, 8):
            continue

        is_good = True
        for b in range(base - 1, 1, -1):
            if not is_pandigital(current, b):
                is_good = False
                break

        if is_good:
            total += current
            num_found += 1
            if num_found == num_results:
                break

    return total


def main():
    assert solve(10, 10) == 20319792309
    print(solve())


if __name__ == "__main__":
    main()
