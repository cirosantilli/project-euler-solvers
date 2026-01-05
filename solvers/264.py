"""Project Euler 264: Triangle Centres.

We need all lattice triangles ABC with:
  - circumcenter at the origin O
  - orthocenter at H = (5, 0)
  - perimeter <= 1e5

Answer: sum of perimeters rounded to 4 decimals.
"""

from __future__ import annotations

import math
from math import gcd, hypot, isqrt


H_X, H_Y = 5, 0


def _ceil_div(a: int, b: int) -> int:
    """Ceiling division for integers, b>0."""
    return -((-a) // b)


def _is_square(n: int) -> int | None:
    """Return integer sqrt if n is a perfect square, else None."""
    if n < 0:
        return None
    r = isqrt(n)
    return r if r * r == n else None


def _sum_perimeters(limit_p: int) -> tuple[float, int]:
    """Return (sum of perimeters, number of triangles) for perimeter <= limit_p."""
    # For any triangle inscribed in a circle of radius R, perimeter >= 4R.
    # Therefore R <= limit_p/4.
    r_max = limit_p / 4.0
    r2_max = r_max * r_max

    # Let vectors a,b,c be the vertices (as position vectors from O).
    # With circumcenter at O, orthocenter satisfies: h = a + b + c.
    # We will enumerate using d = b + c (so a = h - d).
    # Also let P = b - c. Then b = (d + P)/2, c = (d - P)/2.
    # Since |b|=|c| and b,c are on the same circle, P ⟂ d.
    # A short derivation yields |P|^2 = 3|d|^2 - 40 dx + 100, where d=(dx,dy).

    # Bounding trick:
    # |d| = |b+c| <= |b|+|c| = 2R <= limit_p/2.
    d_max = limit_p / 2.0
    # Also, m = p^2+q^2 (primitive direction for d) is bounded by:
    # m <= 40*|d| + 100 <= 40*d_max + 100 = 20*limit_p + 100.
    m_limit = int(40.0 * d_max + 100.0)  # = 20*limit_p + 100
    pq_limit = isqrt(m_limit) + 1

    seen: set[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]] = set()
    perimeters: list[float] = []

    # Special case: d = 0 => a = H, and b = -c on circle of radius 5.
    # This only happens for n = |H|^2 = 25.
    if limit_p >= 0:
        n0 = H_X * H_X + H_Y * H_Y  # 25
        pts = set()
        for x in range(-5, 6):
            y2 = n0 - x * x
            if y2 < 0:
                continue
            y = isqrt(y2)
            if y * y == y2:
                pts.add((x, y))
                pts.add((x, -y))
        H = (H_X, H_Y)
        for b in pts:
            c = (-b[0], -b[1])
            if b == c or b == H or c == H:
                continue
            tri = tuple(sorted((H, b, c)))
            if tri in seen:
                continue
            per = (
                hypot(H_X - b[0], H_Y - b[1])
                + hypot(b[0] - c[0], b[1] - c[1])
                + hypot(c[0] - H_X, c[1] - H_Y)
            )
            if per <= limit_p + 1e-9:
                seen.add(tri)
                perimeters.append(per)

    # Enumerate primitive directions (p,q) with p^2+q^2 <= m_limit.
    # We take p >= 0 (canonical), q any (needed), and include (0,1) for vertical.
    for p in range(0, pq_limit + 1):
        p2 = p * p
        if p2 > m_limit:
            break
        q_max = isqrt(m_limit - p2)
        for q in range(-q_max, q_max + 1):
            if p == 0:
                if q != 1:
                    continue
            if p == 0 and q == 0:
                continue
            if gcd(p, abs(q)) != 1:
                continue

            m = p2 + q * q
            if m == 0 or m > m_limit:
                continue

            # Solve congruence: (40p) * g ≡ 100 (mod m)
            # This is exactly the condition that |P|^2 is divisible by m.
            a = (40 * p) % m
            b = 100 % m
            d = gcd(a, m)
            if b % d != 0:
                continue
            m1 = m // d
            a1 = a // d
            b1 = b // d
            if m1 == 1:
                g0 = 0
            else:
                # gcd(a1, m1) == 1 by construction
                g0 = (b1 * pow(a1, -1, m1)) % m1

            # Bound |g| using |d|=|g|*sqrt(m) <= d_max.
            g_abs_max = int(d_max / math.sqrt(m)) + 2
            if g_abs_max <= 0:
                continue

            # Additional bound from divisibility magnitude:
            # if m divides (40gp - 100) then m <= |40gp - 100| <= 40|g|p + 100.
            if p == 0:
                g_abs_min = 1
            else:
                if m <= 100:
                    g_abs_min = 1
                else:
                    g_abs_min = max(1, (m - 100 + 40 * p - 1) // (40 * p))
            if g_abs_min > g_abs_max:
                continue

            # Enumerate all g = g0 + k*m1 with |g| <= g_abs_max.
            k_min = _ceil_div(-g_abs_max - g0, m1)
            k_max = (g_abs_max - g0) // m1

            for k in range(k_min, k_max + 1):
                g = g0 + k * m1
                if g == 0:
                    continue
                if abs(g) < g_abs_min:
                    continue

                # |P|^2 = 3 g^2 m - 40 g p + 100 = m * t^2
                M = 3 * g * g * m - 40 * g * p + 100
                if M <= 0 or M % m != 0:
                    continue
                t = _is_square(M // m)
                if t is None:
                    continue

                # P = (tq, -tp), d = (gp, gq). Need (d±P)/2 integral.
                if ((g * p + t * q) & 1) or ((g * q - t * p) & 1):
                    continue

                ax = H_X - g * p
                ay = H_Y - g * q
                bx = (g * p + t * q) // 2
                by = (g * q - t * p) // 2
                cx = (g * p - t * q) // 2
                cy = (g * q + t * p) // 2

                if (ax, ay) == (bx, by) or (ax, ay) == (cx, cy) or (bx, by) == (cx, cy):
                    continue

                # Radius bound (safe because perimeter >= 4R for inscribed triangles)
                n = ax * ax + ay * ay
                if n > r2_max + 1e-9:
                    continue

                per = (
                    hypot(ax - bx, ay - by)
                    + hypot(bx - cx, by - cy)
                    + hypot(cx - ax, cy - ay)
                )
                if per > limit_p + 1e-9:
                    continue

                tri = tuple(sorted(((ax, ay), (bx, by), (cx, cy))))
                if tri in seen:
                    continue
                seen.add(tri)
                perimeters.append(per)

    return math.fsum(perimeters), len(perimeters)


def solve(limit_p: int = 100_000) -> str:
    total, _ = _sum_perimeters(limit_p)
    return f"{total:.4f}"


def _self_test() -> None:
    # From the problem statement:
    # - there are 9 triangles with perimeter <= 50
    # - the sum of their perimeters, rounded to 4 decimals, is 291.0089
    total_50, count_50 = _sum_perimeters(50)
    assert count_50 == 9
    assert f"{total_50:.4f}" == "291.0089"


if __name__ == "__main__":
    _self_test()
    print(solve(100_000))
