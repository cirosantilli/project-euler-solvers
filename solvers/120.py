#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0120.cpp"""


def main() -> None:
    def rmax(a: int) -> int:
        n_max = (a - 1) // 2
        return 2 * a * n_max

    assert rmax(7) == 42

    total = 0
    for a in range(3, 1001):
        total += rmax(a)

    print(total)


if __name__ == "__main__":
    main()
