#!/usr/bin/env python3
"""
Project Euler 557 - Cutting Triangles

Optimized enumeration using the transformed (s, a, d) formulation:
Let t = a+b+c+d (triangle area), and define s = t + a.

Then:
    bc = a^2*d / s  must be integer
    b + c = s - 2a - d
    discriminant = (b+c)^2 - 4bc  must be a perfect square

We enumerate s,a and d values efficiently by stepping d in multiples of s/gcd(s,a^2).
"""

import sys
from math import gcd, isqrt


def is_square(x: int) -> int:
    """Return sqrt(x) if x is a perfect square, else -1."""
    if x < 0:
        return -1
    r = isqrt(x)
    return r if r * r == x else -1


def S(N: int) -> int:
    total_sum = 0

    # s = t + a, with t <= N and a >= 1  => s <= 2N
    for s in range(3, 2 * N + 1):
        a_min = max(1, s - N)  # ensure t=s-a <= N
        a_max = (s - 3) // 2  # ensure b+c >=2 (since d>=1)

        if a_min > a_max:
            continue

        for a in range(a_min, a_max + 1):
            a2 = a * a
            g = gcd(s, a2)
            if g == 1:
                continue

            step = s // g  # d must be multiple of this
            # Need b+c = s - 2a - d >= 2  => d <= s - 2a - 2
            max_k = (s - 2 * a - 2) // step
            if max_k <= 0:
                continue

            base_prod = a2 // g  # since bc = k * a^2/g

            for k in range(1, max_k + 1):
                d = step * k
                w = s - 2 * a - d  # w = b+c
                prod = base_prod * k  # prod = bc

                disc = w * w - 4 * prod
                r = is_square(disc)
                if r < 0:
                    continue

                # b = (w-r)/2 must be integer
                if (w - r) & 1:
                    continue

                b = (w - r) // 2
                if b <= 0:
                    continue
                c = (w + r) // 2
                if b > c:
                    continue

                t = s - a  # total triangle area
                total_sum += t

    return total_sum


def solve() -> None:
    # Problem statement test value
    assert S(20) == 259

    # The example says total area 55 has exactly two quadruples; verify via brute from formula
    # (Only done for correctness checks, small enough.)
    def quads_total(T):
        res = []
        for a in range(1, T):
            for b in range(1, T - a):
                for c in range(b, T - a - b):
                    denom = a * a - b * c
                    if denom <= 0:
                        continue
                    num = b * c * (2 * a + b + c)
                    if num % denom:
                        continue
                    d = num // denom
                    if a + b + c + d == T:
                        res.append((a, b, c, d))
        return sorted(res)

    assert quads_total(55) == [(20, 2, 24, 9), (22, 8, 11, 14)]

    print(S(10000))


if __name__ == "__main__":
    solve()
