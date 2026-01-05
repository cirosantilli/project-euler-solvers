#!/usr/bin/env python3
"""
Project Euler 198: Ambiguous Numbers

Key facts used:

1) x is ambiguous for some denominator bound d  <=>  x is the midpoint of two
   neighboring fractions in the Farey sequence of order d.

2) If a/b and c/d are Farey neighbors then bc - ad = 1, and the midpoint
      (a/b + c/d)/2 = (ad + bc) / (2bd)
   is already in lowest terms, so its denominator is exactly 2*b*d.

We need to count ambiguous x = p/q with 0 < x < 1/100 and q <= 1e8.

Split into two parts:
A) Bounds d < 100: the only way to approximate numbers < 1/100 with denominators < 100
   is using 0/1 and 1/n. Their midpoints are x = 1/(2n).
   Condition 1/(2n) < 1/100  <=>  n > 50.
   Also q = 2n <= 1e8  <=>  n <= 5e7.
   So this contributes 5e7 - 50.

B) Bounds d >= 100: then 1/100 is allowed and is closer to x < 1/100 than any fraction > 1/100,
   so both best approximations lie in (0, 1/100]. Every x in (0, 1/100) lies in exactly one interval
   (1/(n+1), 1/n] where n = floor(1/x) >= 100. Each such interval starts with Farey neighbors
   1/(n+1) and 1/n, whose denominators are (n+1, n). Inside that interval, the Stern–Brocot splitting
   keeps denominators evolving only by addition:
       (a, b) -> (a, a+b) and (a+b, b)
   Every node (a, b) corresponds to one ambiguous midpoint with denominator 2ab, so we count nodes with
   a*b <= 1e8/2.

This runs in well under a second in CPython.
"""

from __future__ import annotations

from fractions import Fraction
from math import gcd, isqrt
from typing import Set


def best_approximations(x: Fraction, d: int) -> Set[Fraction]:
    """Brute-force best approximations to x among reduced rationals with denominator <= d."""
    best: Set[Fraction] = set()
    best_err = None
    for q in range(1, d + 1):
        for p in range(0, q + 1):
            if gcd(p, q) != 1:
                continue
            r = Fraction(p, q)
            err = abs(r - x)
            if best_err is None or err < best_err:
                best_err = err
                best = {r}
            elif err == best_err:
                best.add(r)
    return best


def solve(limit_q: int = 10**8, R: int = 100) -> int:
    """
    Count ambiguous rationals x with 0 < x < 1/R and denominator q <= limit_q.
    For Euler 198: limit_q=1e8 and R=100.
    """
    L = limit_q // 2  # since midpoint denominator is 2*a*b

    # Part A: midpoints between 0/1 and 1/n: x = 1/(2n)
    # Need n > R/2 and n <= L
    base = L - (R // 2)

    # Part B: count all Stern–Brocot nodes inside each (1/(n+1), 1/n] interval, n>=R,
    # with a*b <= L.
    m = isqrt(L)
    internal = 0

    for n in range(R, m + 1):
        stack = [
            (n, n + 1)
        ]  # denominator-pair of neighbors (1/n, 1/(n+1)) up to ordering
        while stack:
            a, b = stack.pop()
            if a * b > L:
                continue
            internal += 1
            c = a + b
            stack.append((a, c))
            stack.append((c, b))

    return base + internal


if __name__ == "__main__":
    # Assert the example from the problem statement:
    # 9/40 has the two best approximations 1/4 and 1/5 for denominator bound 6.
    assert best_approximations(Fraction(9, 40), 6) == {Fraction(1, 4), Fraction(1, 5)}

    print(solve())
