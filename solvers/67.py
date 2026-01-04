from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List


def parse_triangle(text: str) -> List[List[int]]:
    rows: List[List[int]] = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append([int(x) for x in line.split()])
    return rows


def max_path_sum(triangle: List[List[int]]) -> int:
    if not triangle:
        return 0
    # Bottom-up DP: dp[j] holds best sum from current position to bottom.
    dp = triangle[-1][:]  # copy last row
    for i in range(len(triangle) - 2, -1, -1):
        row = triangle[i]
        for j in range(len(row)):
            dp[j] = row[j] + max(dp[j], dp[j + 1])
    return dp[0]


def read_triangle_file() -> str:
    candidates = [
        Path("resources/documents/0067_triangle.txt"),
        Path("0067_triangle.txt"),
        Path("triangle.txt"),
        Path("p067_triangle.txt"),
    ]
    for p in candidates:
        if p.exists():
            return p.read_text(encoding="utf-8")
    raise FileNotFoundError(
        "Could not find the triangle input file. Tried: "
        + ", ".join(str(p) for p in candidates)
    )


def main() -> None:
    # Sample from the statement
    sample = """\
    3
    7 4
    2 4 6
    8 5 9 3
    """
    assert max_path_sum(parse_triangle(sample)) == 23

    text = read_triangle_file()
    tri = parse_triangle(text)
    ans = max_path_sum(tri)

    # Project Euler #67 known answer (helps catch file/parse issues)

    print(ans)


if __name__ == "__main__":
    main()
