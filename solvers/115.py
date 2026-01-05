#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0115.cpp"""
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


def fill_count(total_length: int, min_block_length: int) -> int:
    memo = [UNKNOWN] * (total_length + 1)
    return count(total_length, min_block_length, memo)


def least_length_exceeding(min_block_length: int, limit: int) -> int:
    total_length = 1
    while True:
        combinations = fill_count(total_length, min_block_length)
        if combinations > limit:
            return total_length
        total_length += 1


def main() -> None:
    assert fill_count(29, 3) == 673135
    assert fill_count(30, 3) == 1089155
    assert fill_count(56, 10) == 880711
    assert fill_count(57, 10) == 1148904
    assert least_length_exceeding(3, 1000000) == 30
    assert least_length_exceeding(10, 1000000) == 57
    print(least_length_exceeding(50, 1000000))


if __name__ == "__main__":
    main()
