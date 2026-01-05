#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0259.cpp"""


class Fraction:
    def __init__(self, numerator, denominator=1):
        self.numerator = int(numerator)
        self.denominator = int(denominator)

    def __add__(self, other):
        return Fraction(
            self.numerator * other.denominator + other.numerator * self.denominator,
            self.denominator * other.denominator,
        )

    def __mul__(self, other):
        return Fraction(
            self.numerator * other.numerator,
            self.denominator * other.denominator,
        )

    def __truediv__(self, other):
        return Fraction(
            self.numerator * other.denominator,
            self.denominator * other.numerator,
        )

    def __lt__(self, other):
        return self.numerator * other.denominator < other.numerator * self.denominator

    def __eq__(self, other):
        return self.numerator * other.denominator == other.numerator * self.denominator


def search(digits):
    result = [Fraction(int(digits))]

    for split in range(1, len(digits)):
        left = digits[:split]
        right = digits[split:]

        left_fractions = search(left)
        right_fractions = search(right)

        for x in left_fractions:
            for y in right_fractions:
                result.append(x + y)
                result.append(x + Fraction(-y.numerator, y.denominator))
                result.append(x * y)
                if y.numerator != 0:
                    result.append(x / y)

    if len(result) > 1:
        result.sort()
        unique = [result[0]]
        for current in result[1:]:
            if not (current == unique[-1]):
                unique.append(current)
        result = unique

    return result


def solve(last_digit: int) -> int:
    digits = "123456789"[:last_digit]

    fractions = search(digits)

    found = []
    for current in fractions:
        if current.denominator < 0:
            current.numerator *= -1
            current.denominator *= -1
        if current.numerator <= 0:
            continue
        if current.numerator % current.denominator == 0:
            found.append(current.numerator // current.denominator)

    found.sort()
    unique = []
    for value in found:
        if not unique or value != unique[-1]:
            unique.append(value)

    total = 0
    for value in unique:
        total += value

    return total


if __name__ == "__main__":
    print(solve(9))
