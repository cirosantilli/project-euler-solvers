#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0161.cpp"""


def use(pos: int, row: int) -> tuple[bool, int]:
    mask = 1 << pos
    result = (row & mask) == 0
    row |= mask
    return result, row


def search(
    rows_left: int, row_a: int, row_b: int, row_c: int, width: int, cache: dict
) -> int:
    if rows_left == 0:
        return 1

    full_row = (1 << width) - 1
    if row_a == full_row:
        return search(rows_left - 1, row_b, row_c, 0, width, cache)

    pos = 0
    while row_a & (1 << pos):
        pos += 1

    hash_value = rows_left
    hash_value = (hash_value << width) | row_a
    hash_value = (hash_value << width) | row_b
    hash_value = (hash_value << width) | row_c

    if hash_value in cache:
        return cache[hash_value]

    result = 0

    if rows_left >= 2 and pos < width - 1:
        a = row_a
        b = row_b
        ok, a = use(pos, a)
        if ok:
            ok, a = use(pos + 1, a)
        if ok:
            ok, b = use(pos, b)
        if ok:
            result += search(rows_left, a, b, row_c, width, cache)

    if rows_left >= 2 and pos < width - 1:
        a = row_a
        b = row_b
        ok, a = use(pos, a)
        if ok:
            ok, a = use(pos + 1, a)
        if ok:
            ok, b = use(pos + 1, b)
        if ok:
            result += search(rows_left, a, b, row_c, width, cache)

    if rows_left >= 2 and pos < width - 1:
        a = row_a
        b = row_b
        ok, a = use(pos, a)
        if ok:
            ok, b = use(pos, b)
        if ok:
            ok, b = use(pos + 1, b)
        if ok:
            result += search(rows_left, a, b, row_c, width, cache)

    if rows_left >= 2 and 0 < pos < width:
        a = row_a
        b = row_b
        ok, a = use(pos, a)
        if ok:
            ok, b = use(pos - 1, b)
        if ok:
            ok, b = use(pos, b)
        if ok:
            result += search(rows_left, a, b, row_c, width, cache)

    if rows_left >= 3 and pos < width:
        a = row_a
        b = row_b
        c = row_c
        ok, a = use(pos, a)
        if ok:
            ok, b = use(pos, b)
        if ok:
            ok, c = use(pos, c)
        if ok:
            result += search(rows_left, a, b, c, width, cache)

    if rows_left >= 1 and pos < width - 2:
        a = row_a
        ok, a = use(pos, a)
        if ok:
            ok, a = use(pos + 1, a)
        if ok:
            ok, a = use(pos + 2, a)
        if ok:
            result += search(rows_left, a, row_b, row_c, width, cache)

    cache[hash_value] = result
    return result


def solve(width: int, height: int) -> int:
    if width > height:
        width, height = height, width

    cache: dict[int, int] = {}
    return search(height, 0, 0, 0, width, cache)


def main() -> None:
    assert solve(2, 9) == 41
    print(solve(9, 12))


if __name__ == "__main__":
    main()
