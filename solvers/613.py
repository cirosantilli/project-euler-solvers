#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0613.cpp"""
import math

A = 3.0
B = 4.0
C = 5.0
PI = 3.1415926535897932384626433832795028


def get_alpha(x, y):
    return math.atan(x / (B - y))


def get_beta(x, y):
    return math.atan(y / (A - x))


def get_probability(x, y):
    gamma = PI / 2 + get_alpha(x, y) + get_beta(x, y)
    return gamma / (2 * PI)


def solve():
    result = 0.5 + math.log(
        (pow(2, 16) * pow(3, 4) * math.sqrt(3.0 / 5)) / pow(5, 12)
    ) / (12 * PI)
    return result


def main():
    print(f"{solve():.10f}")


if __name__ == "__main__":
    main()
