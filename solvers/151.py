#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0151.cpp"""
import sys


def evaluate(sheets: list[int]) -> float:
    num_sheets = sum(sheets)

    single = 0.0
    if num_sheets == 1:
        if sheets[-1] == 1:
            return 0.0
        if sheets[0] == 0:
            single = 1.0

    for i, count in enumerate(sheets):
        if count == 0:
            continue

        next_sheets = sheets[:]
        next_sheets[i] -= 1
        for j in range(i + 1, len(next_sheets)):
            next_sheets[j] += 1

        probability = count / num_sheets
        single += evaluate(next_sheets) * probability

    return single


def main() -> None:
    result = evaluate([1, 0, 0, 0, 0])
    sys.stdout.write(f"{result:.6f}")


if __name__ == "__main__":
    main()
