#!/usr/bin/env python3
"""
Project Euler 180: Golden Triplets.

We call (x,y,z) a golden triple of order k if:
- x,y,z are rationals of the form a/b with 0 < a < b <= k (equivalently: reduced denominator <= k)
- There exists an integer n such that f_n(x,y,z) = 0, where f_n is defined in the problem.

A key identity (and the point of the problem) is:
    f_n(x,y,z) = 0  <=>  x^n + y^n = z^n

By Fermat's Last Theorem, there are no non-zero rational solutions for |n| > 2,
so we only need to consider n in {1, 2, -1, -2}:
    n = 1   -> x + y = z
    n = 2   -> x^2 + y^2 = z^2
    n = -1  -> 1/x + 1/y = 1/z
    n = -2  -> 1/x^2 + 1/y^2 = 1/z^2

For each pair (x,y) we can compute z for each of these cases and check if z is in the allowed set.
We collect all distinct sums s = x + y + z, then compute:
    t = sum_{distinct s} s
and output u+v where t = u/v in lowest terms.
"""

from __future__ import annotations

from fractions import Fraction
from math import gcd, isqrt
from typing import Iterable, List, Set, Tuple


def rationals_between_0_and_1(k: int) -> List[Fraction]:
    """All reduced rationals a/b with 0 < a < b <= k."""
    Q: List[Fraction] = []
    for b in range(2, k + 1):
        for a in range(1, b):
            if gcd(a, b) == 1:
                Q.append(Fraction(a, b))
    # Sorting is helpful for stable iteration; duplicates are impossible due to gcd=1.
    return sorted(Q)


def is_square_fraction(q: Fraction) -> Tuple[bool, Fraction]:
    """Return (True, sqrt(q)) if q is a perfect square rational; otherwise (False, 0)."""
    if q < 0:
        return False, Fraction(0, 1)
    num = q.numerator
    den = q.denominator
    sn = isqrt(num)
    if sn * sn != num:
        return False, Fraction(0, 1)
    sd = isqrt(den)
    if sd * sd != den:
        return False, Fraction(0, 1)
    return True, Fraction(sn, sd)


def solve(k: int = 35) -> int:
    Q = rationals_between_0_and_1(k)
    Qset = set(Q)

    sums: Set[Fraction] = set()

    # Only need x <= y because all equations are symmetric in x and y,
    # and we only care about distinct sums.
    for i, x in enumerate(Q):
        for y in Q[i:]:
            # n = 1: x + y = z
            z = x + y
            if z in Qset:
                sums.add(x + y + z)

            # n = -1: 1/x + 1/y = 1/z  -> z = xy / (x+y)
            z = x * y / (x + y)
            if z in Qset:
                sums.add(x + y + z)

            # n = 2: x^2 + y^2 = z^2
            ok, z = is_square_fraction(x * x + y * y)
            if ok and z in Qset:
                sums.add(x + y + z)

            # n = -2: 1/x^2 + 1/y^2 = 1/z^2  -> z^2 = (xy)^2 / (x^2 + y^2)
            z2 = (x * y) ** 2 / (x * x + y * y)
            ok, z = is_square_fraction(z2)
            if ok and z in Qset:
                sums.add(x + y + z)

    t = sum(sums, Fraction(0, 1))
    return t.numerator + t.denominator


if __name__ == "__main__":
    ans = solve(35)
    print(ans)
