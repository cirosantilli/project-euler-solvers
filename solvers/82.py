from __future__ import annotations

import sys
from typing import List


def minimal_path_sum_three_ways(mat: List[List[int]]) -> int:
    """
    Project Euler 82:
    Start in any cell in left column, end in any cell in right column.
    Allowed moves: up, down, right.
    """
    n = len(mat)
    assert n > 0 and all(len(row) == n for row in mat), "Matrix must be square"

    # dp[i] = minimal cost to reach row i at current column
    dp = [mat[i][0] for i in range(n)]

    for j in range(1, n):
        # Step 1: move right from previous column
        temp = [dp[i] + mat[i][j] for i in range(n)]

        # Step 2: relax downward moves within this column
        for i in range(1, n):
            cand = temp[i - 1] + mat[i][j]
            if cand < temp[i]:
                temp[i] = cand

        # Step 3: relax upward moves within this column
        for i in range(n - 2, -1, -1):
            cand = temp[i + 1] + mat[i][j]
            if cand < temp[i]:
                temp[i] = cand

        dp = temp

    return min(dp)


def parse_matrix_from_text(text: str) -> List[List[int]]:
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    return [list(map(int, ln.split(","))) for ln in lines]


def read_input_matrix() -> List[List[int]]:
    with open("0082_matrix.txt", "r", encoding="utf-8") as f:
        return parse_matrix_from_text(f.read())


def _self_test() -> None:
    sample = [
        [131, 673, 234, 103, 18],
        [201, 96, 342, 965, 150],
        [630, 803, 746, 422, 111],
        [537, 699, 497, 121, 956],
        [805, 732, 524, 37, 331],
    ]
    assert minimal_path_sum_three_ways(sample) == 994


def main() -> None:
    _self_test()
    mat = read_input_matrix()
    ans = minimal_path_sum_three_ways(mat)
    print(ans)


if __name__ == "__main__":
    main()
