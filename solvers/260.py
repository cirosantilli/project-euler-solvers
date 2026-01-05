#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0260.cpp"""
max_pile_size = 1000


def idx(a, b):
    return a * (max_pile_size + 1) + b


def solve(limit: int) -> int:
    global max_pile_size
    max_pile_size = limit

    won = False
    lost = True

    size = (max_pile_size + 1) * (max_pile_size + 1)
    one = [won] * size
    two = [won] * size
    all_piles = [won] * size

    count = 0

    for x in range(max_pile_size + 1):
        for y in range(x, max_pile_size + 1):
            if one[idx(x, y)] == lost:
                continue
            for z in range(y, max_pile_size + 1):
                if (
                    one[idx(y, z)] == lost
                    or one[idx(x, z)] == lost
                    or one[idx(x, y)] == lost
                ):
                    continue

                if (
                    two[idx(y - x, z)] == lost
                    or two[idx(z - y, x)] == lost
                    or two[idx(z - x, y)] == lost
                ):
                    continue

                if all_piles[idx(y - x, z - x)] == lost:
                    continue

                count += x + y + z

                one[idx(y, z)] = lost
                one[idx(x, z)] = lost
                one[idx(x, y)] = lost

                two[idx(y - x, z)] = lost
                two[idx(z - y, x)] = lost
                two[idx(z - x, y)] = lost

                all_piles[idx(y - x, z - x)] = lost

    return count


if __name__ == "__main__":
    assert solve(100) == 173895
    print(solve(1000))
