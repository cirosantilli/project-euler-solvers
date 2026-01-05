#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0229.cpp"""
import math

SLICE_SIZE = 1000 * 1000

ONE = 1 << 0
TWO = 1 << 1
THREE = 1 << 2
SEVEN = 1 << 3
ALL = ONE | TWO | THREE | SEVEN


def solve(limit: int) -> int:
    count = 0
    used = bytearray(SLICE_SIZE)

    max_a = int(math.isqrt(limit))
    b1 = [1] * (max_a + 1)
    b2 = [1] * (max_a + 1)
    b3 = [1] * (max_a + 1)
    b7 = [1] * (max_a + 1)

    start = 0
    while start < limit:
        end = start + SLICE_SIZE
        if end > limit:
            end = limit

        for a in range(1, max_a + 1):
            if a * a + b1[a] * b1[a] >= end:
                break

            b = b1[a]
            while a * a + b * b < end:
                used[a * a + b * b - start] |= ONE
                b += 1
            b1[a] = b

            b = b2[a]
            while a * a + 2 * b * b < end:
                used[a * a + 2 * b * b - start] |= TWO
                b += 1
            b2[a] = b

            b = b3[a]
            while a * a + 3 * b * b < end:
                used[a * a + 3 * b * b - start] |= THREE
                b += 1
            b3[a] = b

            b = b7[a]
            while a * a + 7 * b * b < end:
                used[a * a + 7 * b * b - start] |= SEVEN
                b += 1
            b7[a] = b

        for i in range(end - start):
            if used[i] == ALL:
                count += 1
            used[i] = 0

        start = end

    return count


def main() -> None:
    assert solve(10000000) == 75373
    print(solve(2000000000))


if __name__ == "__main__":
    main()
