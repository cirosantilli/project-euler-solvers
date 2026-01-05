#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0277.cpp"""


def is_good(x, sequence):
    for s in sequence:
        mod = x % 3
        if mod == 0:
            if s != "D":
                return False
            x //= 3
        elif mod == 1:
            if s != "U":
                return False
            x = (4 * x + 2) // 3
        else:
            if s != "d":
                return False
            x = (2 * x - 1) // 3
    return True


def solve(start: int, sequence: str) -> int:
    current = start
    step = 1
    for length in range(1, len(sequence) + 1):
        partial = sequence[:length]
        iterations = 0
        while not is_good(current, partial):
            current += step
            iterations += 1
            if iterations > 100:
                return 0
        step *= 3

    return current


if __name__ == "__main__":
    assert solve(1000000, "DdDddUUdDD") == 1004064
    print(solve(1000000000000000, "UDDDUdddDDUDDddDdDddDDUDDdUUDd"))
