#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0138.cpp"""


def precompute(max_precompute: int) -> list[int]:
    solutions = []
    current = 17
    solutions.append(current)
    total = current

    previous = 1
    for _ in range(2, max_precompute + 1):
        next_val = current * 18 - previous
        previous = current
        current = next_val

        total += current
        solutions.append(total)
    return solutions


def solve(nth: int, solutions: list[int]) -> int:
    return solutions[nth - 1]


def main() -> None:
    solutions = precompute(12)
    assert solve(1, solutions) == 17
    assert solve(2, solutions) == 322
    print(solve(12, solutions))


if __name__ == "__main__":
    main()
