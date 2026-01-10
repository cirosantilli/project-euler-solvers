#!/usr/bin/env python3
"""Project Euler 572: Idempotent Matrices

Count 3x3 integer matrices M with M^2 = M and all entries in [-n, n].

Given in the problem statement:
  C(1) = 164
  C(2) = 848
Find C(200).

No external libraries are used.
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import List, Tuple


Range = Tuple[int, int]
Triple = Tuple[int, int, int]


def floor_div(a: int, b: int) -> int:
    """Return floor(a/b) for integers."""
    return a // b


def ceil_div(a: int, b: int) -> int:
    """Return ceil(a/b) for integers."""
    return -((-a) // b)


def div_interval(low: int, high: int, coef: int) -> Range:
    """Return integer interval [L,R] s.t. low <= coef*v <= high."""
    if coef > 0:
        return ceil_div(low, coef), floor_div(high, coef)
    else:
        return ceil_div(high, coef), floor_div(low, coef)


def t_bounds(base: int, step: int, low: int, high: int) -> Range:
    """Solve low <= base + step*t <= high for integer t, return [tmin,tmax]."""
    if step > 0:
        tmin = ceil_div(low - base, step)
        tmax = floor_div(high - base, step)
    else:
        # dividing by a negative flips inequalities
        tmin = ceil_div(high - base, step)
        tmax = floor_div(low - base, step)
    return tmin, tmax


@lru_cache(maxsize=None)
def egcd(a: int, b: int) -> Tuple[int, int, int]:
    """Extended gcd: return (g,x,y) with a*x + b*y = g, g >= 0."""
    if b == 0:
        if a == 0:
            return 0, 0, 0
        return abs(a), (1 if a > 0 else -1), 0
    g, x1, y1 = egcd(b, a % b)
    x = y1
    y = x1 - (a // b) * y1
    return g, x, y


def count_2d(A: int, B: int, C: int, Ly: int, Ry: int, Lz: int, Rz: int) -> int:
    """Count integer solutions of A*y + B*z = C with y in [Ly,Ry], z in [Lz,Rz]."""
    if Ly > Ry or Lz > Rz:
        return 0

    if A == 0:
        if B == 0:
            return (Ry - Ly + 1) * (Rz - Lz + 1) if C == 0 else 0
        if C % B != 0:
            return 0
        z = C // B
        return (Ry - Ly + 1) if Lz <= z <= Rz else 0

    if B == 0:
        if C % A != 0:
            return 0
        y = C // A
        return (Rz - Lz + 1) if Ly <= y <= Ry else 0

    g, xg, yg = egcd(A, B)
    if g == 0 or C % g != 0:
        return 0

    k = C // g
    y0 = xg * k
    z0 = yg * k
    step_y = B // g
    step_z = -A // g

    lo1, hi1 = t_bounds(y0, step_y, Ly, Ry)
    lo2, hi2 = t_bounds(z0, step_z, Lz, Rz)
    lo = max(lo1, lo2)
    hi = min(hi1, hi2)
    return max(0, hi - lo + 1)


def count_3d_linear(a: int, b: int, c: int, ranges: List[Range]) -> int:
    """Count integer solutions of a*x + b*y + c*z = 1 in a rectangular box."""
    (Lx, Rx), (Ly, Ry), (Lz, Rz) = ranges
    if Lx > Rx or Ly > Ry or Lz > Rz:
        return 0

    if a == 0 and b == 0 and c == 0:
        return 0

    nnz = (a != 0) + (b != 0) + (c != 0)

    if nnz == 1:
        if a != 0:
            if 1 % a != 0:
                return 0
            x = 1 // a
            return (Ry - Ly + 1) * (Rz - Lz + 1) if Lx <= x <= Rx else 0
        if b != 0:
            if 1 % b != 0:
                return 0
            y = 1 // b
            return (Rx - Lx + 1) * (Rz - Lz + 1) if Ly <= y <= Ry else 0
        if 1 % c != 0:
            return 0
        z = 1 // c
        return (Rx - Lx + 1) * (Ry - Ly + 1) if Lz <= z <= Rz else 0

    if nnz == 2:
        if a == 0:
            return count_2d(b, c, 1, Ly, Ry, Lz, Rz) * (Rx - Lx + 1)
        if b == 0:
            return count_2d(a, c, 1, Lx, Rx, Lz, Rz) * (Ry - Ly + 1)
        return count_2d(a, b, 1, Lx, Rx, Ly, Ry) * (Rz - Lz + 1)

    # nnz == 3
    lens = [(Rx - Lx + 1, 0), (Ry - Ly + 1, 1), (Rz - Lz + 1, 2)]
    lens.sort()
    idx = lens[0][1]

    total = 0
    if idx == 0:
        for x in range(Lx, Rx + 1):
            total += count_2d(b, c, 1 - a * x, Ly, Ry, Lz, Rz)
    elif idx == 1:
        for y in range(Ly, Ry + 1):
            total += count_2d(a, c, 1 - b * y, Lx, Rx, Lz, Rz)
    else:
        for z in range(Lz, Rz + 1):
            total += count_2d(a, b, 1 - c * z, Lx, Rx, Ly, Ry)

    return total


def triples_up_to(T: int) -> List[Triple]:
    """All integer triples (a,b,c) with max(|.|) <= T, excluding (0,0,0)."""
    res: List[Triple] = []
    for a in range(-T, T + 1):
        for b in range(-T, T + 1):
            for c in range(-T, T + 1):
                if a == 0 and b == 0 and c == 0:
                    continue
                res.append((a, b, c))
    return res


def count_rank1(n: int) -> int:
    """Count rank-1 idempotent matrices with entries in [-n,n]."""
    T = math.isqrt(n)
    us = triples_up_to(T)

    cube_T = [(-T, T), (-T, T), (-T, T)]

    S = 0  # u small, v bounded by n//maxabs(u)
    O = 0  # overlap: both u and v small

    for a, b, c in us:
        U = max(abs(a), abs(b), abs(c))
        B = n // U
        cube_B = [(-B, B), (-B, B), (-B, B)]

        S += count_3d_linear(a, b, c, cube_B)
        O += count_3d_linear(a, b, c, cube_T)

    # ordered pairs (u,v) are counted; (u,v) and (-u,-v) represent the same matrix
    ordered_pairs = 2 * S - O
    return ordered_pairs // 2


def v_ranges_for_rank2(u: Triple, n: int) -> List[Range]:
    """Given small u, return allowed ranges for v_i such that M = I - u v^T is within [-n,n]."""
    u0, u1, u2 = u
    uvals = (u0, u1, u2)

    # Diagonal constraint on uv^T: 1-n <= u_i v_i <= 1+n
    low = 1 - n
    high = 1 + n

    rng: List[Range] = []
    for j in range(3):
        # Off-diagonal constraints: for all i != j, |u_i v_j| <= n
        off = n
        for i in range(3):
            if i == j:
                continue
            ui = uvals[i]
            if ui != 0:
                off = min(off, n // abs(ui))

        L = -off
        R = off

        uj = uvals[j]
        if uj != 0:
            Ld, Rd = div_interval(low, high, uj)
            if Ld > Rd:
                Ld, Rd = Rd, Ld
            L = max(L, Ld)
            R = min(R, Rd)

        rng.append((L, R))

    return rng


def count_rank2(n: int) -> int:
    """Count rank-2 idempotent matrices with entries in [-n,n]."""
    T = math.isqrt(n)
    us = triples_up_to(T)

    SA = 0  # u small, v satisfying constraints
    overlap = 0  # u small AND v small (for inclusion-exclusion)

    for u in us:
        a, b, c = u
        vr = v_ranges_for_rank2(u, n)

        if vr[0][0] > vr[0][1] or vr[1][0] > vr[1][1] or vr[2][0] > vr[2][1]:
            continue

        SA += count_3d_linear(a, b, c, vr)

        # overlap: additionally restrict v to [-T, T]^3
        vr2: List[Range] = []
        ok = True
        for L, R in vr:
            L2 = max(L, -T)
            R2 = min(R, T)
            if L2 > R2:
                ok = False
                break
            vr2.append((L2, R2))

        if ok:
            overlap += count_3d_linear(a, b, c, vr2)

    ordered_pairs = 2 * SA - overlap
    return ordered_pairs // 2


def C(n: int) -> int:
    """Return C(n) as defined in the problem statement."""
    if n == 0:
        return 1  # only the zero matrix fits
    # rank 0 (zero matrix) and rank 3 (identity matrix)
    return 2 + count_rank1(n) + count_rank2(n)


def main() -> None:
    # Tests given in the problem statement
    assert C(1) == 164
    assert C(2) == 848

    print(C(200))


if __name__ == "__main__":
    main()
