#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0125.cpp"""


def is_palindrome(x: int) -> bool:
    reduced = x // 10
    reverse = x % 10
    if reverse == 0:
        return False

    while reduced > 0:
        reverse = reverse * 10 + reduced % 10
        reduced //= 10

    return reverse == x


def solve(limit: int, stride: int) -> int:
    solutions = set()
    first = 1
    while 2 * first * first < limit:
        next_val = first + stride
        current = first * first + next_val * next_val
        while current < limit:
            if is_palindrome(current):
                solutions.add(current)
            next_val += stride
            current += next_val * next_val
        first += 1
    return sum(solutions)


def main() -> None:
    assert solve(1000, 1) == 4164
    print(solve(100000000, 1))


if __name__ == "__main__":
    main()
