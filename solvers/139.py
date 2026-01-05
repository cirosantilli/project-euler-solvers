#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0139.cpp"""


def gcd(a: int, b: int) -> int:
    while a:
        a, b = b % a, a
    return b


def solve(max_length: int) -> int:
    num_valid = 0
    m = 2
    while 2 * m * m < max_length:
        n = 1
        while n < m:
            if (m + n) % 2 == 1 and gcd(m, n) == 1:
                a = m * m - n * n
                b = 2 * m * n
                c = m * m + n * n
                total = a + b + c

                diff = b - a
                if a > b:
                    diff = a - b

                if diff > 0 and c % diff == 0:
                    num_valid += max_length // total
            n += 1
        m += 1
    return num_valid


def main() -> None:
    print(solve(100000000))


if __name__ == "__main__":
    main()
