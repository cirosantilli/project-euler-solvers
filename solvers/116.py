#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0116.cpp"""


def choose(n: int, k: int) -> int:
    result = 1
    for inv_k in range(1, k + 1):
        result *= n
        result //= inv_k
        n -= 1
    return result


def count_color(total_length: int, block_length: int) -> int:
    total = 0
    max_blocks = total_length // block_length
    for colored in range(1, max_blocks + 1):
        black = total_length - colored * block_length
        tiles = black + colored
        total += choose(tiles, colored)
    return total


def solve(total_length: int) -> int:
    return sum(count_color(total_length, block) for block in range(2, 5))


def main() -> None:
    assert count_color(5, 2) == 7
    assert count_color(5, 3) == 3
    assert count_color(5, 4) == 2
    assert solve(5) == 12
    print(solve(50))


if __name__ == "__main__":
    main()
