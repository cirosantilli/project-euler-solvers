#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0117.cpp"""
UNKNOWN = -1


def count(space: int, memo) -> int:
    if space == 0:
        return 1
    if memo[space] != UNKNOWN:
        return memo[space]

    result = 0
    for block in range(1, 5):
        if block > space:
            break
        result += count(space - block, memo)

    memo[space] = result
    return result


def solve(limit: int) -> int:
    memo = [UNKNOWN] * (limit + 1)
    return count(limit, memo)


def main() -> None:
    assert solve(5) == 15
    print(solve(50))


if __name__ == "__main__":
    main()
