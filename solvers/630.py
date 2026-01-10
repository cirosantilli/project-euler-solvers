#!/usr/bin/env python3
"""
Project Euler 630: Crossed Lines

We generate 2500 pseudo-random points, form all unique infinite lines through
pairs of points, then compute:

S(L) = sum over lines of (# other lines crossing it).

Two distinct non-parallel lines always intersect once, while parallel lines
never intersect, so:

S(L) = M*(M-1) - sum_over_parallel_classes c*(c-1)

where M is the number of unique lines and c is the number of lines in each
parallel (same slope) class.

The main work is deduplicating lines built from point pairs.
We represent a line by a primitive normal (A,B) (gcd(A,B)=1 with fixed sign)
and offset D = A*x + B*y, which is constant on that line.
Parallel lines share (A,B); different lines of that slope have different D.

To reduce memory and speed up uniqueness checking, we pack (A,B,D) into a
single integer, sort all codes, and scan to count uniques and class sizes.
"""

from math import gcd


# Bit packing layout:
# normal_id = (A << B_BITS) | (B + B_OFFSET)   uses 11 + 12 = 23 bits
# code      = (normal_id << D_BITS) | (D + D_OFFSET) uses additional 23 bits
A_BITS = 11
B_BITS = 12
D_BITS = 23

B_OFFSET = 1999  # B in [-1999, 1999] -> [0, 3998]
D_OFFSET = 4_000_000  # D in about [-4e6, 4e6] -> [0, 8e6]


def generate_points(n: int):
    """Return the first n points (T_{2k-1}, T_{2k}) as a list of (x,y)."""
    s = 290797
    pts = []
    t = []

    # T_1 .. T_{2n}
    for _ in range(2 * n):
        s = (s * s) % 50515093
        t.append((s % 2000) - 1000)

    # Points: (T1,T2), (T3,T4), ...
    for k in range(n):
        pts.append((t[2 * k], t[2 * k + 1]))
    return pts


def _line_code(p1, p2):
    """
    Build a packed integer representing the unique line through p1 and p2.

    Line representation:
      - Reduce direction (dx,dy) by gcd to make it primitive.
      - Use primitive normal (A,B) = (dy, -dx), flip sign so that:
            A > 0  OR  (A == 0 AND B > 0)
      - Offset D = A*x + B*y

    Returns None if points are identical.
    """
    x1, y1 = p1
    x2, y2 = p2

    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return None

    g = gcd(abs(dx), abs(dy))
    dx //= g
    dy //= g

    # Primitive normal to the direction
    A = dy
    B = -dx

    # Fix sign to make (A,B) canonical
    if A < 0 or (A == 0 and B < 0):
        A = -A
        B = -B

    normal_id = (A << B_BITS) | (B + B_OFFSET)
    D = A * x1 + B * y1
    return (normal_id << D_BITS) | (D + D_OFFSET)


def calc_M_and_S(points):
    """
    Given a list of points, return (M, S) for the set of unique lines formed.

    We:
      1) Generate a packed code for each point pair.
      2) Sort all codes.
      3) Scan to count unique lines (M) and sizes of parallel classes (c).
    """
    n = len(points)
    codes = []
    append = codes.append
    for i in range(n - 1):
        pi = points[i]
        for j in range(i + 1, n):
            code = _line_code(pi, points[j])
            if code is not None:
                append(code)

    codes.sort()

    M = 0
    sum_parallel_pairs_x2 = 0  # will accumulate sum c*(c-1)
    prev_code = None
    prev_normal = None
    c = 0

    for code in codes:
        if code == prev_code:
            continue  # duplicate line from a different point pair

        M += 1
        normal = code >> D_BITS

        if normal != prev_normal:
            if prev_normal is not None:
                sum_parallel_pairs_x2 += c * (c - 1)
            prev_normal = normal
            c = 1
        else:
            c += 1

        prev_code = code

    if prev_normal is not None:
        sum_parallel_pairs_x2 += c * (c - 1)

    S = M * (M - 1) - sum_parallel_pairs_x2
    return M, S


def solve() -> int:
    points = generate_points(2500)

    # Asserts from the problem statement
    assert points[0] == (527, 144)
    assert points[1] == (-488, 732)
    assert points[2] == (-454, -947)

    M3, S3 = calc_M_and_S(points[:3])
    assert (M3, S3) == (3, 6)

    M100, S100 = calc_M_and_S(points[:100])
    assert (M100, S100) == (4948, 24477690)

    _, ans = calc_M_and_S(points)
    return ans


def main():
    print(solve())


if __name__ == "__main__":
    main()
