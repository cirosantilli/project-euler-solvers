#!/usr/bin/env python3
"""
Project Euler 453: Lattice Quadrilaterals

A *simple quadrilateral* has 4 distinct vertices, no straight (180°) angles, and does not self-intersect.

This program computes:
    Q(12345, 6789) mod 135707531

It also asserts the test values given in the problem statement.

No external libraries are used (only Python's standard library).
"""

from __future__ import annotations

import math
from functools import lru_cache


MOD = 135707531


def _sum_pows(t: int, k: int) -> int:
    """
    Sum_{i=1..t} i^k for k in [0..4]. Returns 0 for t<=0.
    Closed forms are used for speed and exactness.
    """
    if t <= 0:
        return 0
    if k == 0:
        return t
    if k == 1:
        return t * (t + 1) // 2
    if k == 2:
        return t * (t + 1) * (2 * t + 1) // 6
    if k == 3:
        return (t * t * (t + 1) * (t + 1)) // 4
    if k == 4:
        return t * (t + 1) * (2 * t + 1) * (3 * t * t + 3 * t - 1) // 30
    raise ValueError("k must be in [0..4]")


def Q(m: int, n: int) -> int:
    """
    Return Q(m,n) exactly (may be huge).

    Implementation follows the (forum-derived) formula:
        Q = C(P,4) - C(P,3) + 2*S + (7 - 2P)*L3 + 7*L4
    where:
      - P = (m+1)(n+1) is the number of lattice points.
      - S is the sum of areas of all (non-degenerate) triangles in the grid.
      - L3/L4 count collinear triples/quadruples in a specific weighted way.

    The key subroutine is a fast computation of weighted coprime sums using
    floor-division grouping plus memoization.
    """

    if m < 0 or n < 0:
        raise ValueError("m and n must be non-negative")

    P = (m + 1) * (n + 1)

    @lru_cache(maxsize=None)
    def G(u: int, v: int, a: int, b: int) -> int:
        """
        G(u,v,a,b) = sum_{1<=x<=u, 1<=y<=v, gcd(x,y)=1} x^a y^b

        This is computed via a divide-and-conquer recursion using floor-division
        (a classic trick for fast summatory functions), with memoization.
        """
        if u <= 0 or v <= 0:
            return 0

        q = math.isqrt(u)
        upper = min(v, u // q)

        res = _sum_pows(u, a) * _sum_pows(v, b)

        # Subtract contributions for gcd >= 2 by grouping on k = gcd(x,y).
        for k in range(2, upper + 1):
            res -= G(u // k, v // k, a, b) * (k ** (a + b))

        # More floor-division grouping to cover all k efficiently.
        for k in range(1, q):
            x = v // (u // (k + 1) + 1)
            y = v // (u // k)

            if x == y:
                res -= G(k, x, a, b) * (
                    _sum_pows(u // k, a + b) - _sum_pows(u // (k + 1), a + b)
                )
            else:
                lo = max(u // (k + 1), v // (x + 1))
                hi = min(u // k, v // x)
                if hi > lo:
                    res -= G(k, x, a, b) * (_sum_pows(hi, a + b) - _sum_pows(lo, a + b))

                if y:
                    lo2 = max(u // (k + 1), v // (y + 1))
                    hi2 = min(u // k, v // y)
                    if hi2 > lo2:
                        res -= G(k, y, a, b) * (
                            _sum_pows(hi2, a + b) - _sum_pows(lo2, a + b)
                        )

        return res

    def H(a: int, b: int, c: int) -> int:
        """
        H(a,b,c) = sum_{1<=x<=m, 1<=y<=n} x^a y^b gcd(x,y)^c
        """
        if c == 0:
            return _sum_pows(m, a) * _sum_pows(n, b)

        q = math.isqrt(m)
        upper = min(n, m // q)

        res = 0
        for k in range(1, upper + 1):
            res += G(m // k, n // k, a, b) * (k ** (a + b + c))

        for k in range(1, q):
            x = n // (m // (k + 1) + 1)
            y = n // (m // k)

            if x == y:
                res += G(k, x, a, b) * (
                    _sum_pows(m // k, a + b + c) - _sum_pows(m // (k + 1), a + b + c)
                )
            else:
                lo = max(m // (k + 1), n // (x + 1))
                hi = min(m // k, n // x)
                if hi > lo:
                    res += G(k, x, a, b) * (
                        _sum_pows(hi, a + b + c) - _sum_pows(lo, a + b + c)
                    )

                if y:
                    lo2 = max(m // (k + 1), n // (y + 1))
                    hi2 = min(m // k, n // y)
                    if hi2 > lo2:
                        res += G(k, y, a, b) * (
                            _sum_pows(hi2, a + b + c) - _sum_pows(lo2, a + b + c)
                        )

        return res

    def f(a: int, b: int, c: int) -> int:
        """
        f(a,b,c) = sum_{x=0..m, y=0..n} x^a y^b gcd(x,y)^c

        We compute the 1..m,1..n part via H() and then add the boundary cases
        involving x=0 or y=0 explicitly.
        """
        res = H(a, b, c)
        if a == 0:
            # x=0, y>=1: gcd(0,y)=y
            res += _sum_pows(n, b + c)
        if b == 0:
            # y=0, x>=1: gcd(x,0)=x
            res += _sum_pows(m, a + c)
        if a + b + c == 0:
            # (0,0): treat 0^0 as 1 for the point-counting case
            res += 1
        return res

    # Precompute the specific moments needed by the closed-form combination.
    need = [
        (0, 0, 1),
        (0, 1, 1),
        (1, 0, 1),
        (1, 1, 1),
        (0, 0, 2),
        (0, 1, 2),
        (1, 0, 2),
        (1, 1, 2),
        (0, 0, 0),
        (0, 1, 0),
        (1, 0, 0),
        (1, 1, 0),
        (3, 3, 0),
        (3, 2, 0),
        (2, 3, 0),
        (2, 2, 0),
        (3, 1, 0),
        (2, 1, 0),
        (3, 0, 0),
        (2, 0, 0),
        (1, 3, 0),
        (1, 2, 0),
        (0, 3, 0),
        (0, 2, 0),
    ]
    vals = {t: f(*t) for t in need}

    s001 = vals[(0, 0, 1)]
    s011 = vals[(0, 1, 1)]
    s101 = vals[(1, 0, 1)]
    s111 = vals[(1, 1, 1)]
    s002 = vals[(0, 0, 2)]
    s012 = vals[(0, 1, 2)]
    s102 = vals[(1, 0, 2)]
    s112 = vals[(1, 1, 2)]

    s000 = vals[(0, 0, 0)]
    s010 = vals[(0, 1, 0)]
    s100 = vals[(1, 0, 0)]
    s110 = vals[(1, 1, 0)]

    s330 = vals[(3, 3, 0)]
    s320 = vals[(3, 2, 0)]
    s230 = vals[(2, 3, 0)]
    s220 = vals[(2, 2, 0)]
    s310 = vals[(3, 1, 0)]
    s210 = vals[(2, 1, 0)]
    s300 = vals[(3, 0, 0)]
    s200 = vals[(2, 0, 0)]
    s130 = vals[(1, 3, 0)]
    s120 = vals[(1, 2, 0)]
    s030 = vals[(0, 3, 0)]
    s020 = vals[(0, 2, 0)]

    # s is 6*S (S = sum of triangle areas).
    s = (
        (s012 - 11 * s230 - s210 - s030) * (m + 1)
        + (s102 - 11 * s320 - s300 - s120) * (n + 1)
        - (s112 - 11 * s330 - s310 - s130)
        - (s002 - 11 * s220 - s200 - s020) * (m + 1) * (n + 1)
    )

    # c3 corresponds to L3 in the referenced derivation.
    c3 = (
        2
        * (
            (s010 - s011) * (m + 1)
            + (s100 - s101) * (n + 1)
            - (s000 - s001) * (m + 1) * (n + 1)
            - (s110 - s111)
        )
        + s020
        - (n + 2) * s010
        + (n + 1) * s000
        + s200
        - (m + 2) * s100
        + (m + 1) * s000
    )

    # c4 is 2*L4 in the referenced derivation (hence later //2).
    c4 = (
        (s000 * 4 - s001 * 6 + s002 * 2) * (m + 1) * (n + 1)
        + (s110 * 4 - s111 * 6 + s112 * 2)
        - (s100 * 4 - s101 * 6 + s102 * 2) * (n + 1)
        - (s010 * 4 - s011 * 6 + s012 * 2) * (m + 1)
        + s030
        - (n + 4) * s020
        + (3 * n + 5) * s010
        - 2 * (n + 1) * s000
        + s300
        - (m + 4) * s200
        + (3 * m + 5) * s100
        - 2 * (m + 1) * s000
    )

    # Final closed form.
    return math.comb(P, 4) - math.comb(P, 3) + s // 3 + (7 - 2 * P) * c3 + 7 * (c4 // 2)


def euler453() -> int:
    """Return the requested value: Q(12345, 6789) mod 135707531."""
    return Q(12345, 6789) % MOD


def _run_asserts() -> None:
    # Test values from the problem statement.
    assert Q(2, 2) == 94
    assert Q(3, 7) == 39590
    assert Q(12, 3) == 309000
    assert Q(123, 45) == 70542215894646


if __name__ == "__main__":
    _run_asserts()
    print(euler453())
