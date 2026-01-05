#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0168.cpp"""


def search(num_digits: int, multiplier: int, last_digit: int, modulo: int) -> int:
    shift = 10
    carry = 0

    current = last_digit
    result = last_digit

    while num_digits > 1:
        num_digits -= 1
        next_val = multiplier * current + carry
        carry = next_val // 10
        current = next_val % 10

        if shift < modulo:
            result += current * shift
            shift *= 10

    first = multiplier * current + carry
    if current == 0 or first != last_digit:
        return 0

    return result


def solve(max_digits: int) -> int:
    modulo = 100000
    result = 0

    for num_digits in range(2, max_digits + 1):
        for multiplier in range(1, 10):
            for last_digit in range(1, 10):
                result += search(num_digits, multiplier, last_digit, modulo)

    return result % modulo


def main() -> None:
    print(solve(100))


if __name__ == "__main__":
    main()
