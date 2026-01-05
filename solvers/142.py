#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0142.cpp"""
import math


def main() -> None:
    limit = 1000000
    is_square = [False] * limit
    i = 1
    while i * i < limit:
        is_square[i * i] = True
        i += 1

    a = 3
    while True:
        min_b = 2 if a % 2 == 0 else 1
        b = min_b
        while b < a:
            x = (a * a + b * b) // 2
            y = a * a - x
            if x <= y:
                break

            c = int(math.isqrt(x)) + 1
            while True:
                z = c * c - x
                if y <= z:
                    break

                if is_square[x - z] and is_square[y + z] and is_square[y - z]:
                    print(x + y + z)
                    return
                c += 1

            b += 2
        a += 1


if __name__ == "__main__":
    main()
