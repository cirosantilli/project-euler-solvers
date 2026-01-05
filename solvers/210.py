# Project Euler 210: Obtuse Angled Triangles
#
# Key idea:
# Split obtuse-angle cases by which vertex is obtuse, using dot products.
# For r divisible by 4, let a = r/4 and C = (a,a).
#
# - Angle at O is obtuse  <=> (x,y)·(a,a) < 0  <=> x+y < 0.
# - Angle at C is obtuse  <=> (O-C)·(B-C) < 0 <=> x+y > 2a (= r/2).
# - Angle at B is obtuse  <=> (O-B)·(C-B) < 0 <=> x^2+y^2 < a(x+y).
#
# These regions are disjoint (except boundaries which are excluded by strictness),
# so N(r) = N_O + N_C + N_B, but we must subtract degenerate "triangles" where
# O, B, C are collinear (largest angle = 180°). That happens iff B lies on y=x,
# and there are exactly (r-1) such points in S(r) excluding O and C.

from __future__ import annotations
import math


def circle_points_leq(n: int) -> int:
    """
    Count integer lattice points (x,y) with x^2 + y^2 <= n.

    Uses a decomposition:
      - Take the biggest axis-aligned square |x|<=m, |y|<=m fully inside the circle.
        Choose m = isqrt(n//2) so 2(m+1)^2 > n, guaranteeing no points with both
        |x|>m and |y|>m can still be inside the circle.
      - Then all remaining points lie in one of four disjoint strips where exactly
        one coordinate has abs > m. By symmetry, count the right strip (x>m) and
        multiply by 4.
    """
    if n < 0:
        return 0
    isqrt = math.isqrt
    r = isqrt(n)
    m = isqrt(n // 2)

    total = (2 * m + 1) ** 2  # all points in the inscribed square

    # Count points in the right strip x = m+1..r, y in [-ymax..ymax]
    strip = 0
    x = m + 1
    rem = n - x * x  # rem = n - x^2
    while x <= r:
        y = isqrt(rem)
        strip += 2 * y + 1
        # Update rem for next x: (x+1)^2 - x^2 = 2x + 1
        rem -= 2 * x + 1
        x += 1

    total += 4 * strip
    return total


def N(r: int) -> int:
    assert r % 4 == 0, "Problem setup uses C=(r/4,r/4); r should be divisible by 4."
    a = r // 4

    # Points in S(r): |x|+|y| <= r  => total = 1 + sum_{k=1..r} 4k = 1 + 2r(r+1)
    # Using symmetry in u=x+y:
    # N_O = #{x+y<0 in S(r)} = (total - #{x+y=0})/2 = r^2 + r/2  (r is even here)
    N_O = r * r + r // 2

    # N_C = #{x+y>r/2} in S(r). For r divisible by 4, this simplifies to:
    # N_C = r(2r+1)/4
    N_C = (r * (2 * r + 1)) // 4

    # N_B: points with x^2+y^2 < a(x+y).
    # In (u,v)=(x+y, x-y): this becomes (u-a)^2 + v^2 < a^2 with u,v same parity.
    # Let p=u-a. Then count (p,v) with p^2+v^2 < a^2 and parity p+v ≡ a (mod 2).
    # If a is even, we want p+v even; else odd.
    n_total = a * a - 1  # p^2+v^2 <= a^2-1
    n_even = (a * a - 1) // 2  # for p+v even: s^2+t^2 <= floor((a^2-1)/2)

    if a % 2 == 0:
        N_B = circle_points_leq(n_even)
    else:
        N_B = circle_points_leq(n_total) - circle_points_leq(n_even)

    # Subtract degenerate collinear cases (largest angle = 180°), which occur
    # exactly when B lies on the line y=x, excluding B=O and B=C.
    # Along y=x inside |x|+|y|<=r => 2|x|<=r => x in [-r/2..r/2], giving r+1 points.
    # Excluding O and C leaves (r+1)-2 = r-1.
    degenerate = r - 1

    return N_O + N_C + N_B - degenerate


# Tests from the problem statement
assert N(4) == 24
assert N(8) == 100

if __name__ == "__main__":
    print(N(1_000_000_000))
