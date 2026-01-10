#!/usr/bin/env python3
"""
Project Euler 634 - Numbers of the Form a^2 b^3

Count integers x <= n that can be written as x = a^2 * b^3 with a,b > 1.

No external libraries are used (standard library only).
"""

from __future__ import annotations

import math


def iroot(n: int, k: int) -> int:
    """Return floor(n^(1/k)) for integers n>=0, k>=1 using integer binary search."""
    if n < 2:
        return n
    # Exponential search for an upper bound
    hi = 1
    while hi**k <= n:
        hi <<= 1
    lo = hi >> 1
    # Binary search in [lo, hi)
    while lo + 1 < hi:
        mid = (lo + hi) >> 1
        if mid**k <= n:
            lo = mid
        else:
            hi = mid
    return lo


def squarefree_sieve(m: int) -> bytearray:
    """
    is_sqfree[x] == 1 iff x is squarefree, for 0 <= x <= m.
    Uses marking multiples of p^2 for primes p <= sqrt(m).
    """
    is_sqfree = bytearray(b"\x01") * (m + 1)
    if m >= 0:
        is_sqfree[0] = 0

    limit = math.isqrt(m)
    # sieve primes up to limit
    is_prime = bytearray(b"\x01") * (limit + 1)
    if limit >= 0:
        is_prime[0:2] = b"\x00\x00"
    root = math.isqrt(limit)
    for p in range(2, root + 1):
        if is_prime[p]:
            start = p * p
            step = p
            cnt = ((limit - start) // step) + 1
            is_prime[start : limit + 1 : step] = b"\x00" * cnt

    for p in range(2, limit + 1):
        if is_prime[p]:
            sq = p * p
            start = sq
            step = sq
            cnt = ((m - start) // step) + 1
            is_sqfree[start : m + 1 : step] = b"\x00" * cnt

    return is_sqfree


def mobius_upto(n: int) -> list[int]:
    """Compute Möbius function mu[0..n] with a linear sieve."""
    mu = [0] * (n + 1)
    if n >= 1:
        mu[1] = 1
    primes: list[int] = []
    is_comp = [False] * (n + 1)

    for i in range(2, n + 1):
        if not is_comp[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            v = i * p
            if v > n:
                break
            is_comp[v] = True
            if i % p == 0:
                mu[v] = 0
                break
            mu[v] = -mu[i]
    return mu


def count_primes_upto(n: int) -> int:
    """Count primes <= n with a simple sieve (n is small here: <= ~2000)."""
    if n < 2:
        return 0
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, math.isqrt(n) + 1):
        if sieve[p]:
            start = p * p
            step = p
            cnt = ((n - start) // step) + 1
            sieve[start : n + 1 : step] = b"\x00" * cnt
    return int(sum(sieve))


def count_cubefree(R: int) -> int:
    """
    Count cubefree integers <= R.

    Uses Möbius inversion:
      cubefree_count(R) = sum_{k>=1} mu(k) * floor(R / k^3),
    where the sum only needs k <= floor(R^(1/3)).
    """
    kmax = iroot(R, 3)
    mu = mobius_upto(kmax)
    total = 0
    for k in range(1, kmax + 1):
        mk = mu[k]
        if mk:
            k3 = k * k * k
            total += mk * (R // k3)
    return total


def powerful_count_and_squarefree(n: int) -> tuple[int, bytearray, int]:
    """
    Count powerful numbers <= n (including 1), using the unique representation:
        x = a^2 * b^3  with b squarefree, a >= 1.
    Then:
        powerful_count(n) = sum_{squarefree b <= n^(1/3)} floor(sqrt(n / b^3)).
    Returns (P, is_sqfree, m) where m = floor(n^(1/3)).
    """
    m = iroot(n, 3)
    is_sqfree = squarefree_sieve(m)
    isqrt = math.isqrt
    total = 0
    for b in range(1, m + 1):
        if is_sqfree[b]:
            b3 = b * b * b
            total += isqrt(n // b3)
    return total, is_sqfree, m


def F(n: int) -> int:
    """
    Compute F(n) for the problem.

    Let P be the number of powerful numbers <= n (including 1).
    The only powerful numbers that cannot be written with a,b > 1 are:
      X1: numbers whose prime exponents are all in {0,2,4}  (i.e. squares of cubefree integers)
      X2: numbers whose prime exponents are all in {0,3}    (i.e. cubes of squarefree integers)
      X3: prime sixth powers p^6
    X1 and X2 overlap only at 1, and X3 is disjoint from both.

    Therefore:
      F(n) = P - |X1| - |X2| - |X3| + 1
    """
    P, is_sqfree, _m = powerful_count_and_squarefree(n)

    R = math.isqrt(n)
    X1 = count_cubefree(R)  # includes 1
    X2 = int(sum(is_sqfree))  # squarefree numbers <= floor(n^(1/3)), includes 1
    X3 = count_primes_upto(iroot(n, 6))  # primes p with p^6 <= n

    return P - X1 - X2 - X3 + 1


def solve() -> None:
    # Test values from the statement
    assert F(100) == 2
    assert F(2 * 10**4) == 130
    assert F(3 * 10**6) == 2014

    n = 9 * 10**18
    print(F(n))


if __name__ == "__main__":
    solve()
