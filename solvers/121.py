#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0121.cpp"""


def solve(max_rounds: int) -> int:
    available_red = 1
    available_blue = 1
    possibilities = 1
    open_counts = [1]

    for round_num in range(1, max_rounds + 1):
        possibilities *= available_red + available_blue

        next_counts = [0] * (round_num + 1)
        for blue, count in enumerate(open_counts):
            if count == 0:
                continue
            next_counts[blue] += count * available_red
            next_counts[blue + 1] += count * available_blue

        open_counts = next_counts
        available_red += 1

    more_blue = 0
    for blue, count in enumerate(open_counts):
        red = max_rounds - blue
        if blue > red:
            more_blue += count

    return possibilities // more_blue


def main() -> None:
    assert solve(4) == 10
    print(solve(15))


if __name__ == "__main__":
    main()
