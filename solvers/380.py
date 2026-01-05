#!/usr/bin/env python3
"""
Project Euler 380: Amazing Mazes!

An m×n "perfect maze" (exactly one path between squares) is exactly a spanning
tree of the m×n grid graph. Therefore C(m,n) is the number of spanning trees of
P_m × P_n.

We compute C(100,500) in scientific notation (5 significant digits).
No external libraries are used.
"""

import math


# ---------- Exact (small) spanning tree counts via Matrix-Tree + Bareiss ----------


def _laplacian_minor(m: int, n: int, drop: int = 0):
    """Return the (mn-1)x(mn-1) Laplacian minor of the m×n grid graph with vertex `drop` removed."""
    N = m * n
    if N <= 1:
        return []

    size = N - 1
    A = [[0] * size for _ in range(size)]

    def idx(u: int) -> int:
        # Map original vertex index to minor index (skip `drop`)
        return u - 1 if u > drop else u

    def add_edge(u: int, v: int):
        # Add an undirected edge u—v into the Laplacian minor.
        # If one endpoint is dropped, only the remaining endpoint's degree increases.
        if u == drop and v == drop:
            return
        if u == drop:
            vv = idx(v)
            A[vv][vv] += 1
            return
        if v == drop:
            uu = idx(u)
            A[uu][uu] += 1
            return

        uu = idx(u)
        vv = idx(v)
        A[uu][uu] += 1
        A[vv][vv] += 1
        A[uu][vv] -= 1
        A[vv][uu] -= 1

    for r in range(m):
        for c in range(n):
            u = r * n + c
            if r + 1 < m:
                add_edge(u, (r + 1) * n + c)
            if c + 1 < n:
                add_edge(u, r * n + (c + 1))

    return A


def _det_bareiss(mat):
    """
    Fraction-free determinant (Bareiss algorithm), exact for integer matrices.

    For the small test cases in this problem, this is fast and avoids any
    floating-point issues.
    """
    n = len(mat)
    if n == 0:
        return 1
    A = [row[:] for row in mat]
    sign = 1
    prev = 1

    for k in range(n - 1):
        # Ensure a non-zero pivot at A[k][k] using row/column swaps if needed.
        if A[k][k] == 0:
            pivot_row = None
            for i in range(k + 1, n):
                if A[i][k] != 0:
                    pivot_row = i
                    break
            if pivot_row is not None:
                A[k], A[pivot_row] = A[pivot_row], A[k]
                sign *= -1
            else:
                pivot_col = None
                for j in range(k + 1, n):
                    if A[k][j] != 0:
                        pivot_col = j
                        break
                if pivot_col is None:
                    return 0
                for r in range(n):
                    A[r][k], A[r][pivot_col] = A[r][pivot_col], A[r][k]
                sign *= -1

        pivot = A[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = A[i][j] * pivot - A[i][k] * A[k][j]
                if k > 0:
                    A[i][j] //= prev
            A[i][k] = 0

        for j in range(k + 1, n):
            A[k][j] = 0

        prev = pivot

    return sign * A[n - 1][n - 1]


def spanning_trees_exact(m: int, n: int) -> int:
    """Exact number of spanning trees of the m×n grid graph (only feasible for small grids)."""
    if m * n == 1:
        return 1
    minor = _laplacian_minor(m, n, drop=0)
    return _det_bareiss(minor)


# ---------- Fast large-grid computation via Laplacian eigenvalues (log domain) ----------


def log10_spanning_trees(m: int, n: int) -> float:
    """
    Return log10(C(m,n)) for an m×n grid.

    For P_m × P_n, Laplacian eigenvalues are:
        λ_{i,j} = (2 - 2 cos(iπ/m)) + (2 - 2 cos(jπ/n))
               = 4 - 2 cos(iπ/m) - 2 cos(jπ/n),
    for i=0..m-1, j=0..n-1.
    The Matrix-Tree theorem gives:
        C(m,n) = (1/(mn)) * Π_{(i,j)≠(0,0)} λ_{i,j}.
    We sum log10(λ_{i,j}) and subtract log10(mn).
    """
    if m * n == 1:
        return 0.0

    pi = math.pi
    a = [2.0 * math.cos(pi * i / m) for i in range(m)]
    b = [2.0 * math.cos(pi * j / n) for j in range(n)]

    # Kahan summation for numerical stability
    total = -math.log10(m * n)
    c = 0.0
    for i in range(m):
        ai = a[i]
        for j in range(n):
            if i == 0 and j == 0:
                continue
            lam = 4.0 - ai - b[j]
            y = math.log10(lam) - c
            t = total + y
            c = (t - total) - y
            total = t
    return total


def format_sci_from_log10(log10x: float, sig: int = 5) -> str:
    """Format 10**log10x into scientific notation with `sig` significant digits."""
    exp = int(math.floor(log10x))
    frac = log10x - exp
    mant = 10.0**frac  # mantissa in [1, 10)

    decimals = sig - 1
    mant_rounded = round(mant, decimals)
    if mant_rounded >= 10.0:
        mant_rounded /= 10.0
        exp += 1
    return f"{mant_rounded:.{decimals}f}e{exp}"


def solve() -> str:
    # Tests from the problem statement
    assert spanning_trees_exact(1, 1) == 1
    assert spanning_trees_exact(2, 2) == 4
    assert spanning_trees_exact(3, 4) == 2415
    assert format_sci_from_log10(log10_spanning_trees(9, 12)) == "2.5720e46"

    # Required answer
    return format_sci_from_log10(log10_spanning_trees(100, 500))


if __name__ == "__main__":
    print(solve())
