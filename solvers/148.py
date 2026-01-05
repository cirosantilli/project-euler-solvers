#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0148.cpp"""
MODULO = 7


def solve(num_rows: int) -> int:
    base7 = [1] * 12
    count = 1

    for _ in range(1, num_rows):
        base7[0] += 1
        carry_pos = 0
        while base7[carry_pos] == MODULO + 1:
            base7[carry_pos] = 1
            base7[carry_pos + 1] += 1
            carry_pos += 1

        found = 1
        for x in base7:
            found *= x
        count += found

    return count


def main() -> None:
    assert solve(7) == 28
    assert solve(100) == 2361
    print(solve(1000000000))


if __name__ == "__main__":
    main()
