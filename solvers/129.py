#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0129.cpp"""


def get_min_k(x: int) -> int:
    if x % 2 == 0 or x % 5 == 0:
        return 0

    result = 1
    repunit = 1
    while repunit != 0:
        repunit = (repunit * 10 + 1) % x
        result += 1

    return result


def least_exceeding(limit: int) -> int:
    i = limit
    while get_min_k(i) <= limit:
        i += 1
    return i


def main() -> None:
    assert least_exceeding(10) == 17
    print(least_exceeding(1000000))


if __name__ == "__main__":
    main()
