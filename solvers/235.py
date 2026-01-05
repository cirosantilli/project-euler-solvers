#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0235.cpp"""
import sys


def s(r: float) -> float:
    result = 0.0
    x = 1.0
    for k in range(1, 5001):
        result += (900 - 3 * k) * x
        x *= r
    return result


def main() -> None:
    lower = 0.0
    upper = 2.0

    while upper - lower > 1e-13:
        mid = (upper + lower) / 2
        current = s(mid)
        if current < -600000000000.0:
            upper = mid
        else:
            lower = mid

    print(f"{(upper + lower) / 2:.12f}")


if __name__ == "__main__":
    main()
