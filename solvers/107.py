from __future__ import annotations

import os
from typing import List, Tuple


Edge = Tuple[int, int, int]  # (weight, u, v)


class DSU:
    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x

    def union(self, a: int, b: int) -> bool:
        ra = self.find(a)
        rb = self.find(b)
        if ra == rb:
            return False
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
        return True


def parse_network_lines(lines: List[str]) -> Tuple[int, int, List[Edge]]:
    """
    Parse an adjacency matrix network where '-' means no edge and weights are integers.
    Returns: (n, total_weight, edges) where total_weight sums each undirected edge once.
    """
    matrix = [line.strip() for line in lines if line.strip()]
    n = len(matrix)
    edges: List[Edge] = []
    total = 0

    for i, line in enumerate(matrix):
        parts = [p.strip() for p in line.split(",")]
        if len(parts) != n:
            raise ValueError(f"Row {i} has {len(parts)} columns, expected {n}")
        for j in range(i + 1, n):
            v = parts[j]
            if v != "-":
                w = int(v)
                total += w
                edges.append((w, i, j))

    return n, total, edges


def mst_weight_kruskal(n: int, edges: List[Edge]) -> int:
    dsu = DSU(n)
    wsum = 0
    edges_sorted = sorted(edges)
    used = 0
    for w, u, v in edges_sorted:
        if dsu.union(u, v):
            wsum += w
            used += 1
            if used == n - 1:
                break
    if used != n - 1:
        raise ValueError("Graph is not connected; MST does not exist.")
    return wsum


def max_saving_from_lines(lines: List[str]) -> int:
    n, total, edges = parse_network_lines(lines)
    mst = mst_weight_kruskal(n, edges)
    return total - mst


def _test_example() -> None:
    # Example network from the statement (total weight 243, MST weight 93, saving 150)
    example_lines = [
        "-,16,12,21,-,-,-",
        "16,-,-,17,20,-,-",
        "12,-,-,28,-,31,-",
        "21,17,28,-,18,19,23",
        "-,20,-,18,-,-,11",
        "-,-,31,19,-,-,27",
        "-,-,-,23,11,27,-",
    ]
    n, total, edges = parse_network_lines(example_lines)
    assert n == 7
    assert total == 243
    assert mst_weight_kruskal(n, edges) == 93
    assert max_saving_from_lines(example_lines) == 150


def _read_network_file() -> List[str]:
    # Per prompt: use basename from the statement; also fall back to common Euler name.
    candidates = ["0107_network.txt", "network.txt"]
    for fn in candidates:
        if os.path.exists(fn):
            with open(fn, "r", encoding="utf-8") as f:
                return f.read().strip().splitlines()
    raise FileNotFoundError(f"Could not find any of: {candidates}")


def main() -> None:
    _test_example()

    lines = _read_network_file()
    saving = max_saving_from_lines(lines)
    print(saving)


if __name__ == "__main__":
    main()
