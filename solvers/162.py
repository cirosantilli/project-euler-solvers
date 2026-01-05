#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0162.cpp"""


def count(
    digits: int,
    have_any: bool = False,
    have_zero: bool = False,
    have_one: bool = False,
    have_a: bool = False,
) -> int:
    if have_zero and have_one and have_a and digits < 15:
        return 1 << (4 * digits)
    if digits == 0:
        return 0

    next_count = count(digits - 1, True, have_zero, have_one, have_a)
    result = 13 * next_count

    result += (
        next_count
        if have_zero
        else count(digits - 1, have_any, have_any, have_one, have_a)
    )
    result += (
        next_count if have_one else count(digits - 1, True, have_zero, True, have_a)
    )
    result += (
        next_count if have_a else count(digits - 1, True, have_zero, have_one, True)
    )

    return result


def solve(digits: int) -> int:
    return count(digits)


def main() -> None:
    assert solve(3) == 4
    print(format(solve(16), "X"))


if __name__ == "__main__":
    main()
