#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0150.cpp"""


def lcg() -> int:
    lcg.seed = (615949 * lcg.seed + 797807) % (1 << 20)
    return lcg.seed - (1 << 19)


lcg.seed = 0


def build_triangle(size: int) -> list[list[int]]:
    triangle = []
    for y in range(size):
        row = []
        for _ in range(y + 1):
            row.append(lcg())
        triangle.append(row)
    return triangle


def solve(size: int) -> int:
    triangle = build_triangle(size)

    sums = []
    for y in range(size):
        row_sum = 0
        row = []
        for x in range(y + 1):
            row_sum += triangle[y][x]
            row.append(row_sum)
        sums.append(row)

    result = triangle[0][0]

    for y in range(size):
        for x in range(y + 1):
            total = triangle[y][x]
            if result > total:
                result = total

            max_len = size - y
            for current in range(1, max_len):
                row_sum = sums[y + current][x + current]
                if x > 0:
                    row_sum -= sums[y + current][x - 1]
                total += row_sum
                if result > total:
                    result = total

    return result


def main() -> None:
    lcg.seed = 0
    first_values = [lcg(), lcg(), lcg()]
    assert first_values == [273519, -153582, 450905]

    lcg.seed = 0
    print(solve(1000))


if __name__ == "__main__":
    main()
