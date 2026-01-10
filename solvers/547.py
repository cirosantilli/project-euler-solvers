#!/usr/bin/env python3
"""
Project Euler 547: Distance of Random Points Within Hollow Square Laminae

Computes S(40) rounded to four digits after the decimal point.

No external libraries are used.
"""

from __future__ import annotations

import math
from typing import List, Tuple


Segment = Tuple[
    int, int, float, float
]  # (start, end, slope m, intercept c) with weight = m*t + c


def _precompute_tables(max_n: int):
    """
    Precompute small lookup tables for fast rectangle integrals.

    Coordinates needed are integers in [-max_n, max_n].
    """
    size = 2 * max_n + 1
    off = max_n

    # A[x][y] = ∬_{[0..x]×[0..y]} sqrt(u^2+v^2) dv du  (oriented; x,y can be negative)
    A = [[0.0] * size for _ in range(size)]

    def A_pos(a: int, b: int) -> float:
        # a,b >= 0
        if a == 0 or b == 0:
            return 0.0
        r = math.hypot(a, b)
        # Correct closed-form:
        # ∬_{0..a,0..b} sqrt(x^2+y^2) dy dx
        return (
            2.0 * a * b * r + (a**3) * math.asinh(b / a) + (b**3) * math.asinh(a / b)
        ) / 6.0

    for x in range(-max_n, max_n + 1):
        sx = -1.0 if x < 0 else 1.0
        ax = abs(x)
        for y in range(-max_n, max_n + 1):
            if x == 0 or y == 0:
                A[x + off][y + off] = 0.0
            else:
                sy = -1.0 if y < 0 else 1.0
                A[x + off][y + off] = sx * sy * A_pos(ax, abs(y))

    # F3[a][y] = ∫_0^y (a^2 + t^2)^(3/2) dt   with a >= 0, y can be negative
    F3 = [[0.0] * size for _ in range(max_n + 1)]
    for a in range(0, max_n + 1):
        a2 = a * a
        a4 = a2 * a2
        for y in range(-max_n, max_n + 1):
            if a == 0:
                # ∫_0^y |t|^3 dt = y*|y|^3 / 4  (oriented)
                F3[a][y + off] = (y * (abs(y) ** 3)) / 4.0
            else:
                r = math.hypot(a, y)
                yy = y * y
                F3[a][y + off] = (
                    y * r * (2.0 * yy + 5.0 * a2) + 3.0 * a4 * math.asinh(y / a)
                ) / 8.0

    # P5[a][b] = (a^2 + b^2)^(5/2) for a,b >= 0
    P5 = [[0.0] * (max_n + 1) for _ in range(max_n + 1)]
    for a in range(max_n + 1):
        aa = a * a
        for b in range(max_n + 1):
            P5[a][b] = (aa + b * b) ** 2.5

    return A, F3, P5, off


def _overlap_segments(outer_len: int, inner_len: int, left: int) -> List[Segment]:
    """
    For outer interval [0, outer_len] and inner interval [left, left+inner_len] (nested),
    return segments over t = (outer_point - inner_point) where

      overlap_length(t) = m*t + c  (piecewise linear).

    Each segment is [start, end] with start < end and integer endpoints.
    """
    right = (
        outer_len - left - inner_len
    )  # distance from inner's right edge to outer's right edge
    segs: List[Segment] = []

    # Rising edge: t in [-(left+inner), -left], overlap = t + left + inner
    a0 = -(left + inner_len)
    a1 = -left
    if a0 != a1:
        segs.append((a0, a1, 1.0, float(left + inner_len)))

    # Plateau: t in [-left, right], overlap = inner_len
    b0 = -left
    b1 = right
    if b0 != b1:
        segs.append((b0, b1, 0.0, float(inner_len)))

    # Falling edge: t in [right, outer-left], overlap = outer-left - t
    c0 = right
    c1 = outer_len - left
    if c0 != c1:
        segs.append((c0, c1, -1.0, float(outer_len - left)))

    return segs


def _solve_S(n: int) -> float:
    """
    Compute S(n) as defined in the problem statement.
    """
    max_needed = n  # dx,dy ranges reach ±n when comparing an n×n rectangle with itself
    A, F3, P5, off = _precompute_tables(max_needed)

    # Fast rectangle basis integrals on [x0,x1]×[y0,y1] for r = sqrt(x^2+y^2)
    def I0(x0: int, x1: int, y0: int, y1: int) -> float:
        return (
            A[x1 + off][y1 + off]
            - A[x0 + off][y1 + off]
            - A[x1 + off][y0 + off]
            + A[x0 + off][y0 + off]
        )

    def Ix(x0: int, x1: int, y0: int, y1: int) -> float:
        # ∬ x*r
        a1 = abs(x1)
        a0 = abs(x0)
        return (
            (F3[a1][y1 + off] - F3[a1][y0 + off])
            - (F3[a0][y1 + off] - F3[a0][y0 + off])
        ) / 3.0

    def Iy(x0: int, x1: int, y0: int, y1: int) -> float:
        # symmetry (swap x and y)
        return Ix(y0, y1, x0, x1)

    def Ixy(x0: int, x1: int, y0: int, y1: int) -> float:
        # ∬ x*y*r
        ax1, ax0 = abs(x1), abs(x0)
        ay1, ay0 = abs(y1), abs(y0)
        return (P5[ax1][ay1] - P5[ax0][ay1] - P5[ax1][ay0] + P5[ax0][ay0]) / 15.0

    # Cross integral between outer rectangle [0..W]×[0..H] and a nested inner rectangle
    def cross_integral(
        outer_w: int, outer_h: int, inner_w: int, inner_h: int, left: int, bottom: int
    ) -> float:
        xsegs = _overlap_segments(outer_w, inner_w, left)
        ysegs = _overlap_segments(outer_h, inner_h, bottom)
        total = 0.0
        for x0, x1, mx, cx in xsegs:
            for y0, y1, my, cy in ysegs:
                i0 = I0(x0, x1, y0, y1)
                term = cx * cy * i0
                if mx:
                    term += mx * cy * Ix(x0, x1, y0, y1)
                if my:
                    term += cx * my * Iy(x0, x1, y0, y1)
                if mx and my:
                    term += mx * my * Ixy(x0, x1, y0, y1)
                total += term
        return total

    # I for full outer square (constant across all laminae of size n)
    I_outer = cross_integral(n, n, n, n, 0, 0)

    # I for holes (depends only on hole size, not position)
    I_hole = [[0.0] * (n) for _ in range(n)]
    for w in range(1, n - 1):
        for h in range(1, n - 1):
            I_hole[w][h] = cross_integral(w, h, w, h, 0, 0)

    # Precompute 1D overlap segments for each possible placement (saves list creation in inner loops)
    segx: List[List[List[Segment]]] = [[[] for _ in range(n + 1)] for _ in range(n + 1)]
    segy: List[List[List[Segment]]] = [[[] for _ in range(n + 1)] for _ in range(n + 1)]
    for w in range(1, n - 1):
        for left in range(0, n - w + 1):
            segx[w][left] = _overlap_segments(n, w, left)
    for h in range(1, n - 1):
        for bottom in range(0, n - h + 1):
            segy[h][bottom] = _overlap_segments(n, h, bottom)

    S_total = 0.0
    for w in range(1, n - 1):
        for h in range(1, n - 1):
            area = n * n - w * h
            inv_area2 = 1.0 / (area * area)
            Ih = I_hole[w][h]

            # Hole placements are strictly inside the square: 1 <= left <= n-w-1, similarly for bottom
            for left in range(1, n - w):
                xsegs = segx[w][left]
                for bottom in range(1, n - h):
                    ysegs = segy[h][bottom]

                    # I_cross = ∬_{outer} ∬_{hole} distance
                    I_cross = 0.0
                    for x0, x1, mx, cx in xsegs:
                        for y0, y1, my, cy in ysegs:
                            i0 = I0(x0, x1, y0, y1)
                            term = cx * cy * i0
                            if mx:
                                term += mx * cy * Ix(x0, x1, y0, y1)
                            if my:
                                term += cx * my * Iy(x0, x1, y0, y1)
                            if mx and my:
                                term += mx * my * Ixy(x0, x1, y0, y1)
                            I_cross += term

                    # Inclusion-exclusion: region = outer \ hole
                    I_region = I_outer - 2.0 * I_cross + Ih
                    S_total += I_region * inv_area2

    return S_total


def solve() -> str:
    ans = _solve_S(40)
    return f"{ans:.4f}"


def _self_test() -> None:
    # Test values from the problem statement (rounded to 4 digits)
    assert f"{_solve_S(3):.4f}" == "1.6514"
    assert f"{_solve_S(4):.4f}" == "19.6564"


if __name__ == "__main__":
    _self_test()
    print(solve())
