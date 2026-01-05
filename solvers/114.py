#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0114.cpp"""
UNKNOWN = -1


def count(space: int, min_block_length: int, memo) -> int:
    if space == 0:
        return 1
    if memo[space] != UNKNOWN:
        return memo[space]

    result = count(space - 1, min_block_length, memo)
    for block in range(min_block_length, space + 1):
        next_space = space - block
        if next_space > 0:
            next_space -= 1
        result += count(next_space, min_block_length, memo)

    memo[space] = result
    return result


def solve(total_length: int, min_block_length: int) -> int:
    memo = [UNKNOWN] * (total_length + 1)
    return count(total_length, min_block_length, memo)


def main() -> None:
    assert solve(7, 3) == 17
    print(solve(50, 3))


if __name__ == "__main__":
    main()
