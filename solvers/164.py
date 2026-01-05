#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0164.cpp"""
MAX_DIGITS = 100
max_sum = 9
cache = [0] * ((MAX_DIGITS + 1) * 100)


def search(prevprev: int, prev: int, digits: int, is_first: bool) -> int:
    if digits == 0:
        return 1

    idx = digits * 100 + prevprev * 10 + prev
    if cache[idx] != 0:
        return cache[idx]

    result = 0
    current = 0
    while current + prev + prevprev <= max_sum:
        if current == 0 and is_first:
            current += 1
            continue
        result += search(prev, current, digits - 1, False)
        current += 1

    cache[idx] = result
    return result


def solve(digits: int, max_digit_sum: int) -> int:
    global max_sum
    max_sum = max_digit_sum
    if digits > MAX_DIGITS:
        return 0
    return search(0, 0, digits, True)


def main() -> None:
    print(solve(20, 9))


if __name__ == "__main__":
    main()
