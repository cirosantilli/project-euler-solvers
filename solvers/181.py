#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0181.cpp"""
MAX_BLACK = 160
MAX_WHITE = 160


def solve(max_black: int, max_white: int) -> int:
    previous = [[0] * (MAX_WHITE + 1) for _ in range(MAX_BLACK + 1)]
    current = [[0] * (MAX_WHITE + 1) for _ in range(MAX_BLACK + 1)]
    previous[0][0] = 1

    for use_black in range(max_black + 1):
        for use_white in range(max_white + 1):
            if use_black == 0 and use_white == 0:
                continue
            for i in range(max_black + 1):
                for j in range(max_white + 1):
                    total = 0
                    k = 0
                    while i >= k * use_black and j >= k * use_white:
                        total += previous[i - k * use_black][j - k * use_white]
                        k += 1
                    current[i][j] = total
            for i in range(max_black + 1):
                for j in range(max_white + 1):
                    previous[i][j] = current[i][j]

    return current[max_black][max_white]


if __name__ == "__main__":
    assert solve(3, 1) == 7
    print(solve(60, 40))
