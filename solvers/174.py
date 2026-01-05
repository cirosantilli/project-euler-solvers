#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0174.cpp"""


def build_solutions(limit: int) -> list[int]:
    solutions = [0] * (limit + 1)

    outer = 3
    while True:
        total = 0
        inner = outer
        while inner >= 3:
            ring = 4 * (inner - 1)
            if total + ring > limit:
                break
            total += ring
            solutions[total] += 1
            inner -= 2

        if total == 0:
            break
        outer += 1
    return solutions


def count_up_to(limit: int, min_type: int, max_type: int) -> int:
    solutions = build_solutions(limit)
    return sum(1 for value in solutions if min_type <= value <= max_type)


def count_exact(limit: int, target: int) -> int:
    solutions = build_solutions(limit)
    return sum(1 for value in solutions if value == target)


def main() -> None:
    assert count_exact(1000000, 15) == 832
    print(count_up_to(1000000, 1, 10))


if __name__ == "__main__":
    main()
