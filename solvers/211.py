#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0211.cpp"""
import math


def process_slice(from_val: int, to_val: int) -> int:
    sum_squares = [0] * (to_val - from_val + 1)
    for i in range(1, to_val + 1):
        pos = (from_val // i) * i
        if pos < from_val:
            pos += i
        while pos <= to_val:
            sum_squares[pos - from_val] += i * i
            pos += i

    total = 0
    for idx, current in enumerate(sum_squares):
        number = from_val + idx
        root = int(math.isqrt(current))
        if root * root == current:
            total += number

    return total


def solve(limit: int) -> int:
    slice_size = 2000000
    total = 0
    from_val = 1
    while from_val < limit:
        to_val = from_val + slice_size - 1
        if to_val >= limit:
            to_val = limit
        total += process_slice(from_val, to_val)
        from_val = to_val + 1

    return total


if __name__ == "__main__":
    print(solve(64000000))
