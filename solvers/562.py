#!/usr/bin/env python3
"""
Project Euler 562: Maximal perimeter

We must construct a lattice triangle ABC inside/on the circle of radius r centered at the origin,
with no other lattice point inside or on its edges, maximizing the perimeter. Define T(r)=R/r where
R is the circumradius of the maximal-perimeter triangle. Output the rounded value of T(10^7).

Key facts used:
- "No other lattice point" ⇔ triangle is a *primitive lattice triangle* ⇔ area = 1/2.
  With one vertex translated to the origin, this is equivalent to |det(u, v)| = 1 where
  u, v are the two edge vectors from that vertex.

- If we fix B and A, with d = A - B (must be primitive gcd(dx,dy)=1), then all C satisfying
  det(d, C-B) = ±1 are given by:
      C = B + (v0 + k d)  (det=+1)  or  C = B + (-v0 + k d) (det=-1),
  where v0 is any particular solution to det(d, v0)=1. We obtain v0 from extended gcd.

- For fixed A,B, feasible C are those on the line B + v0 + k d inside the disk; this gives an
  interval of integer k. The perimeter as a function of k is convex on that line segment, so the
  maximum over integer k occurs at one of the endpoints.

Implementation notes:
- We search a small neighborhood of the antipode of each circle lattice point B (canonical reps)
  to find A, because the maximal-perimeter triangle has A nearly opposite B.
  For this problem's input (r=10^7), a neighborhood radius of 200 is sufficient and fast.

- We generate lattice points on x^2 + y^2 = r^2 using Gaussian-integer multiplicativity and
  Cornacchia's algorithm to get a sum-of-two-squares representation for primes p≡1 (mod 4).
"""

from __future__ import annotations
import math
import sys
from typing import Dict, Iterable, List, Set, Tuple

Point = Tuple[int, int]


# ----------------------------
# Number theory utilities
# ----------------------------

def factorize(n: int) -> Dict[int, int]:
    """Trial division factorization for n <= 1e7 (fast enough)."""
    f: Dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            f[d] = f.get(d, 0) + 1
            n //= d
        d = 3 if d == 2 else d + 2
    if n > 1:
        f[n] = f.get(n, 0) + 1
    return f


def egcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended gcd: returns (g, x, y) with a*x + b*y = g."""
    x0, y0, x1, y1 = 1, 0, 0, 1
    while b:
        q = a // b
        a, b = b, a % b
        x0, x1 = x1, x0 - q * x1
        y0, y1 = y1, y0 - q * y1
    return a, x0, y0


def sqrt_minus1_mod_p(p: int) -> int:
    """
    Find t such that t^2 ≡ -1 (mod p), where p is an odd prime with p ≡ 1 (mod 4).
    Deterministic search for a quadratic non-residue.
    """
    # For p ≡ 1 (mod 4), if a is a quadratic non-residue then a^((p-1)/4) is a square root of -1.
    e = (p - 1) // 4
    for a in range(2, p):
        if pow(a, (p - 1) // 2, p) == p - 1:  # non-residue
            t = pow(a, e, p)
            if (t * t) % p == p - 1:
                return t
    raise ValueError("Failed to find sqrt(-1) mod p")


def sum_two_squares_prime(p: int) -> Tuple[int, int]:
    """
    For prime p ≡ 1 (mod 4), find a,b >= 0 such that a^2 + b^2 = p (Cornacchia's algorithm).
    """
    t = sqrt_minus1_mod_p(p)
    r0, r1 = p, t
    while r1 * r1 > p:
        r0, r1 = r1, r0 % r1

    a = abs(r1)
    b2 = p - a * a
    b = math.isqrt(b2)
    if b * b != b2:
        # Try the other square root
        t = p - t
        r0, r1 = p, t
        while r1 * r1 > p:
            r0, r1 = r1, r0 % r1
        a = abs(r1)
        b2 = p - a * a
        b = math.isqrt(b2)
        if b * b != b2:
            raise ValueError("Cornacchia failed")
    return (a, b) if a >= b else (b, a)


# Gaussian integer helpers: represent z = a + b i as tuple (a,b)
def gmul(z1: Tuple[int, int], z2: Tuple[int, int]) -> Tuple[int, int]:
    (a, b), (c, d) = z1, z2
    return (a * c - b * d, a * d + b * c)


def gconj(z: Tuple[int, int]) -> Tuple[int, int]:
    a, b = z
    return (a, -b)


def canon_pair(x: int, y: int) -> Tuple[int, int]:
    x = abs(x)
    y = abs(y)
    return (x, y) if x >= y else (y, x)


def reps_prime_power(p: int, e: int) -> Set[Tuple[int, int]]:
    """
    Canonical representations (x>=y>=0) of p^e as x^2 + y^2.
    In this problem we only call it with e even (because we factor r^2),
    which simplifies cases p=2 and p≡3 (mod 4).
    """
    if e == 0:
        return {(1, 0)}

    if p == 2:
        # For even e: 2^e = (2^(e/2))^2 + 0^2.
        return {(1 << (e // 2), 0)}

    if p % 4 == 3:
        # For even e: only axis representations.
        return {(pow(p, e // 2), 0)}

    # p % 4 == 1, prime in our usage (from factorization)
    a, b = sum_two_squares_prime(p)  # a^2+b^2=p
    g = (a, b)

    # precompute g^k for k=0..e
    gpows: List[Tuple[int, int]] = [(1, 0)]
    for _ in range(e):
        gpows.append(gmul(gpows[-1], g))

    reps: Set[Tuple[int, int]] = set()
    # All gaussian integers of norm p^e (up to units) are g^k * conj(g)^(e-k), k=0..e
    for k in range(e + 1):
        z = gmul(gpows[k], gconj(gpows[e - k]))
        reps.add(canon_pair(z[0], z[1]))
    return reps


def circle_reps_canonical(r: int) -> List[Tuple[int, int]]:
    """
    Return canonical lattice points (x>=y>=0) on the circle x^2+y^2=r^2.
    Uses multiplicativity of sums of two squares in Gaussian integers.
    """
    fac = factorize(r)
    reps: Set[Tuple[int, int]] = {(1, 0)}
    for p, exp in fac.items():
        e = 2 * exp  # exponent in r^2
        rp = reps_prime_power(p, e)
        new: Set[Tuple[int, int]] = set()
        for a, b in reps:
            for c, d in rp:
                # multiply (a+bi)(c+di) and (a+bi)(c-di)
                x1, y1 = a * c - b * d, a * d + b * c
                x2, y2 = a * c + b * d, a * d - b * c
                new.add(canon_pair(x1, y1))
                new.add(canon_pair(x2, y2))
        reps = new
    # Sort by decreasing x then y
    return sorted(reps, key=lambda t: (t[0], t[1]), reverse=True)


# ----------------------------
# Geometry/search
# ----------------------------

def ceil_div(a: int, b: int) -> int:
    """Ceiling division for b>0."""
    return -((-a) // b)


def best_triangle_for_r(r: int, W: int = 200) -> Tuple[Point, Point, Point, int]:
    """
    Find a maximal-perimeter primitive lattice triangle inside the disk radius r.

    Returns (A,B,C,N) where N = |AB|^2 * |BC|^2 * |CA|^2 (an integer).
    """
    r2 = r * r
    Bs = circle_reps_canonical(r)

    bestP = -1.0
    bestABC: Tuple[Point, Point, Point] = ((0, 0), (0, 0), (0, 0))
    bestN = 0

    sqrt = math.sqrt
    gcd = math.gcd

    for Bx, By in Bs:
        # Search A near the antipode -B.
        cx = -Bx
        cy = -By

        for ox in range(-W, W + 1):
            Ax = cx + ox
            Ax2 = Ax * Ax
            for oy in range(-W, W + 1):
                Ay = cy + oy
                if Ax2 + Ay * Ay > r2:
                    continue
                dx = Ax - Bx
                dy = Ay - By
                if gcd(abs(dx), abs(dy)) != 1:
                    continue

                g, s, t = egcd(dx, dy)
                if g == 0:
                    continue
                if g == -1:
                    s, t = -s, -t
                elif g != 1:
                    continue

                # Particular v0 with det(d, v0) = 1
                v0x, v0y = -t, s

                ab2 = dx * dx + dy * dy
                ab = sqrt(ab2)

                # det = +1 and det = -1 are both allowed (orientation doesn't matter for perimeter)
                for sign in (1, -1):
                    vx0 = v0x * sign
                    vy0 = v0y * sign

                    # C(k) = B + (v0 + k d) must lie in disk -> quadratic in k
                    wx = Bx + vx0
                    wy = By + vy0

                    a = ab2
                    b = 2 * (wx * dx + wy * dy)
                    c = wx * wx + wy * wy - r2
                    D = b * b - 4 * a * c
                    if D < 0:
                        continue

                    sD = math.isqrt(D)
                    # use ceil(sqrt(D)) for safe bounds (we'll verify by disk check)
                    if sD * sD != D:
                        sD += 1

                    denom = 2 * a
                    kmin = ceil_div(-b - sD, denom)
                    kmax = (-b + sD) // denom
                    if kmin > kmax:
                        continue

                    for k in (kmin, kmax):
                        vx = vx0 + k * dx
                        vy = vy0 + k * dy
                        Cx = Bx + vx
                        Cy = By + vy
                        if Cx * Cx + Cy * Cy > r2:
                            continue

                        bc2 = vx * vx + vy * vy
                        cax = Cx - Ax
                        cay = Cy - Ay
                        ca2 = cax * cax + cay * cay

                        P = ab + sqrt(bc2) + sqrt(ca2)
                        if P > bestP:
                            bestP = P
                            bestABC = ((Ax, Ay), (Bx, By), (Cx, Cy))
                            bestN = ab2 * bc2 * ca2

    A, B, C = bestABC
    return A, B, C, bestN


def T_value(r: int, W: int = 200) -> Tuple[float, int]:
    """
    Return (T(r) as float, rounded(T(r)) as int) using exact-integer rounding.
    """
    _, _, _, N = best_triangle_for_r(r, W=W)
    denom = 2 * r

    # integer rounding of sqrt(N) / denom
    s = math.isqrt(N)
    q = s // denom  # floor
    # round up if sqrt(N) >= (q+0.5)*denom  <=>  4N >= (2q+1)^2 * denom^2
    if 4 * N >= (2 * q + 1) * (2 * q + 1) * denom * denom:
        rounded = q + 1
    else:
        rounded = q

    return (math.sqrt(N) / denom, rounded)


def solve(r: int = 10_000_000) -> int:
    """Compute the required rounded value for the given r."""
    _, rounded = T_value(r, W=200)
    return rounded


def _run_tests() -> None:
    # Test values from the problem statement (rounded to 5 decimal places).
    t10, r10 = T_value(10, W=200)
    assert abs(t10 - 97.26729) < 1e-5
    assert r10 == 97

    t100, r100 = T_value(100, W=200)
    assert abs(t100 - 9157.64707) < 1e-5
    assert r100 == 9158


def main() -> None:
    _run_tests()
    if len(sys.argv) >= 2:
        r = int(sys.argv[1])
    else:
        r = 10_000_000
    print(solve(r))


if __name__ == "__main__":
    main()
