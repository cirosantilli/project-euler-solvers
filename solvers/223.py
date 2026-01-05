#!/usr/bin/env python3
"""
Project Euler 223: Almost right-angled triangles I

Count integer triangles (a <= b <= c) with:
    a^2 + b^2 = c^2 + 1
and perimeter a + b + c <= 25,000,000.

Technique:
Generate all positive integer solutions to x^2 + y^2 - z^2 = 1 using a Berggren-style
tree of integer linear transformations (automorphisms of the quadratic form).
"""

from __future__ import annotations

import math
from typing import List, Tuple


LIMIT = 25_000_000


def solve(limit: int = LIMIT) -> int:
    """
    Returns the number of (a,b,c) with a<=b<=c, a^2+b^2=c^2+1 and a+b+c<=limit.
    """
    # Two root solutions generate two disjoint parity classes.
    stack: List[Tuple[int, int, int]] = [(1, 1, 1), (1, 2, 2)]
    count = 0

    # Local bindings for speed
    lim = limit
    append = stack.append
    pop = stack.pop

    while stack:
        a, b, c = pop()
        if a + b + c > lim:
            continue
        count += 1

        # Child via matrix A:
        x = a - 2 * b + 2 * c
        y = 2 * a - b + 2 * c
        z = 2 * a - 2 * b + 3 * c
        if x > y:
            x, y = y, x
        if x + y + z <= lim:
            append((x, y, z))

        # Child via matrix B:
        x = a + 2 * b + 2 * c
        y = 2 * a + b + 2 * c
        z = 2 * a + 2 * b + 3 * c
        if x > y:
            x, y = y, x
        if x + y + z <= lim:
            append((x, y, z))

        # Child via matrix C:
        # For isosceles nodes (a==b), the C-child is a duplicate of the A-child after swapping x/y.
        if a != b:
            x = -a + 2 * b + 2 * c
            y = -2 * a + b + 2 * c
            z = -2 * a + 2 * b + 3 * c
            if x > y:
                x, y = y, x
            if x + y + z <= lim:
                append((x, y, z))

    return count


def _bruteforce_count(limit: int) -> int:
    """
    Brute force verifier for small limits.
    Runs in O(limit^2), so keep limit small (e.g. <= 500).
    """
    cnt = 0
    for a in range(1, limit + 1):
        aa = a * a
        for b in range(a, limit + 1):
            s = aa + b * b - 1
            c = math.isqrt(s)
            if c < b:
                continue
            if c * c == s and a + b + c <= limit:
                cnt += 1
    return cnt


def _self_test() -> None:
    # The Project Euler statement doesn't provide sample counts for smaller limits,
    # so we sanity-check by comparing against brute force on a small bound.
    small = 300
    assert solve(small) == _bruteforce_count(small)


if __name__ == "__main__":
    _self_test()
    print(solve(LIMIT))
