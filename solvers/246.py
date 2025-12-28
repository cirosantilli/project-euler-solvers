#!/usr/bin/env python3
"""Project Euler 246: Tangents to an Ellipse

We are given:
  M(-2000,1500), G(8000,1500), and a circle centered at M of radius r=15000.

The ellipse e is the set of points X such that the distance from X to G equals
the distance from X to the circle. Because G lies inside the circle, all points
on the ellipse satisfy:

    d(X,M) + d(X,G) = r

So e is the standard ellipse with foci at M and G and major-axis length r.

We must count lattice points P for which the angle RPS (between the two tangents
from P to the ellipse) is greater than 45 degrees.

This file computes the exact answer using only integer arithmetic.
"""

from __future__ import annotations

import math


def solve() -> int:
    # Problem data
    Mx, My = -2000, 1500
    Gx, Gy = 8000, 1500
    r = 15000

    # Ellipse parameters
    # Center is midpoint of foci; shifting by (cx,cy) keeps lattice points integral.
    cx = (Mx + Gx) // 2
    cy = (My + Gy) // 2

    # Semi-major axis a = r/2, focal distance c = |MG|/2, b^2 = a^2 - c^2.
    dx = Gx - Mx
    dy = Gy - My
    dist2_MG = dx * dx + dy * dy
    # d(G,M) < r is guaranteed by the statement.
    assert dist2_MG < r * r
    a = r // 2
    a2 = a * a
    c2 = dist2_MG // 4
    b2 = a2 - c2

    # For this problem all values are integers.
    # Director circle radius^2 for axis-aligned ellipse: x^2 + y^2 = a^2 + b^2.
    R2 = a2 + b2
    ab = a2 * b2
    A = R2

    # The core angle criterion. Let (x,y) be coordinates relative to (cx,cy).
    # With u=x^2, v=y^2, the slopes of tangents satisfy a quadratic; for the
    # *acute* angle phi between the two tangent lines:
    #   |tan(phi)| > 1  <=> 4(b^2 u + a^2 v - a^2 b^2) > (u+v-(a^2+b^2))^2.
    # For points outside the director circle, the actual angle RPS equals phi.
    def angle_tan_gt_1(u: int, v: int) -> bool:
        return 4 * (b2 * u + a2 * v - ab) > (u + v - A) ** 2

    # --- Region 1: inside the director circle -> angle RPS > 90° -> always >45°.
    # Count integer points with x^2 + y^2 < R2 and outside the ellipse.
    total = 0
    y_max1 = math.isqrt(R2 - 1)  # strict: y^2 < R2
    for y in range(0, y_max1 + 1):
        v = y * y
        # Circle: x^2 + v < R2  <=>  x^2 <= R2 - v - 1
        rem = R2 - v - 1
        if rem < 0:
            continue
        x_max = math.isqrt(rem)

        # Outside ellipse: b^2 x^2 + a^2 y^2 > a^2 b^2.
        if v >= b2:
            x_min = 0
        else:
            # Need b^2 x^2 > a^2 (b^2 - v)
            num = a2 * (b2 - v)
            # Smallest integer x >=0 with b^2 x^2 > num.
            x_min = math.isqrt(num // b2)
            while b2 * x_min * x_min <= num:
                x_min += 1

        if x_min > x_max:
            continue
        if x_min == 0:
            count_x = 1 + 2 * x_max
        else:
            count_x = 2 * (x_max - x_min + 1)
        count_y = 2 if y > 0 else 1
        total += count_x * count_y

    # --- Region 2: outside the director circle.
    # Here angle RPS is acute (<90°), so RPS >45°  <=>  tan(phi) > 1.
    # We scan y and solve a quadratic in u=x^2 to get a contiguous x-range.
    y_limit = 20000  # safe upper bound for this specific ellipse
    for y in range(0, y_limit + 1):
        v = y * y

        # Derive quadratic in u = x^2:
        #   angle_tan_gt_1(u,v)  <=>  u^2 + p u + q < 0
        k = v - A
        p = 2 * k - 4 * b2
        q = k * k - 4 * a2 * v + 4 * ab
        disc = p * p - 4 * q
        if disc <= 0:
            continue
        s = math.isqrt(disc)

        # Approximate integer bounds for u between the (open) roots.
        u1 = (-p - s) // 2
        u2 = (-p + s) // 2
        if u2 < 0:
            continue

        # Find the actual integer x-range [x_min, x_max] (nonnegative) satisfying
        # the strict inequality, by small local adjustments.
        x_min_guess = max(0, math.isqrt(max(0, u1)) - 3)
        x_max_guess = math.isqrt(u2) + 3

        x_min = x_min_guess
        while x_min <= x_max_guess and not angle_tan_gt_1(x_min * x_min, v):
            x_min += 1
        if x_min > x_max_guess:
            continue

        x_max = x_max_guess
        while angle_tan_gt_1(x_max * x_max, v):
            x_max += 1
        x_max -= 1
        while x_max >= x_min and not angle_tan_gt_1(x_max * x_max, v):
            x_max -= 1
        if x_max < x_min:
            continue

        # Enforce "outside director circle": x^2 + v > R2.
        t = R2 - v
        if t >= 0:
            x_out = math.isqrt(t) + 1  # smallest x with x^2 > t
            x_min = max(x_min, x_out)
            if x_min > x_max:
                continue

        if x_min == 0:
            count_x = 1 + 2 * x_max
        else:
            count_x = 2 * (x_max - x_min + 1)
        count_y = 2 if y > 0 else 1
        total += count_x * count_y

    return total


def main() -> None:
    print(solve())


if __name__ == "__main__":
    main()
