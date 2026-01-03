#!/usr/bin/env python3
"""
Project Euler 482 - The Incenter of a Triangle

We sum L = p + IA + IB + IC over all integer-sided triangles with incenter I,
integer IA, IB, IC, and perimeter p <= P.

Key reduction (see README):
- Let x = s-a, y = s-b, z = s-c where s is semiperimeter.
- Let r be inradius. Then IA^2 = x^2 + r^2 (and similarly for y,z).
- Under the problem's integrality assumptions, r is an integer, hence (r,x,IA)
  is a (possibly non-primitive) Pythagorean triple.
- Also r^2 = xyz / (x+y+z)  =>  xyz = r^2 (x+y+z).
  For fixed r and chosen x,y, we get:
      z = r^2 (x+y) / (x*y - r^2).

We enumerate all possible (r,x,IA) with bounds derived from P, then for each r
solve for (x,y,z) using the formula above.
"""

from __future__ import annotations

import math
import sys
from array import array


def _build_pythagorean_pairs(r_max: int, x_max: int):
    """
    Build, grouped by r, all x such that r^2 + x^2 is a perfect square.

    Returns:
      counts[r]  : number of x-values stored for this r
      offsets[r] : start index in flat arrays (CSR style), offsets has length r_max+2
      xs[idx]    : x value
      us[idx]    : corresponding hypotenuse u = sqrt(r^2 + x^2)
    """
    # counts[r] = number of (x,u) pairs for this r
    counts = array("I", [0]) * (r_max + 1)

    gcd = math.gcd
    m_limit = int(math.isqrt(x_max)) + 1

    # Pass 1: count how many pairs each r will have
    for m in range(2, m_limit + 1):
        mm = m * m
        for n in range(1, m):
            if ((m - n) & 1) == 0:
                continue
            if gcd(m, n) != 1:
                continue
            a = mm - n * n
            b = 2 * m * n
            if a > b:
                a, b = b, a

            # orientation: r = k*a, x = k*b
            k_max = r_max // a
            kb = x_max // b
            if kb < k_max:
                k_max = kb
            if k_max:
                step = a
                for r in range(step, step * (k_max + 1), step):
                    counts[r] += 1

            # orientation: r = k*b, x = k*a
            k_max = r_max // b
            ka = x_max // a
            if ka < k_max:
                k_max = ka
            if k_max:
                step = b
                for r in range(step, step * (k_max + 1), step):
                    counts[r] += 1

    # Prefix sums -> offsets (CSR)
    offsets = array("I", [0]) * (r_max + 2)
    total = 0
    for r in range(1, r_max + 1):
        total += counts[r]
        offsets[r + 1] = total

    xs = array("I", [0]) * total
    us = array("I", [0]) * total
    pos = array("I", offsets)  # write pointer for each r

    # Pass 2: fill the flat arrays
    for m in range(2, m_limit + 1):
        mm = m * m
        for n in range(1, m):
            if ((m - n) & 1) == 0:
                continue
            if gcd(m, n) != 1:
                continue
            a = mm - n * n
            b = 2 * m * n
            if a > b:
                a, b = b, a
            c = mm + n * n

            # r = k*a, x = k*b
            k_max = r_max // a
            kb = x_max // b
            if kb < k_max:
                k_max = kb
            for k in range(1, k_max + 1):
                r = k * a
                idx = pos[r]
                xs[idx] = k * b
                us[idx] = k * c
                pos[r] = idx + 1

            # r = k*b, x = k*a
            k_max = r_max // b
            ka = x_max // a
            if ka < k_max:
                k_max = ka
            for k in range(1, k_max + 1):
                r = k * b
                idx = pos[r]
                xs[idx] = k * a
                us[idx] = k * c
                pos[r] = idx + 1

    return counts, offsets, xs, us


def S(P: int) -> int:
    """Compute S(P) as defined in the problem."""
    if P < 0:
        return 0
    s_max = P // 2  # semiperimeter
    if s_max < 3:
        return 0

    # x,y,z are all >=1 so x_max = s_max-2
    x_max = s_max - 2

    # For fixed semiperimeter s, inradius r is maximized by an equilateral triangle:
    # r = s*sqrt(3)/9. Any r larger than that cannot occur for perimeter <= P.
    r_max = int(s_max * math.sqrt(3) / 9) + 2

    counts, offsets, xs, us = _build_pythagorean_pairs(r_max, x_max)

    total = 0

    for r in range(1, r_max + 1):
        start = offsets[r]
        end = offsets[r + 1]
        if end - start < 3:
            continue

        # Build mapping x -> u = sqrt(r^2 + x^2) and a sorted list of x
        # (counts are small per r; dict+sort is fast)
        m = {}
        for i in range(start, end):
            m[xs[i]] = us[i]
        if len(m) < 3:
            continue
        x_list = sorted(m)
        r2 = r * r
        m_get = m.get

        n = len(x_list)
        for i in range(n):
            x = x_list[i]
            ux = m[x]
            for j in range(i, n):
                y = x_list[j]
                denom = x * y - r2
                if denom <= 0:
                    continue
                numer = r2 * (x + y)
                if numer % denom:
                    continue
                z = numer // denom
                if z < y:
                    continue
                s = x + y + z
                if s > s_max:
                    continue
                uz = m_get(z)
                if uz is None:
                    continue

                # Found x<=y<=z. Convert to L:
                # perimeter p = 2s, IA=u(x), IB=u(y), IC=u(z)
                total += 2 * s + ux + m[y] + uz

    return total


def main() -> None:
    # Test value given in the statement
    assert S(10**3) == 3619

    P = 10**7
    if len(sys.argv) >= 2:
        P = int(sys.argv[1])

    print(S(P))


if __name__ == "__main__":
    main()
