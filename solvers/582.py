#!/usr/bin/env python3
"""
Project Euler 582: Nearly Isosceles 120 Degree Triangles

We count integer-sided triangles (a, b, c) with one 120° angle, a <= b <= c,
b - a <= 100, and c <= N.

The answer for N = 10^100 is printed.

No external libraries are used (only Python standard library).
"""

from __future__ import annotations

import math


def is_square(n: int) -> int:
    """Return sqrt(n) if n is a perfect square, else -1."""
    if n < 0:
        return -1
    r = math.isqrt(n)
    return r if r * r == n else -1


def seeds_for_k(k: int, y_max: int = 2000) -> list[tuple[int, int]]:
    """
    Find orbit seeds (x,y) for x^2 - 3y^2 = k^2 with:
      - x even (so c = x/2 is integer),
      - y ≡ k (mod 2) (so a = (y-k)/2 is integer, possibly <= 0).

    We include solutions with y <= k (degenerate/non-triangle) because some
    orbits only enter the valid triangle region (a > 0) after one or more steps.

    A seed is a solution that has no positive predecessor under the parity-
    preserving unit step.
    """
    k2 = k * k
    sols: list[tuple[int, int]] = []

    for y in range(0, y_max + 1):
        if (y - k) & 1:
            continue
        x = is_square(3 * y * y + k2)
        if x == -1 or (x & 1):
            continue
        # sanity
        if x * x - 3 * y * y != k2:
            continue
        sols.append((x, y))

    # predecessor maps for the chosen step:
    # - even k: multiply/divide by (2 ± √3)
    # - odd  k: multiply/divide by (7 ± 4√3) = (2 ± √3)^2 (preserves x even, y odd)
    if k % 2 == 0:

        def prev(x: int, y: int) -> tuple[int, int]:
            # (x + y√3)(2 - √3) = (2x - 3y) + (2y - x)√3
            return (2 * x - 3 * y, 2 * y - x)

    else:

        def prev(x: int, y: int) -> tuple[int, int]:
            # (x + y√3)(7 - 4√3) = (7x - 12y) + (7y - 4x)√3
            return (7 * x - 12 * y, 7 * y - 4 * x)

    seeds: set[tuple[int, int]] = set()
    for x, y in sols:
        xp, yp = prev(x, y)
        # If predecessor exists in the same parity class, current isn't a seed.
        if (
            xp > 0
            and yp >= 0
            and ((yp - k) & 1) == 0
            and (xp & 1) == 0
            and xp * xp - 3 * yp * yp == k2
        ):
            continue
        seeds.add((x, y))

    return sorted(seeds)


def count_triangles(N: int) -> int:
    """
    Count triangles with c <= N (N can be huge).
    """
    total = 0
    limit_x = 2 * N  # because x = 2c

    for k in range(1, 101):
        seeds = seeds_for_k(k)

        if k % 2 == 0:

            def step(x: int, y: int) -> tuple[int, int]:
                # (x + y√3)(2 + √3) = (2x + 3y) + (x + 2y)√3
                return (2 * x + 3 * y, x + 2 * y)

        else:

            def step(x: int, y: int) -> tuple[int, int]:
                # (x + y√3)(7 + 4√3) = (7x + 12y) + (4x + 7y)√3
                return (7 * x + 12 * y, 4 * x + 7 * y)

        for x, y in seeds:
            while x <= limit_x:
                # Convert back: y = 2a + k, x = 2c, b = a + k
                if y > k:  # a > 0
                    a = (y - k) // 2
                    b = a + k
                    c = x // 2
                    # (Optional) sanity checks for development:
                    # assert c * c == a * a + b * b + a * b
                    # assert a <= b <= c and b - a <= 100
                    total += 1
                x, y = step(x, y)

    return total


def solve() -> int:
    # Problem statement test values
    assert count_triangles(1000) == 235
    assert count_triangles(10**8) == 1245

    return count_triangles(10**100)


if __name__ == "__main__":
    print(solve())
