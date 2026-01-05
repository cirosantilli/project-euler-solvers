#!/usr/bin/env python3
"""
Project Euler 233: Lattice points on a circle

Let f(N) be the number of integer-coordinate points on the circle through
(0,0), (N,0), (0,N), (N,N). We need:

    sum_{1 <= N <= 1e11, f(N) = 420} N

The key reduction is f(N) = r2(N^2), where r2(m) is the number of integer
solutions (a,b) to a^2 + b^2 = m.
"""
from __future__ import annotations

import bisect
import math
from typing import List

LIMIT = 10**11


def iroot(n: int, k: int) -> int:
    """floor(n**(1/k)) for integers."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n in (0, 1) or k == 1:
        return n
    x = int(n ** (1.0 / k))
    # fix rounding errors
    while (x + 1) ** k <= n:
        x += 1
    while x**k > n:
        x -= 1
    return x


def sieve_is_prime(n: int) -> bytearray:
    """Bytearray sieve: is_prime[i] is 1 iff i is prime."""
    if n < 2:
        return bytearray(b"\x00") * (n + 1)
    is_prime = bytearray(b"\x01") * (n + 1)
    is_prime[0:2] = b"\x00\x00"
    # evens > 2 are not prime
    is_prime[4 : n + 1 : 2] = b"\x00" * (((n - 4) // 2) + 1)
    m = int(n**0.5)
    for p in range(3, m + 1, 2):
        if is_prime[p]:
            step = 2 * p
            start = p * p
            is_prime[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return is_prime


def primes_mod1_up_to(n: int) -> List[int]:
    """All primes <= n with p % 4 == 1."""
    is_prime = sieve_is_prime(n)
    out: List[int] = []
    # only odd primes can be 1 mod 4, start at 5
    for p in range(5, n + 1, 2):
        if is_prime[p] and (p & 3) == 1:
            out.append(p)
    return out


def multiplier_prefix_sum(gmax: int, primes_mod1: List[int]) -> List[int]:
    """
    prefix[m] = sum_{1 <= t <= m, t has no prime factor p ≡ 1 (mod 4)} t

    i.e. t's prime factors are only from {2} ∪ {p ≡ 3 (mod 4)}.
    """
    allowed = bytearray(b"\x01") * (gmax + 1)
    allowed[0] = 0
    for p in primes_mod1:
        if p > gmax:
            break
        for m in range(p, gmax + 1, p):
            allowed[m] = 0

    prefix = [0] * (gmax + 1)
    s = 0
    for i in range(1, gmax + 1):
        if allowed[i]:
            s += i
        prefix[i] = s
    return prefix


def f(N: int) -> int:
    """
    Count integer lattice points on the circle through (0,0),(N,0),(0,N),(N,N).

    It can be shown this equals r2(N^2) = 4 * Π(2e_i+1) over primes p_i ≡ 1 (mod 4)
    appearing in N with exponent e_i.
    """
    n = N
    # remove factor 2 (irrelevant for r2(N^2))
    while (n & 1) == 0:
        n //= 2

    prod = 1
    p = 3
    while p * p <= n:
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            if (p & 3) == 1:
                prod *= 2 * e + 1
        p += 2

    if n > 1 and (n & 3) == 1:
        # remaining prime factor with exponent 1
        prod *= 3

    return 4 * prod


def solve(limit: int = LIMIT) -> int:
    # test value from the problem statement
    assert f(10000) == 36

    # For f(N)=420:
    # 4 * Π(2e_i+1) = 420  =>  Π(2e_i+1) = 105 = 3*5*7
    # Feasible exponent patterns for primes ≡ 1 (mod 4) in N are:
    #   (3,2,1), (10,2), (7,3)
    #
    # Any extra factor made of primes 2 or ≡3 (mod 4) doesn't change f(N).
    # We'll multiply each "base" by all such "allowed multipliers" t <= limit//base.

    # Max prime needed occurs in (3,2,1) with smallest p^3*q^2 = 5^3 * 13^2.
    max_prime = limit // (5**3 * 13**2)
    primes1 = primes_mod1_up_to(int(max_prime))

    # For the multiplier prefix sum, we only ever need m <= limit//min_base,
    # where min_base is achieved by 5^3 * 13^2 * 17.
    gmax = limit // (5**3 * 13**2 * 17)
    prefix = multiplier_prefix_sum(int(gmax), primes1)

    def g(m: int) -> int:
        # By construction, m should never exceed gmax.
        return prefix[m]

    total = 0

    # Convenience: get index in primes1 for <= bound.
    def idx_upto(bound: int) -> int:
        return bisect.bisect_right(primes1, bound)

    # Pattern (10,2): p^10 * q^2 (p != q), primes ≡ 1 (mod 4)
    # Only p=5 works for exponent 10 under limit 1e11.
    p = 5
    p10 = p**10
    if p10 <= limit:
        qmax = math.isqrt(limit // p10)
        iq = idx_upto(qmax)
        for j in range(iq):
            q = primes1[j]
            if q == p:
                continue
            base = p10 * (q * q)
            m = limit // base
            total += base * g(m)

    # Pattern (7,3): a^7 * b^3 (a != b), primes ≡ 1 (mod 4)
    amax = iroot(limit, 7)
    ia = idx_upto(amax)
    for i in range(ia):
        a = primes1[i]
        a7 = a**7
        if a7 > limit:
            break
        bmax = iroot(limit // a7, 3)
        ib = idx_upto(bmax)
        for j in range(ib):
            b = primes1[j]
            if b == a:
                continue
            base = a7 * (b**3)
            if base > limit:
                continue
            m = limit // base
            total += base * g(m)

    # Pattern (3,2,1): p^3 * q^2 * r (all distinct), primes ≡ 1 (mod 4)
    p3max = iroot(limit, 3)
    ip3 = idx_upto(p3max)
    for i in range(ip3):
        p3 = primes1[i]
        p3_3 = p3**3
        if p3_3 > limit:
            break
        q2max = math.isqrt(limit // p3_3)
        iq = idx_upto(q2max)
        for j in range(iq):
            q = primes1[j]
            if q == p3:
                continue
            base_pq = p3_3 * (q * q)
            if base_pq > limit:
                continue
            rmax = limit // base_pq
            ir = idx_upto(rmax)
            for k in range(ir):
                r = primes1[k]
                if r == p3 or r == q:
                    continue
                base = base_pq * r
                m = limit // base
                total += base * g(m)

    return total


if __name__ == "__main__":
    print(solve())
