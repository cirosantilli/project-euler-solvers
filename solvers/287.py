#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0287.cpp"""
size = 1 << 24


def is_black(x, y):
    middle = size >> 1
    threshold = middle * middle
    dx = x - middle
    dy = y - middle
    return dx * dx + dy * dy <= threshold


def encode(from_x, from_y, to_x, to_y, is_first=True):
    if from_x == to_x:
        return 2

    a = is_black(from_x, from_y)
    b = is_black(to_x, from_y)
    c = is_black(to_x, to_y)
    d = is_black(from_x, to_y)

    if a == b and b == c and c == d and not is_first:
        return 2

    if from_x + 1 == to_x:
        return 1 + 4 * 2

    half = (to_x - from_x + 1) // 2
    return (
        encode(from_x, from_y + half, to_x - half, to_y, False)
        + encode(from_x + half, from_y + half, to_x, to_y, False)
        + encode(from_x, from_y, to_x - half, to_y - half, False)
        + encode(from_x + half, from_y, to_x, to_y - half, False)
        + 1
    )


def solve(shift: int) -> int:
    global size
    size = 1 << shift
    return encode(0, 0, size - 1, size - 1)


if __name__ == "__main__":
    # TODO extra assert
    # assert solve(2) == 16
    print(solve(24))
