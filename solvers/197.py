#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0197.cpp"""
import math


def f(x: float) -> float:
    return math.floor(pow(2.0, 30.403243784 - x * x)) * pow(10, -9)


def main() -> None:
    u = -1.0
    next_val = f(u)
    for _ in range(1, 513):
        u = next_val
        next_val = f(u)

    result = u + next_val
    print(f"{result:.9f}")


if __name__ == "__main__":
    main()
