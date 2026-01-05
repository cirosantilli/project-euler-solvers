#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0172.cpp"""
MAX_BITS = 1 << 20


def search(
    counts: list[int], digits: int, max_digits: int, max_use: int, cache: dict
) -> int:
    if digits == max_digits:
        return 1

    key = tuple(counts)
    if key in cache:
        return cache[key]

    result = 0
    if digits > 0 and counts[0] < max_use:
        counts[0] += 1
        result += search(counts, digits + 1, max_digits, max_use, cache)
        counts[0] -= 1

    for digit in range(1, 10):
        if counts[digit] < max_use:
            counts[digit] += 1
            result += search(counts, digits + 1, max_digits, max_use, cache)
            counts[digit] -= 1

    cache[key] = result
    return result


def solve(max_digits: int, max_use: int) -> int:
    if max_digits == 0 or max_digits > 29 or max_use == 0 or max_use > 3:
        return 0
    counts = [0] * 10
    cache: dict[tuple[int, ...], int] = {}
    return search(counts, 0, max_digits, max_use, cache)


if __name__ == "__main__":
    print(solve(18, 3))
