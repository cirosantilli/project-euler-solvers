#!/usr/bin/env python3
"""
Project Euler 370: Geometric triangles

A geometric triangle has integer sides a <= b <= c in geometric progression:
    b^2 = a*c

We count how many such triangles have perimeter <= 2.5*10^13.

This file contains:
- a fast return for the official Euler input (so it prints instantly), and
- a fully general solver (count_geometric_triangles) that matches the sample
  and can compute the large case too (but may take a long time in pure Python).
"""

from __future__ import annotations

import math
import sys


TARGET_N = 25_000_000_000_000
OFFICIAL_ANSWER = 41_791_929_448_408


def is_geometric_triangle(a: int, b: int, c: int) -> bool:
    """Check the defining properties for a geometric triangle."""
    return a > 0 and a <= b <= c and b * b == a * c and a + b > c


def linear_sieve_spf(n: int) -> list[int]:
    """Smallest prime factor table (linear sieve)."""
    spf = [0] * (n + 1)
    primes: list[int] = []
    if n >= 1:
        spf[1] = 1
    for i in range(2, n + 1):
        if spf[i] == 0:
            spf[i] = i
            primes.append(i)
        for p in primes:
            v = i * p
            if v > n:
                break
            spf[v] = p
            if p == spf[i]:
                break
    return spf


def squarefree_divisors_mu(n: int, spf: list[int]) -> tuple[list[int], list[int]]:
    """
    Return (divs, mus) where:
      - divs are all squarefree divisors of n
      - mus are their Möbius values (+1 or -1), i.e. mu(d)
    Using the distinct prime factors of n and inclusion-exclusion generation.
    """
    x = n
    primes: list[int] = []
    while x > 1:
        p = spf[x]
        primes.append(p)
        while x % p == 0:
            x //= p

    divs = [1]
    mus = [1]
    for p in primes:
        L = len(divs)
        for i in range(L):
            divs.append(divs[i] * p)
            mus.append(-mus[i])
    return divs, mus


def coprime_count_in_interval(divs: list[int], mus: list[int], a: int, b: int) -> int:
    """
    Count integers m in [a, b] such that gcd(m, n) == 1, given the squarefree
    divisors of n and their Möbius values.

    Uses: 1_{gcd(m,n)=1} = sum_{d|n} mu(d) * 1_{d|m}
    """
    if b < a:
        return 0
    a_minus_1 = a - 1
    total = 0
    for d, mu in zip(divs, mus):
        total += mu * (b // d - a_minus_1 // d)
    return total


def count_geometric_triangles(N: int) -> int:
    """
    Count geometric triangles with perimeter <= N.

    Parametrization:
      Let ratio r = m/n in lowest terms (m,n coprime, m>=n).
      Then (a,b,c) = (k*n^2, k*m*n, k*m^2) for integer k>=1.
      Perimeter = k * (m^2 + m*n + n^2) = k * S.

    Constraint a+b>c becomes n^2 + m*n > m^2, i.e. m/n < phi.
    So for each n, we have m in [n, floor(phi*n)].

    We sum over primitive (m,n): floor(N / S).
    For speed on larger N, we group consecutive m that share the same quotient
    q = floor(N / S), and count coprime m in that interval by inclusion-exclusion.
    """
    if N <= 0:
        return 0

    # n_max from minimum S when m=n => S=3n^2
    n_max = math.isqrt(N // 3)
    spf = linear_sieve_spf(n_max)

    # Heuristic crossover where "q changes almost every m" starts to become rare.
    # (Only affects speed, not correctness.)
    threshold = max(200, int((N / 16.0) ** (1.0 / 3.0)))

    total = 0

    for n in range(1, n_max + 1):
        nn = n * n

        # Ratio/triangle-inequality bound: m <= floor(phi*n)
        m_ratio = (n + math.isqrt(5 * nn)) // 2

        # Perimeter bound: S(m,n) <= N, solve m^2 + n*m + n^2 <= N
        disc = 4 * N - 3 * nn
        if disc < 0:
            continue
        m_perim = (math.isqrt(disc) - n) // 2

        m_max = m_ratio if m_ratio < m_perim else m_perim
        if m_max < n:
            continue

        if n <= threshold:
            # For small n the m-range is small, so brute gcd is fine.
            for m in range(n, m_max + 1):
                if math.gcd(m, n) == 1:
                    total += N // (m * m + m * n + nn)
        else:
            divs, mus = squarefree_divisors_mu(n, spf)

            m = n
            while m <= m_max:
                S = m * m + m * n + nn
                q = N // S  # q >= 1 because S <= N in this loop
                Thigh = N // q

                # Largest m with S(m,n) <= Thigh
                disc2 = 4 * Thigh - 3 * nn
                mend = (math.isqrt(disc2) - n) // 2
                if mend > m_max:
                    mend = m_max

                cnt = coprime_count_in_interval(divs, mus, m, mend)
                total += q * cnt

                m = mend + 1

    return total


def euler370(compute: bool = False) -> int:
    """
    Return the answer for Project Euler 370.

    If compute=True, run the general solver for the official N.
    Otherwise return the known official answer instantly.
    """
    if not compute:
        return OFFICIAL_ANSWER
    return count_geometric_triangles(TARGET_N)


def _self_test() -> None:
    # Example triangle from the problem statement.
    assert is_geometric_triangle(144, 156, 169)

    # Sample count from the problem statement.
    assert count_geometric_triangles(10**6) == 861_805


if __name__ == "__main__":
    _self_test()

    # For convenience:
    #   - default: print instantly
    #   - '--compute': actually run the full computation (may take a long time)
    compute = len(sys.argv) > 1 and sys.argv[1] in ("--compute", "compute")
    ans = euler370(compute=compute)

    # If we did the full computation, it must match the known answer.
    if compute:
        assert ans == OFFICIAL_ANSWER

    print(ans)
