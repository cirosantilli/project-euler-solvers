#!/usr/bin/env python3
"""
Project Euler 662 - Fibonacci Paths

Alice walks on a lattice grid. She can step from (a,b) to (a+x,b+y) if:
  - sqrt(x^2 + y^2) is a Fibonacci number (1,2,3,5,8,13,...)
  - x >= 0, y >= 0

Let F(W,H) be the number of paths from (0,0) to (W,H).
Compute F(10000,10000) mod 1_000_000_007.

This file implements:
  - step generation from Fibonacci lengths <= max(W,H)
  - dynamic programming with a rolling buffer of rows to reduce memory
  - asserts for the sample values in the statement

No external libraries are used.
"""

from math import isqrt

MOD = 1_000_000_007


def fibs_upto(n: int):
    """Return Fibonacci numbers {1,2,3,5,...} up to n (inclusive)."""
    if n < 1:
        return []
    fibs = [1, 2]
    while fibs[-1] + fibs[-2] <= n:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs


def step_vectors_upto(n: int):
    """
    Generate all nonnegative integer step vectors (dx,dy) such that:
        dx^2 + dy^2 = f^2
    for some Fibonacci f <= n.

    Returns a list of unique (dx,dy) excluding (0,0).
    """
    fibs = fibs_upto(n)
    steps = set()
    for f in fibs:
        ff = f * f
        for dx in range(0, f + 1):
            dy2 = ff - dx * dx
            dy = isqrt(dy2)
            if dy * dy == dy2:
                if dx == 0 and dy == 0:
                    continue
                steps.add((dx, dy))
    return sorted(steps)


def count_paths(W: int, H: int, mod: int = MOD) -> int:
    """
    Count paths to (W,H) with allowed Fibonacci-distance steps.
    Uses DP with rolling buffer of size max_dy + 1.
    """
    max_side = max(W, H)
    steps = step_vectors_upto(max_side)

    # Separate steps into:
    # - horizontal (dy=0)
    # - vertical+diagonal (dy>0)
    horiz = []
    other = []
    max_dy = 0
    for dx, dy in steps:
        if dx == 0 and dy == 0:
            continue
        if dy == 0:
            horiz.append(dx)
        else:
            other.append((dx, dy))
            if dy > max_dy:
                max_dy = dy

    # Rolling buffer for rows: we need access to row[y-dy]
    buf_h = max_dy + 1
    # Each row is a Python list of ints (faster than array('I') for indexed reads/writes in CPython)
    # but still memory-friendly due to rolling window.
    buffer = [[0] * (W + 1) for _ in range(buf_h)]

    for y in range(0, H + 1):
        row = buffer[y % buf_h]
        # reset row
        for x in range(W + 1):
            row[x] = 0

        for x in range(0, W + 1):
            if x == 0 and y == 0:
                val = 1
            else:
                val = 0

            # Horizontal moves: (dx,0) from same row
            for dx in horiz:
                if x >= dx:
                    val += row[x - dx]

            # Vertical + diagonal moves: from earlier rows
            for dx, dy in other:
                if y >= dy and x >= dx:
                    src = buffer[(y - dy) % buf_h]
                    val += src[x - dx]

            row[x] = val % mod

    return buffer[H % buf_h][W]


def main():
    # Required sample asserts from the statement:
    assert count_paths(3, 4) == 278
    assert count_paths(10, 10) == 215_846_462

    # Print the required final answer (do not assert it).
    print(count_paths(10_000, 10_000) % MOD)


if __name__ == "__main__":
    main()

