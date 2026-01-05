#!/usr/bin/env python3
"""
Project Euler 228 - Minkowski Sums

We need the number of sides of:
S_1864 + S_1865 + ... + S_1909

Key idea:
For convex polygons, the Minkowski sum's edge normals are the union of the summands'
edge normals (duplicates merge). For regular n-gons centered at the origin, the set of
edge-normal directions is exactly the n directions at angles 2πk/n.

Thus the number of sides equals the number of distinct directions among all
{2πk/n : k = 0..n-1, n in [L..R]}.

Each direction corresponds to a root of unity with some exact order d; the total number
of distinct directions is sum_{d in D} φ(d), where D is the set of all d such that
there exists some n in [L..R] divisible by d.
"""

from __future__ import annotations


def totient_sieve(limit: int) -> list[int]:
    """Compute φ(0..limit) in O(limit log log limit) time."""
    phi = list(range(limit + 1))
    for p in range(2, limit + 1):
        if phi[p] == p:  # p is prime
            for k in range(p, limit + 1, p):
                phi[k] -= phi[k] // p
    return phi


def count_sides_interval(L: int, R: int) -> int:
    """
    Number of sides of S_L + S_{L+1} + ... + S_R.

    A positive integer d contributes iff there is a multiple of d in [L, R], i.e.
    ceil(L/d)*d <= R. If so, we add φ(d).
    """
    if L <= 0 or R <= 0 or L > R:
        raise ValueError("Require positive integers with L <= R")

    phi = totient_sieve(R)
    total = 0

    for d in range(1, R + 1):
        first_multiple = ((L + d - 1) // d) * d
        if first_multiple <= R:
            total += phi[d]

    return total


def main() -> None:
    # From the problem statement example: S3 + S4 is a six-sided shape.
    assert count_sides_interval(3, 4) == 6

    print(count_sides_interval(1864, 1909))


if __name__ == "__main__":
    main()
