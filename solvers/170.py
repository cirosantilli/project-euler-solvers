#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0170.cpp"""
from math import gcd


def is_pandigital(x: int) -> bool:
    used = [0] * 10
    while x > 0:
        digit = x % 10
        if used[digit]:
            return False
        used[digit] = 1
        x //= 10
    return True


def solve(limit: int) -> int:
    adjusted = max(limit, 1023456789)
    while not is_pandigital(adjusted):
        adjusted -= 1
    current = list(str(adjusted))

    while True:
        for split in range(1, len(current)):
            if current[0] == "0" or current[split] == "0":
                continue
            left = int("".join(current[:split]))
            right = int("".join(current[split:]))
            shared = gcd(left, right)
            factor = 3
            while factor <= shared:
                if left % factor == 0 and right % factor == 0:
                    one = left // factor
                    two = right // factor
                    sequence = f"{factor}{one}{two}"
                    if len(sequence) == 10 and is_pandigital(int(sequence)):
                        return int("".join(current))
                factor += 3
        if not prev_permutation(current):
            break
    return 0


def prev_permutation(arr: list[str]) -> bool:
    i = len(arr) - 2
    while i >= 0 and arr[i] <= arr[i + 1]:
        i -= 1
    if i < 0:
        return False
    j = len(arr) - 1
    while arr[j] >= arr[i]:
        j -= 1
    arr[i], arr[j] = arr[j], arr[i]
    arr[i + 1 :] = reversed(arr[i + 1 :])
    return True


if __name__ == "__main__":
    print(solve(9876543210))
