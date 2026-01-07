#!/usr/bin/env python3
"""
Project Euler 556: Squarefree Gaussian Integers

We count proper squarefree Gaussian integers z = a + bi with a > 0 and b >= 0
such that a^2 + b^2 <= n, for n = 10^14.

No external libraries are used.
"""

from __future__ import annotations

from array import array
from math import isqrt


N = 10**14
LIMIT = isqrt(N)  # 10^7


def build_spf(limit: int) -> array:
    """Smallest prime factor sieve for 0..limit (inclusive)."""
    spf = array("I", [0]) * (limit + 1)
    if limit >= 0:
        spf[0] = 1
    if limit >= 1:
        spf[1] = 1

    r = isqrt(limit)
    for i in range(2, r + 1):
        if spf[i] == 0:  # prime
            spf[i] = i
            start = i * i
            step = i
            for j in range(start, limit + 1, step):
                if spf[j] == 0:
                    spf[j] = i

    for i in range(2, limit + 1):
        if spf[i] == 0:
            spf[i] = i
    return spf


def precompute(limit: int) -> tuple[array, array]:
    """
    Precompute:
      - prefixF[m] = sum_{k<=m} F(k), where F(k) is the aggregated Gaussian Möbius sum by norm.
      - A_small[x] = number of nonzero integer pairs (a,b) with a^2+b^2 <= x, for x<=limit.
    """
    spf = build_spf(limit)

    # F(m): aggregated Gaussian Möbius over all (associate classes of) Gaussian integers with norm m.
    # Values are small, int16 is enough.
    F = array("h", [0]) * (limit + 1)
    F[1] = 1

    for n in range(2, limit + 1):
        p = spf[n]
        rest = n // p
        e = 1
        while rest % p == 0:
            rest //= p
            e += 1

        if p == 2:
            coef = -1 if e == 1 else 0
        elif (p & 3) == 1:
            coef = -2 if e == 1 else (1 if e == 2 else 0)
        else:  # p % 4 == 3
            coef = -1 if e == 2 else 0

        F[n] = 0 if coef == 0 else F[rest] * coef

    # Prefix sums of F for fast range sums in the main summation.
    prefixF = array("q", [0]) * (limit + 1)
    s = 0
    for i in range(1, limit + 1):
        s += F[i]
        prefixF[i] = s

    # r2(n): number of representations of n as a^2 + b^2 (ordered pairs, including signs).
    # For n<=1e7 it fits in uint16.
    r2 = array("H", [0]) * (limit + 1)
    if limit >= 1:
        r2[1] = 4  # (±1,0),(0,±1)

    for n in range(2, limit + 1):
        p = spf[n]
        rest = n // p
        e = 1
        while rest % p == 0:
            rest //= p
            e += 1

        base = r2[rest]
        if base == 0:
            r2[n] = 0
        elif p == 2:
            r2[n] = base
        elif (p & 3) == 1:
            r2[n] = base * (e + 1)
        else:  # p % 4 == 3
            r2[n] = 0 if (e & 1) else base

    # A_small[x] = sum_{k=1..x} r2(k), i.e. all lattice points except (0,0).
    A_small = array("I", [0]) * (limit + 1)
    acc = 0
    for n in range(1, limit + 1):
        acc += r2[n]
        A_small[n] = acc

    # Free big temporary arrays (important for memory).
    del spf, F, r2
    return prefixF, A_small


def lattice_points_nonzero(x: int) -> int:
    """
    Exact count of nonzero integer lattice points (a,b) with a^2 + b^2 <= x.

    Uses a monotone boundary walk ("two-pointer") in O(sqrt(x)) time with only integer ops.
    """
    if x <= 0:
        return 0
    R = isqrt(x)
    b = R
    bb = b * b
    s = 0
    for a in range(1, R + 1):
        aa = a * a
        while aa + bb > x:
            b -= 1
            bb = b * b
        s += b
    # total nonzero points = 4*sum_{a=1..R} b(a) + 4*R
    return (s << 2) + (R << 2)


def compute_f(n: int, prefixF: array, A_small: array, small_limit: int) -> int:
    """
    Compute f(n) using:
      f(n) = (1/4) * sum_{m<=sqrt(n)} F(m) * A(n/m^2)
    where:
      - F(m) is aggregated Gaussian Möbius by norm,
      - A(t) counts all nonzero lattice points with a^2+b^2 <= t (full plane).
    """
    M = isqrt(n)
    if M > small_limit:
        raise ValueError("precomputation limit too small")

    # Cache for A(x) where x > small_limit (only needed for small m, so it's small).
    cache: dict[int, int] = {}

    total = 0
    m = 1
    pref = prefixF
    As = A_small
    while m <= M:
        x = n // (m * m)
        if x == 0:
            break

        # Find the largest m2 such that floor(n/m2^2) == x
        m2 = isqrt(n // x)
        if m2 > M:
            m2 = M

        sumF = pref[m2] - pref[m - 1]
        if sumF:
            if x <= small_limit:
                A = As[x]
            else:
                A = cache.get(x)
                if A is None:
                    A = lattice_points_nonzero(x)
                    cache[x] = A
            total += sumF * A

        m = m2 + 1

    # Convert from all associates (4 per unit class) to "proper" representatives.
    return total // 4


def solve() -> None:
    prefixF, A_small = precompute(LIMIT)

    # Asserts from the problem statement.
    assert compute_f(10, prefixF, A_small, LIMIT) == 7
    assert compute_f(10**2, prefixF, A_small, LIMIT) == 54
    assert compute_f(10**4, prefixF, A_small, LIMIT) == 5218
    assert compute_f(10**8, prefixF, A_small, LIMIT) == 52126906

    print(compute_f(N, prefixF, A_small, LIMIT))


if __name__ == "__main__":
    solve()
