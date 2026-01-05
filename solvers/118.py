#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0118.cpp"""
from typing import List

sieve: bytearray = bytearray()


def is_prime(x: int) -> bool:
    if x % 2 == 0:
        return x == 2
    if x >= len(sieve) * 2:
        i = 3
        while i * i <= x:
            if x % i == 0:
                return False
            i += 2
        return True
    return bool(sieve[x >> 1])


def fill_sieve(size: int) -> None:
    half = size >> 1
    global sieve
    sieve = bytearray([1]) * half
    sieve[0] = 0

    limit = int((half - 1) ** 0.5)
    for i in range(1, limit + 1):
        if sieve[i]:
            current = 3 * i + 1
            step = 2 * i + 1
            while current < half:
                sieve[current] = 0
                current += step


def next_permutation(a: List[int]) -> bool:
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


def search(digits: List[int], merged: List[int], first_pos: int = 0) -> int:
    if first_pos == len(digits):
        return 1

    total = 0
    current = 0
    while first_pos < len(digits):
        current = current * 10 + digits[first_pos]
        first_pos += 1

        if merged and current < merged[-1]:
            continue

        if is_prime(current):
            merged.append(current)
            total += search(digits, merged, first_pos)
            merged.pop()

    return total


def solve(str_digits: str) -> int:
    digits = sorted(int(ch) for ch in str_digits)

    count = 0
    while True:
        if digits[-1] % 2 == 0 and (len(digits) > 1 or digits[-1] != 2):
            if not next_permutation(digits):
                break
            continue

        count += search(digits, [])
        if not next_permutation(digits):
            break

    return count


def main() -> None:
    fill_sieve(100000000)
    print(solve("123456789"))


if __name__ == "__main__":
    main()
