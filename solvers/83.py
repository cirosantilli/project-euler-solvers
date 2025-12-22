from __future__ import annotations

from dataclasses import dataclass
import heapq
from pathlib import Path
from typing import List, Tuple


def parse_matrix_from_text(text: str) -> List[List[int]]:
    lines = [ln.strip() for ln in text.strip().splitlines() if ln.strip()]
    return [list(map(int, ln.split(","))) for ln in lines]


def load_matrix_file() -> List[List[int]]:
    """
    Tries a few common locations/names for the Project Euler 83 matrix file.
    """
    candidates = [
        Path("matrix.txt"),
        Path("0083_matrix.txt"),
        Path("p083_matrix.txt"),
        Path("resources") / "documents" / "0083_matrix.txt",
    ]
    for p in candidates:
        if p.exists():
            return parse_matrix_from_text(p.read_text(encoding="utf-8"))
    raise FileNotFoundError(
        "Could not find matrix file. Tried: "
        + ", ".join(str(p) for p in candidates)
        + ". Place the file as matrix.txt (CSV rows)."
    )


def dijkstra_min_path_sum(mat: List[List[int]]) -> int:
    n = len(mat)
    m = len(mat[0])
    total = n * m

    def idx(r: int, c: int) -> int:
        return r * m + c

    INF = 10**30
    dist = [INF] * total
    start = idx(0, 0)
    goal = idx(n - 1, m - 1)

    dist[start] = mat[0][0]
    heap: List[Tuple[int, int]] = [(mat[0][0], start)]

    visited = [False] * total

    while heap:
        d, u = heapq.heappop(heap)
        if visited[u]:
            continue
        visited[u] = True
        if u == goal:
            return d

        r, c = divmod(u, m)
        # 4-neighbors
        if r > 0:
            v = idx(r - 1, c)
            nd = d + mat[r - 1][c]
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
        if r + 1 < n:
            v = idx(r + 1, c)
            nd = d + mat[r + 1][c]
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
        if c > 0:
            v = idx(r, c - 1)
            nd = d + mat[r][c - 1]
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))
        if c + 1 < m:
            v = idx(r, c + 1)
            nd = d + mat[r][c + 1]
            if nd < dist[v]:
                dist[v] = nd
                heapq.heappush(heap, (nd, v))

    raise RuntimeError("No path found (unexpected for a grid).")


def _test_sample() -> None:
    sample = """
    131,673,234,103,18
    201,96,342,965,150
    630,803,746,422,111
    537,699,497,121,956
    805,732,524,37,331
    """
    mat = parse_matrix_from_text(sample)
    assert dijkstra_min_path_sum(mat) == 2297


def main() -> None:
    _test_sample()
    mat = load_matrix_file()
    ans = dijkstra_min_path_sum(mat)
    print(ans)


if __name__ == "__main__":
    main()
