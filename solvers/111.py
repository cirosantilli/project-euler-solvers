#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0111.cpp"""
from typing import List


def is_prime(x: int) -> bool:
    if x % 2 == 0:
        return x == 2
    i = 3
    while i * i <= x:
        if x % i == 0:
            return False
        i += 2
    return True


def next_permutation(a: List[str]) -> bool:
    i = len(a) - 2
    while i >= 0 and a[i] >= a[i + 1]:
        i -= 1
    if i < 0:
        return False
    j = len(a) - 1
    while a[j] <= a[i]:
        j -= 1
    a[i], a[j] = a[j], a[i]
    a[i + 1 :] = reversed(a[i + 1 :])
    return True


def search(digit: int, repeat: int, extra_digits: int) -> int:
    total = 0
    same_digit = str(digit) * repeat

    max_extra = 1
    for _ in range(extra_digits):
        max_extra *= 10

    for extra in range(max_extra):
        current = str(extra)
        if current != "".join(sorted(current)):
            continue

        if len(current) < extra_digits:
            current = "0" * (extra_digits - len(current)) + current

        current += same_digit
        chars = sorted(current)

        while True:
            if chars[0] != "0" and (ord(chars[-1]) % 2 == 1):
                num = int("".join(chars))
                if is_prime(num):
                    total += num
            if not next_permutation(chars):
                break

    return total


def solve(digits: int) -> int:
    total = 0
    for i in range(10):
        for repeated in range(digits - 1, 0, -1):
            insert_digits = digits - repeated
            found = search(i, repeated, insert_digits)
            if found > 0:
                total += found
                break
    return total


def main() -> None:
    assert solve(4) == 273700
    print(solve(10))


if __name__ == "__main__":
    main()
