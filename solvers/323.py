#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0323.cpp"""
import math

max_bits = 32


def solve(limit=max_bits):
    digits = 10
    epsilon = 10 ** (-(digits + 1))

    result = 0.0
    round_num = 0
    while True:
        has_zero = pow(0.5, round_num)
        is_done = pow(1 - has_zero, limit)
        delta = 1 - is_done
        if delta < epsilon:
            break
        result += delta
        round_num += 1

    return result


def main():
    print(f"{solve():.10f}")


if __name__ == "__main__":
    main()
