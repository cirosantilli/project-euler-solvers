#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0135.cpp"""


def build_solutions(limit: int) -> list[int]:
    solutions = [0] * (limit + 1)
    for a in range(1, limit + 1):
        b = (a + 3) // 4
        while b < a:
            current = a * (4 * b - a)
            if current > limit:
                break
            solutions[current] += 1
            b += 1
    return solutions


def count_with_exact(limit: int, target: int, solutions: list[int]) -> int:
    return sum(1 for value in solutions[1:limit] if value == target)


def main() -> None:
    limit = 1000000
    solutions = build_solutions(limit)
    assert solutions[27] == 2
    assert solutions[1155] == 10
    print(count_with_exact(limit, 10, solutions))


if __name__ == "__main__":
    main()
