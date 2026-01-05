#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0203.cpp"""


def is_squarefree(x: int, max_square: int) -> bool:
    for p in range(2, max_square + 1):
        if x % (p * p) == 0:
            return False
    return True


def solve(num_rows: int) -> int:
    squarefree = {1}

    current = [1]
    for row in range(1, num_rows):
        next_row = [1] * (len(current) + 1)
        for col in range(1, len(next_row) - 1):
            next_row[col] = current[col - 1] + current[col]

        for i in range(1, len(next_row) // 2 + 1):
            x = next_row[i]
            if is_squarefree(x, num_rows):
                squarefree.add(x)

        current = next_row

    total = sum(squarefree)
    return total


if __name__ == "__main__":
    assert solve(8) == 105
    print(solve(51))
