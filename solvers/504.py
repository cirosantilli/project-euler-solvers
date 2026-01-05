#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0504.cpp"""
import math

points_on_edge = []


def gcd(a, b):
    while a != 0:
        a, b = b % a, a
    return b


def count_lattice_points(a, b, c, d):
    rectangle = (a + c) * (b + d)
    inside = rectangle // 2
    boundary = (
        points_on_edge[a][b]
        + points_on_edge[b][c]
        + points_on_edge[c][d]
        + points_on_edge[a][d]
    )
    boundary -= 4
    return inside - (boundary // 2) - 1


def solve(limit=100):
    global points_on_edge
    points_on_edge = [[0] * (limit + 1) for _ in range(limit + 1)]
    for a in range(1, limit + 1):
        for b in range(1, limit + 1):
            value = gcd(a, b)
            points_on_edge[a][b] = value
            points_on_edge[b][a] = value

    max_points = count_lattice_points(limit, limit, limit, limit)
    is_square = [0] * (max_points + 1)
    for i in range(1, int(math.isqrt(max_points)) + 1):
        is_square[i * i] = 1

    count = 0
    for a in range(1, limit + 1):
        for b in range(1, limit + 1):
            for c in range(1, limit + 1):
                for d in range(1, limit + 1):
                    if is_square[count_lattice_points(a, b, c, d)]:
                        count += 1

    return count


def main():
    assert solve(4) == 42
    print(solve())


if __name__ == "__main__":
    main()
