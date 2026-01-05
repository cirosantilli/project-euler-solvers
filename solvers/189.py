#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0189.cpp"""


def get_id(row: int, triangles: list[int], num_colors: int) -> int:
    first = row * row
    width = 2 * row + 1

    result = row
    for i in range(first + 2, first + width, 2):
        diff = triangles[i - 2] - triangles[i]
        if diff < 0:
            diff += num_colors
        result = result * num_colors + diff

    reverse = row
    i = first + width - 1
    while i >= first + 2:
        diff = triangles[i - 2] - triangles[i]
        if diff < 0:
            diff += num_colors
        reverse = reverse * num_colors + diff
        i -= 2

    return reverse if result > reverse else result


def search(
    row: int,
    column: int,
    height: int,
    num_colors: int,
    triangles: list[int],
    cache: dict,
) -> int:
    first = row * row
    index = first + column
    width = 2 * row + 1

    next_row = row
    next_column = column + 1
    if next_column == width:
        next_row += 1
        next_column = 0

    prev_id = 0
    if column == 0:
        if row == height:
            return 1
        if row == 0:
            cache.clear()
        else:
            prev_id = get_id(row - 1, triangles, num_colors)
            if prev_id in cache:
                return cache[prev_id]

    result = 0
    if column % 2 == 0:
        for color in range(1, num_colors + 1):
            if column > 0 and triangles[index - 1] == color:
                continue
            triangles[index] = color
            result += search(
                next_row, next_column, height, num_colors, triangles, cache
            )
    else:
        for color in range(1, num_colors + 1):
            if triangles[index - 1] == color or triangles[index - 2 * row] == color:
                continue
            triangles[index] = color
            result += search(
                next_row, next_column, height, num_colors, triangles, cache
            )

    if column == 0 and row > 0:
        cache[prev_id] = result

    return result


def solve(height: int, num_colors: int) -> int:
    triangles = [0] * (height * height)
    cache: dict[int, int] = {}
    return search(0, 0, height, num_colors, triangles, cache)


if __name__ == "__main__":
    print(solve(8, 3))
