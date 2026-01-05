#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0171.cpp"""
MODULO = 1000000000


def count_sum(digits: list[int], factorials: list[int], is_square: list[bool]) -> int:
    sum_sq = 0
    count = 0
    for digit, qty in enumerate(digits):
        sum_sq += qty * digit * digit
        count += qty

    if not is_square[sum_sq]:
        return 0

    result = factorials[count]
    for qty in digits:
        result //= factorials[qty]

    numerator = 0
    for digit, qty in enumerate(digits):
        numerator += digit * qty
    result *= numerator
    result //= count

    ones = 1
    for _ in range(2, min(count, 9) + 1):
        ones = ones * 10 + 1

    result %= MODULO
    result = (result * ones) % MODULO
    return result


def search(
    digits: list[int], at_least_digit: int, digits_left: int, factorials, is_square
) -> int:
    if digits_left == 0:
        return count_sum(digits, factorials, is_square)

    result = 0
    for current in range(at_least_digit, 10):
        digits[current] += 1
        result += search(digits, current, digits_left - 1, factorials, is_square)
        digits[current] -= 1

    return result % MODULO


def solve(num_digits: int) -> int:
    factorials = [1]
    for i in range(1, num_digits + 1):
        factorials.append(i * factorials[-1])

    max_square = num_digits * 9 * 9
    is_square = [False] * (max_square + 1)
    i = 1
    while i * i <= max_square:
        is_square[i * i] = True
        i += 1

    digits = [0] * 10
    result = search(digits, 0, num_digits, factorials, is_square)
    return result % MODULO


def main() -> None:
    print(solve(20))


if __name__ == "__main__":
    main()
