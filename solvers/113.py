#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0113.cpp"""
MODULO = 1000000000000000000


def precompute(num_digits: int) -> list[int]:
    solutions = [0] * (num_digits + 1)

    increase = [1] * 10
    decrease = [1] * 10

    total = 9

    for i in range(1, num_digits):
        new_increase = [0] * 10
        new_decrease = [0] * 10

        prefix_sum = 0
        for current in range(10):
            prefix_sum = (prefix_sum + decrease[current]) % MODULO
            new_decrease[current] = prefix_sum

        suffix_sum = 0
        for current in range(9, -1, -1):
            suffix_sum = (suffix_sum + increase[current]) % MODULO
            new_increase[current] = suffix_sum

        total += sum(new_increase) + sum(new_decrease)
        total -= new_increase[0]
        total -= 10
        total %= MODULO

        solutions[i] = total
        increase = new_increase
        decrease = new_decrease

    return solutions


def solve(digits: int, solutions: list[int]) -> int:
    return solutions[digits - 1]


def main() -> None:
    solutions = precompute(100)
    assert solve(6, solutions) == 12951
    assert solve(10, solutions) == 277032
    print(solve(100, solutions))


if __name__ == "__main__":
    main()
