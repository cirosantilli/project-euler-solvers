#!/usr/bin/env python3
"""
Project Euler 594: Rhombus Tilings

Let O_{a,b} be the equal-angled convex octagon whose edges alternate between
length a and b. We must compute t(O_{4,2}), the number of tilings by unit squares
and unit 45° rhombi, counting distinct rotations/reflections as distinct.

This implementation uses a determinantal enumeration formula (via the
square-grid / de Bruijn representation and the Lindström–Gessel–Viennot theorem)
for the more general centro-symmetric octagon with side lengths (a,b,c,d,a,b,c,d).
For O_{a,b} we have (a,b,c,d) = (a,b,a,b).
"""

from __future__ import annotations


def gen_monotone_matrices(rows: int, cols: int, max_value: int):
    """
    Generate all integer matrices M[rows][cols] with entries in [0..max_value]
    that are nondecreasing to the right and down:
        M[i][j] >= M[i-1][j] and M[i][j] >= M[i][j-1].
    Returned as tuples of tuples (immutable, hashable).
    """
    m = [[0] * cols for _ in range(rows)]

    def rec(pos: int):
        if pos == rows * cols:
            yield tuple(tuple(r) for r in m)
            return
        i, j = divmod(pos, cols)
        lo = 0
        if i > 0:
            lo = max(lo, m[i - 1][j])
        if j > 0:
            lo = max(lo, m[i][j - 1])
        for v in range(lo, max_value + 1):
            m[i][j] = v
            yield from rec(pos + 1)

    yield from rec(0)


_BINOM_CACHE: dict[tuple[int, int], int] = {}


def binom(n: int, k: int) -> int:
    """Binomial coefficient C(n,k) with the convention C(n,k)=0 for invalid k."""
    if n < 0 or k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    key = (n, k)
    if key in _BINOM_CACHE:
        return _BINOM_CACHE[key]

    # Multiplicative formula; exact division at each step.
    res = 1
    # res *= (n-k+1)/1 * (n-k+2)/2 * ... * n/k
    for i in range(1, k + 1):
        res = res * (n - k + i) // i

    _BINOM_CACHE[key] = res
    return res


def det_bareiss(mat: list[list[int]]) -> int:
    """
    Exact determinant of an integer matrix using the Bareiss fraction-free algorithm.
    Runs in O(n^3) and keeps intermediate values integral.
    """
    n = len(mat)
    if n == 0:
        return 1
    if n == 1:
        return mat[0][0]
    # Copy
    a = [row[:] for row in mat]
    sign = 1
    prev = 1

    for k in range(n - 1):
        if a[k][k] == 0:
            swap = None
            for i in range(k + 1, n):
                if a[i][k] != 0:
                    swap = i
                    break
            if swap is None:
                return 0
            a[k], a[swap] = a[swap], a[k]
            sign = -sign

        pivot = a[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                a[i][j] = (a[i][j] * pivot - a[i][k] * a[k][j]) // prev
        prev = pivot
        for i in range(k + 1, n):
            a[i][k] = 0

    return sign * a[n - 1][n - 1]


def count_tilings_octagon(a: int, b: int, c: int, d: int) -> int:
    """
    Count tilings of the centro-symmetric equal-angled octagon with side lengths
    (a,b,c,d,a,b,c,d) using unit squares and 45° rhombi.

    Implements Theorem 1 / eq. (12) of the determinantal formula:
        T_{a,b,c,d} = sum_{(x,y) in X x Y}  Π_u det(M^(u)(x,y)) * Π_v det(P^(v)(x,y))

    Where X and Y are monotone integer arrays (x_{k,l}) and (y_{k,l}).
    """
    # X: b x d monotone matrices with values in [0..a].
    X = list(gen_monotone_matrices(b, d, a))

    # Y: b x d arrays satisfying a "reversed" monotonicity.
    # If we reverse the row order, the constraint becomes standard monotone.
    Y = []
    for y_rev in gen_monotone_matrices(b, d, c):
        # Reverse rows back: y[k][l] = y_rev[b-1-k][l]
        y = tuple(tuple(y_rev[b - 1 - i][j] for j in range(d)) for i in range(b))
        Y.append(y)

    total = 0

    for x in X:
        # Build x_full with boundary conventions (9)
        x_full = [[0] * (d + 2) for _ in range(b + 2)]
        for k in range(1, b + 1):
            for l in range(1, d + 1):
                x_full[k][l] = x[k - 1][l - 1]
        for k in range(1, b + 1):
            x_full[k][0] = 0
            x_full[k][d + 1] = a
        for l in range(0, d + 2):
            x_full[0][l] = 0
            x_full[b + 1][l] = a

        for y in Y:
            # Build y_full with boundary conventions (9)
            y_full = [[0] * (d + 2) for _ in range(b + 2)]
            for k in range(1, b + 1):
                for l in range(1, d + 1):
                    y_full[k][l] = y[k - 1][l - 1]
            for k in range(1, b + 1):
                y_full[k][0] = 0
                y_full[k][d + 1] = c
            for l in range(0, d + 2):
                y_full[0][l] = c
                y_full[b + 1][l] = 0

            prod = 1

            # Product over u = 1..d+1 of det(M^(u))
            for u in range(1, d + 2):
                M = []
                for i in range(1, b + 1):
                    row = []
                    for j in range(1, b + 1):
                        A = (x_full[j][u] - x_full[i][u - 1]) + (
                            y_full[j][u] - y_full[i][u - 1]
                        )
                        B = (x_full[j][u] - x_full[i][u - 1]) + (j - i)
                        row.append(binom(A, B))
                    M.append(row)
                detM = det_bareiss(M)
                prod *= detM
                if prod == 0:
                    break
            if prod == 0:
                continue

            # Product over v = 1..b+1 of det(P^(v))
            for v in range(1, b + 2):
                P = []
                for i in range(1, d + 1):
                    row = []
                    for j in range(1, d + 1):
                        A = (x_full[v][j] - x_full[v - 1][i]) + (
                            y_full[v - 1][i] - y_full[v][j]
                        )
                        B = (x_full[v][j] - x_full[v - 1][i]) + (j - i)
                        row.append(binom(A, B))
                    P.append(row)
                detP = det_bareiss(P)
                prod *= detP
                if prod == 0:
                    break

            total += prod

    return total


def t_O_ab(a: int, b: int) -> int:
    """The Project Euler polygon O_{a,b} corresponds to (a,b,c,d)=(a,b,a,b)."""
    return count_tilings_octagon(a, b, a, b)


def main() -> None:
    # Test values from the problem statement
    assert t_O_ab(1, 1) == 8
    assert t_O_ab(2, 1) == 76
    assert t_O_ab(3, 2) == 456572

    print(t_O_ab(4, 2))


if __name__ == "__main__":
    main()
