#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0213.cpp"""


def make_grid(width: int, height: int, initial: float):
    return [[initial for _ in range(height)] for _ in range(width)]


def solve(width: int, height: int, rounds: int) -> float:
    empty = make_grid(width, height, 1.0)

    mirror_x = False
    mirror_y = False
    max_x = width
    max_y = height

    if width % 2 == 0:
        mirror_x = True
        max_x = width // 2
    if height % 2 == 0:
        mirror_y = True
        max_y = height // 2

    for start_x in range(max_x):
        for start_y in range(max_y):
            current = make_grid(width, height, 0.0)
            current[start_x][start_y] = 1.0

            for _ in range(rounds):
                next_grid = make_grid(width, height, 0.0)
                for x in range(width):
                    for y in range(height):
                        if current[x][y] == 0.0:
                            continue

                        directions = 4
                        if x == 0 or x == width - 1:
                            directions -= 1
                        if y == 0 or y == height - 1:
                            directions -= 1

                        probability = current[x][y] / directions
                        if x > 0:
                            next_grid[x - 1][y] += probability
                        if x < width - 1:
                            next_grid[x + 1][y] += probability
                        if y > 0:
                            next_grid[x][y - 1] += probability
                        if y < height - 1:
                            next_grid[x][y + 1] += probability

                current = next_grid

            for x in range(width):
                for y in range(height):
                    empty[x][y] *= 1 - current[x][y]

                    if mirror_x:
                        empty[x][y] *= 1 - current[width - 1 - x][y]
                    if mirror_y:
                        empty[x][y] *= 1 - current[x][height - 1 - y]
                    if mirror_x and mirror_y:
                        empty[x][y] *= 1 - current[width - 1 - x][height - 1 - y]

    result = 0.0
    for x in range(width):
        for y in range(height):
            result += empty[x][y]

    return result


if __name__ == "__main__":
    print(f"{solve(30, 30, 50):.6f}")
