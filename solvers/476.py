#!/usr/bin/env python3
"""
Project Euler 476: Circle Packing II

We need the average, over all integer triangles 1 ≤ a ≤ b ≤ c < a+b ≤ n,
of the maximal area covered by 3 non-overlapping circles inside the triangle.

This implementation follows the (Zalgaller & Los) result that for 3 circles
the optimal packing has a very small number of configurations:
- Circle 1 is the incircle.
- Circle 2 sits in the smallest angle A and is tangent to the incircle and the two sides.
- Circle 3 is either:
    (i) in the next smallest angle B, tangent to the incircle, or
    (ii) again in angle A, tangent to circle 2 (a "stack" in the same corner),
  chosen by a simple inequality involving half-angles.

The code includes asserts for the test values from the problem statement.
No external (non-stdlib) libraries are used.
"""

from __future__ import annotations

import math
import sys
from array import array
from typing import Tuple


def _count_triangles(n: int) -> int:
    """Number of triples (a,b,c) with 1 ≤ a ≤ b ≤ c < a+b ≤ n."""
    m = n // 2
    # For fixed a and b with a ≤ b and a+b ≤ n, c ranges from b..a+b-1 (exactly a values).
    return sum(a * (n - 2 * a + 1) for a in range(1, m + 1))


def _r_and_half_sines(a: int, b: int, c: int) -> Tuple[float, float, float]:
    """
    Return:
      r2  : inradius squared
      sA  : sin(A/2) where A is angle opposite the smallest side a
      sB  : sin(B/2) where B is angle opposite the middle side b
    Assumes a ≤ b ≤ c and triangle inequality.
    """
    sp = 0.5 * (a + b + c)  # semiperimeter
    # inradius^2 = ((sp-a)(sp-b)(sp-c))/sp
    r2 = ((sp - a) * (sp - b) * (sp - c)) / sp

    # Half-angle sines (standard identities)
    sA = math.sqrt((sp - b) * (sp - c) / (b * c))
    sB = math.sqrt((sp - a) * (sp - c) / (a * c))
    return r2, sA, sB


def R(a: int, b: int, c: int) -> float:
    """
    Maximal area covered by three non-overlapping circles inside triangle (a,b,c).
    """
    if a > b:
        a, b = b, a
    if b > c:
        b, c = c, b
    if a > b:
        a, b = b, a
    # Now a ≤ b ≤ c

    r2, sA, sB = _r_and_half_sines(a, b, c)

    kA = (1.0 - sA) / (1.0 + sA)
    kA2 = kA * kA
    kB = (1.0 - sB) / (1.0 + sB)
    kB2 = kB * kB

    # Decision rule (equivalent to sin(A/2) ≥ tan(B/4)) expressed without extra square roots:
    # sin(A/2) ≥ tan(B/4)  <=>  sin(B/2) ≤ 2 sin(A/2) / (1 + sin(A/2)^2)
    if sB <= (2.0 * sA) / (1.0 + sA * sA):
        # third circle goes to angle B
        factor = 1.0 + kA2 + kB2
    else:
        # third circle stacks again in angle A
        factor = 1.0 + kA2 + kA2 * kA2

    return math.pi * r2 * factor


def S_bruteforce(n: int) -> float:
    """Slow reference implementation (only meant for small n)."""
    total = 0.0
    cnt = 0
    for a in range(1, n // 2 + 1):
        for b in range(a, n - a + 1):
            s = a + b
            if s > n:
                break
            for c in range(b, s):
                total += R(a, b, c)
                cnt += 1
    return total / cnt


def S(n: int) -> float:
    """
    Optimized computation for general n.
    Enumerates triangles in (a,b,x) form where:
        x = a+b-c  (so c = a+b-x), and 1 ≤ x ≤ a.
    This removes a subtraction and makes several expressions cheaper.

    Uses a precomputed sqrt and invsqrt table for integers up to 4*n*n to avoid
    per-triangle sqrt() calls for half-angle sines.
    """
    if n < 2:
        return 0.0

    maxv = 4 * n * n
    sqrt_tab = array("d", [0.0]) * (maxv + 1)
    inv_tab = array("d", [0.0]) * (maxv + 1)

    for i in range(1, maxv + 1):
        s = math.sqrt(i)
        sqrt_tab[i] = s
        inv_tab[i] = 1.0 / s

    total_count = _count_triangles(n)

    pi = math.pi
    total = 0.0
    comp = 0.0  # Kahan compensation

    n2 = n // 2
    for a in range(1, n2 + 1):
        twoa = 2 * a
        foura = 4 * a
        for b in range(a, n - a + 1):
            s_ab = a + b
            if s_ab > n:
                break
            twos = 2 * s_ab
            twob = 2 * b
            fourb = 4 * b

            for x in range(1, a + 1):
                c = s_ab - x

                # Inradius^2 in terms of x:
                # r^2 = x(2a-x)(2b-x) / (4(2(a+b)-x))
                t1 = twoa - x
                t2 = twob - x
                r2 = (x * t1 * t2) / (4.0 * (twos - x))

                # sin(A/2)^2 = x(2a-x) / (4*b*c)
                sA = sqrt_tab[x * t1] * inv_tab[fourb * c]
                kA = (1.0 - sA) / (1.0 + sA)
                kA2 = kA * kA

                # sin(B/2)^2 = x(2b-x) / (4*a*c)
                sB = sqrt_tab[x * t2] * inv_tab[foura * c]

                # Decide configuration:
                # if sin(A/2) ≥ tan(B/4) then 3rd circle goes to angle B; else stack at A.
                if sB <= (2.0 * sA) / (1.0 + sA * sA):
                    kB = (1.0 - sB) / (1.0 + sB)
                    kB2 = kB * kB
                    factor = 1.0 + kA2 + kB2
                else:
                    factor = 1.0 + kA2 + kA2 * kA2

                Rval = pi * r2 * factor

                # Kahan summation
                y = Rval - comp
                t = total + y
                comp = (t - total) - y
                total = t

    return total / total_count


def main() -> None:
    # Problem statement tests
    assert round(R(1, 1, 1), 5) == 0.31998
    assert round(S_bruteforce(2), 5) == 0.31998
    assert round(S_bruteforce(5), 5) == 1.25899

    n = 1803
    if len(sys.argv) >= 2:
        n = int(sys.argv[1])

    ans = S(n)
    print(f"{ans:.5f}")


if __name__ == "__main__":
    main()
