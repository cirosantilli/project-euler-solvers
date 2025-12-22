from __future__ import annotations

import os
import sys
from typing import List


def min_path_sum(matrix: List[List[int]]) -> int:
    n = len(matrix)
    assert n > 0
    m = len(matrix[0])
    assert all(len(row) == m for row in matrix)

    dp = [0] * m
    dp[0] = matrix[0][0]

    # first row: only can come from left
    for j in range(1, m):
        dp[j] = dp[j - 1] + matrix[0][j]

    # remaining rows
    for i in range(1, n):
        # first col: only can come from top
        dp[0] = dp[0] + matrix[i][0]
        for j in range(1, m):
            dp[j] = matrix[i][j] + min(dp[j], dp[j - 1])
    return dp[-1]


def parse_matrix_from_text(text: str) -> List[List[int]]:
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    return [list(map(int, line.split(","))) for line in lines]


def read_matrix() -> List[List[int]]:
    with open("0081_matrix.txt", "r", encoding="utf-8") as f:
        return parse_matrix_from_text(f.read())


def _tests() -> None:
    sample = [
        [131, 673, 234, 103, 18],
        [201, 96, 342, 965, 150],
        [630, 803, 746, 422, 111],
        [537, 699, 497, 121, 956],
        [805, 732, 524, 37, 331],
    ]
    assert min_path_sum(sample) == 2427


def main() -> None:
    _tests()
    matrix = read_matrix()
    ans = min_path_sum(matrix)
    print(ans)


if __name__ == "__main__":
    main()
