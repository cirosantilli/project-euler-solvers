#!/usr/bin/env python3
"""
Project Euler 653: Frictionless Tube

We compute d(L, N, j): the distance (in mm) traveled by the j-th marble (counting from the west)
until its centre reaches the eastern end of the tube.

No external libraries are used.
"""

from __future__ import annotations


def d(L: int, N: int, j: int) -> int:
    """
    Return d(L, N, j) as defined in the problem.

    Key derived formula:
        d(L, N, j) = (L - 20*j + 10) + a_(m)
    where m = N - j + 1 and a_(m) is the m-th smallest value among:
        a_i = -y_i  if marble i initially moves east
             +y_i  if marble i initially moves west
    and y_i is the prefix sum of the surface gaps:
        y_i = g_1 + g_2 + ... + g_i
        g_i = (r_i mod 1000) + 1
        r_1 = 6_563_116
        r_{i+1} = r_i^2 mod 32_745_673
        direction east iff r_i <= 10_000_000
    """
    if not (1 <= j <= N):
        raise ValueError("Require 1 <= j <= N")

    MOD = 32_745_673
    r = 6_563_116

    y = 0
    a = [0] * N  # store a_i

    # Generate gaps/directions, compute y_i (prefix sum of gaps), and a_i
    for i in range(N):
        g = (r % 1000) + 1
        y += g
        a[i] = -y if r <= 10_000_000 else y
        r = (r * r) % MOD

    m = N - j + 1  # exit rank (eastmost exits first)
    a.sort()
    am = a[m - 1]

    return (L - 20 * j + 10) + am


def solve() -> int:
    # Problem asks for:
    return d(1_000_000_000, 1_000_001, 500_001)


if __name__ == "__main__":
    # Given test values from the statement:
    assert d(5000, 3, 2) == 5519
    assert d(10_000, 11, 6) == 11_780
    assert d(100_000, 101, 51) == 114_101

    print(solve())
