#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0178.cpp"""
NO_DIGITS = 0
ALL_DIGITS = (1 << 10) - 1
MAX_DIGITS = 40

cache = [0] * (1024 * 10 * MAX_DIGITS)


def search(mask: int, current_digit: int, num_digits_left: int) -> int:
    mask |= 1 << current_digit

    if num_digits_left == 1:
        return 1 if mask == ALL_DIGITS else 0

    hash_value = mask * MAX_DIGITS * 10 + (num_digits_left - 1) * 10 + current_digit
    if cache[hash_value] != 0:
        return cache[hash_value]

    result = 0
    if current_digit > 0:
        result += search(mask, current_digit - 1, num_digits_left - 1)
    if current_digit < 9:
        result += search(mask, current_digit + 1, num_digits_left - 1)

    cache[hash_value] = result
    return result


def solve(max_digits: int) -> int:
    result = 0
    for num_digits in range(1, max_digits + 1):
        for digit in range(1, 10):
            result += search(NO_DIGITS, digit, num_digits)

    return result


if __name__ == "__main__":
    print(solve(40))
