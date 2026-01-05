#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0169.cpp"""


def count_zeros(x: int) -> list[int]:
    while x & 1:
        x >>= 1

    result = []
    consecutive = 0
    while x > 0:
        if (x & 1) == 0:
            consecutive += 1
        else:
            result.insert(0, consecutive)
            consecutive = 0
        x >>= 1

    return result


def solve(x: int) -> int:
    zeros = count_zeros(x)

    result = 1
    total = 1
    for z in zeros:
        result += z * total
        total += result

    return result


def main() -> None:
    assert solve(10) == 5
    print(solve(10**25))


if __name__ == "__main__":
    main()
