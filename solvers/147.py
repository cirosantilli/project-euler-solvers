#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0147.cpp"""
MODULO = 1000000007


def grid(width: int, height: int) -> int:
    return (width * (width + 1) // 2) * (height * (height + 1) // 2)


def diagonal(width: int, height: int, cache) -> int:
    key = (width, height)
    if key in cache:
        return cache[key]

    a, b = width, height
    if a < b:
        a, b = b, a

    count = 0
    for i in range(a):
        for j in range(b):
            for parity in (0, 1):
                start_x = 2 * i + 1 + parity
                start_y = 2 * j + 2 - parity

                stop = False
                max_height = 999999999
                current_width = 0
                while not stop:
                    current_x = start_x + current_width
                    current_y = start_y - current_width
                    if current_y <= 0:
                        break

                    current_height = 0
                    while current_height < max_height:
                        end_x = current_x + current_height
                        end_y = current_y + current_height
                        if end_x >= 2 * a or end_y >= 2 * b:
                            if max_height > current_height:
                                max_height = current_height
                            stop = current_height == 0
                            break

                        count += 1
                        current_height += 1

                    current_width += 1

    cache[key] = count
    return count


def count_grid(width: int, height: int, cache) -> int:
    return grid(width, height) + diagonal(width, height, cache)


def solve(max_width: int, max_height: int) -> int:
    sum_upright = 0
    sum_diagonal = 0
    cache: dict[tuple[int, int], int] = {}
    for width in range(1, max_width + 1):
        for height in range(1, max_height + 1):
            sum_upright += grid(width, height)
            sum_diagonal += diagonal(width, height, cache)
    return sum_upright + sum_diagonal


def main() -> None:
    cache: dict[tuple[int, int], int] = {}
    assert count_grid(3, 2, cache) == 37
    assert solve(3, 2) == 72
    print(solve(47, 43))


if __name__ == "__main__":
    main()
