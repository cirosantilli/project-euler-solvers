#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0190.cpp"""
import math


def floor_p(m: int) -> int:
    total_weight = m * (m + 1) / 2.0
    scale = total_weight / m
    total = 0.0
    for i in range(1, m + 1):
        x = i / scale
        total += i * math.log(x)
    return int(math.floor(math.exp(total)))


def solve(limit: int) -> int:
    total = 0
    for m in range(2, limit + 1):
        total += floor_p(m)
    return total


def main() -> None:
    assert floor_p(10) == 4112
    print(solve(15))


if __name__ == "__main__":
    main()
