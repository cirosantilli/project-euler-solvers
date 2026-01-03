#!/usr/bin/env python3
"""
Project Euler 332 - Spherical Triangles
https://projecteuler.net/problem=332

We need A(r): the smallest area spherical triangle whose vertices are integer lattice points
on the sphere x^2 + y^2 + z^2 = r^2 (radius r, centered at origin), excluding degenerate
triples that lie on the same great circle.

This is a stdlib-only solution (no NumPy).
"""

from __future__ import annotations

import math
from array import array
from typing import List, Tuple


Point = Tuple[int, int, int]


def lattice_points_on_sphere(r: int) -> List[Point]:
    """All integer points (x,y,z) with x^2+y^2+z^2 = r^2."""
    rr = r * r
    pts: set[Point] = set()
    for x in range(-r, r + 1):
        x2 = x * x
        for y in range(-r, r + 1):
            z2 = rr - x2 - y * y
            if z2 < 0:
                continue
            z = math.isqrt(z2)
            if z * z == z2:
                pts.add((x, y, z))
                pts.add((x, y, -z))
    return list(pts)


def _gcd3(a: int, b: int, c: int) -> int:
    return math.gcd(a, math.gcd(b, c))


def min_area_for_r(r: int) -> float:
    """
    Compute A(r).

    Area formula (unit vectors u,v,w):
        E = 2*atan2(|det(u,v,w)|, 1 + u·v + v·w + w·u)
    For radius-r vectors P,Q,R (|P|=|Q|=|R|=r):
        E = 2*atan2(|det(P,Q,R)|/r^3, 1 + (P·Q + Q·R + R·P)/r^2)
        area = E * r^2

    Degenerate triangles correspond to det(P,Q,R) = 0 and are skipped.

    Pruning:
    - The denominator is always <= 4 (since each dot <= r^2).
      Therefore for y = det/r^3:
          area >= 2*r^2*atan2(y, 4)
      If this lower bound is already >= current best, the det cannot improve best.
      Inverting gives a safe determinant cutoff:
          det <= 4*r^3*tan(best/(2*r^2))
      We maintain this as an integer D_max and skip det > D_max.

    - For a fixed pair (i,j), det(P_i,P_j,P_k) = cross(P_i,P_j)·P_k is always a multiple of
      g = gcd(|cross_x|,|cross_y|,|cross_z|). If g > D_max then no non-degenerate k can help,
      so we skip the whole k-loop for that (i,j).
    """
    pts = lattice_points_on_sphere(r)
    n = len(pts)
    if n < 3:
        return 0.0

    # Store coords in compact arrays for speed.
    xs = array("h", (p[0] for p in pts))
    ys = array("h", (p[1] for p in pts))
    zs = array("h", (p[2] for p in pts))

    r2 = r * r
    r3 = r2 * r
    inv_r2 = 1.0 / r2
    inv_r3 = 1.0 / r3

    # Dot matrix, stored flat: dots[i*n + j] = P_i·P_j
    dots = array("h", [0]) * (n * n)
    for i in range(n):
        xi = xs[i]
        yi = ys[i]
        zi = zs[i]
        row = i * n
        for j in range(i, n):
            v = xi * xs[j] + yi * ys[j] + zi * zs[j]
            dots[row + j] = v
            dots[j * n + i] = v

    atan2 = math.atan2
    tan = math.tan
    abs_ = abs
    gcd = math.gcd

    # Initial upper bound: any non-degenerate triangle area <= (pi/2)*r^2, so use that.
    best = (math.pi / 2.0) * r2
    best_unit = best / r2

    # Corresponding determinant cutoff.
    D_max = int(math.floor(4.0 * r3 * tan(best_unit / 2.0) + 1e-12))
    if D_max < 1:
        D_max = 1

    for i in range(n - 2):
        xi = xs[i]
        yi = ys[i]
        zi = zs[i]
        in_i = i * n

        for j in range(i + 1, n - 1):
            xj = xs[j]
            yj = ys[j]
            zj = zs[j]

            # cross(P_i, P_j)
            cx = yi * zj - zi * yj
            cy = zi * xj - xi * zj
            cz = xi * yj - yi * xj
            if cx == 0 and cy == 0 and cz == 0:
                continue

            # gcd pruning for this (i,j)
            g = gcd(abs_(cx), gcd(abs_(cy), abs_(cz)))
            if g == 0 or g > D_max:
                continue

            dot_ij = dots[in_i + j]
            jn = j * n

            for k in range(j + 1, n):
                # det(P_i,P_j,P_k) = cross(P_i,P_j) · P_k
                det = cx * xs[k] + cy * ys[k] + cz * zs[k]
                if det == 0:
                    continue  # degenerate
                det = abs_(det)
                if det > D_max:
                    continue

                denom = 1.0 + (dot_ij + dots[jn + k] + dots[in_i + k]) * inv_r2
                area = 2.0 * atan2(det * inv_r3, denom) * r2

                if area < best:
                    best = area
                    best_unit = best / r2
                    D_max = int(math.floor(4.0 * r3 * tan(best_unit / 2.0) + 1e-12))
                    if D_max < 1:
                        D_max = 1

    return best


def solve(limit: int = 50) -> float:
    return sum(min_area_for_r(r) for r in range(1, limit + 1))


def main() -> None:
    # Test value from the problem statement:
    assert round(min_area_for_r(14), 6) == 3.294040

    ans = solve(50)
    print(f"{ans:.6f}")


if __name__ == "__main__":
    main()
