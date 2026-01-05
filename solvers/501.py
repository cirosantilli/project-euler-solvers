#!/usr/bin/env python3
"""
Project Euler 501: Eight Divisors

Count numbers n <= 10^12 having exactly 8 divisors.

A number has exactly 8 divisors iff its prime factorization is one of:
  1) p^7
  2) p^3 * q   (p != q primes)
  3) p * q * r (distinct primes)

We count each class using prime counting pi(x). For large x we use
the Lehmer prime-counting algorithm (pure Python).
"""

import sys
import math
from functools import lru_cache
from bisect import bisect_right


# -----------------------------
# Integer roots (safe)
# -----------------------------


def iroot_k(n: int, k: int) -> int:
    """floor(n^(1/k)) using integer binary search (safe for huge n)."""
    if n < 2:
        return n
    lo, hi = 1, int(n ** (1.0 / k)) + 3
    while lo + 1 < hi:
        mid = (lo + hi) >> 1
        if mid**k <= n:
            lo = mid
        else:
            hi = mid
    return lo


def isqrt(n: int) -> int:
    return int(math.isqrt(n))


# -----------------------------
# Prime sieve up to 1e6
# (sqrt(1e12)=1e6, enough for Lehmer loops)
# -----------------------------

SIEVE_MAX = 1_000_000


def sieve(n: int):
    is_prime = bytearray(b"\x01") * (n + 1)
    is_prime[0:2] = b"\x00\x00"
    limit = int(n**0.5)
    for i in range(2, limit + 1):
        if is_prime[i]:
            step = i
            start = i * i
            is_prime[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    primes = []
    pi = [0] * (n + 1)
    cnt = 0
    for i in range(n + 1):
        if is_prime[i]:
            primes.append(i)
            cnt += 1
        pi[i] = cnt
    return primes, pi


PRIMES, PI_SMALL = sieve(SIEVE_MAX)


# -----------------------------
# Lehmer prime counting pi(n)
# -----------------------------


@lru_cache(maxsize=None)
def phi(x: int, s: int) -> int:
    """
    phi(x, s) = count of numbers <= x not divisible by first s primes.
    Recurrence: phi(x,s)=phi(x,s-1)-phi(x/p_{s}, s-1)
    """
    if s == 0:
        return x
    if s == 1:
        return x - x // 2
    if s == 2:
        return x - x // 2 - x // 3 + x // 6
    # General recursion
    return phi(x, s - 1) - phi(x // PRIMES[s - 1], s - 1)


@lru_cache(maxsize=None)
def prime_pi(n: int) -> int:
    """
    Lehmer prime counting function pi(n).
    Works fast enough for n up to 10^12 when combined with caching.
    """
    if n <= SIEVE_MAX:
        return PI_SMALL[n]
    if n < 2:
        return 0

    a = prime_pi(iroot_k(n, 4))
    b = prime_pi(isqrt(n))
    c = prime_pi(iroot_k(n, 3))

    # Lehmer formula
    res = phi(n, a) + ((b + a - 2) * (b - a + 1)) // 2

    for i in range(a, b):
        w = n // PRIMES[i]
        res -= prime_pi(w)
        if i < c:
            lim = prime_pi(isqrt(w))
            for j in range(i, lim):
                res -= prime_pi(w // PRIMES[j]) - j
    return res


# -----------------------------
# Count numbers with exactly 8 divisors <= N
# -----------------------------


def count_eight_divisors(N: int) -> int:
    # Case 1: p^7 <= N
    lim1 = iroot_k(N, 7)
    c1 = prime_pi(lim1)

    # Case 2: p^3 * q <= N, p != q
    # p^3 <= N/2 implies p <= cbrt(N)
    c2 = 0
    lim_p = iroot_k(N, 3)
    # iterate primes p up to lim_p
    for p in PRIMES:
        if p > lim_p:
            break
        p3 = p * p * p
        if p3 > N:
            break
        x = N // p3
        # q prime <= x, excluding p if p <= x
        c2 += prime_pi(x) - (1 if p <= x else 0)

    # Case 3: p*q*r <= N distinct primes
    # Loop p < q and count r > q using pi(N/(p*q)) - pi(q)
    c3 = 0
    lim_p3 = iroot_k(N, 3)
    # p must be <= N^(1/3) for p*q*r <= N with q>=p and r>=q
    p_limit_index = bisect_right(PRIMES, lim_p3)
    for i in range(p_limit_index):
        p = PRIMES[i]
        # q must satisfy p*q*q <= N  -> q <= sqrt(N/p)
        q_max = isqrt(N // p)
        j_end = bisect_right(PRIMES, q_max)
        for j in range(i + 1, j_end):
            q = PRIMES[j]
            max_r = N // (p * q)
            if max_r <= q:
                break
            # count primes r where r > q and r <= max_r
            c3 += prime_pi(max_r) - (j + 1)

    return c1 + c2 + c3


def main():
    # Test values from the problem statement:
    assert count_eight_divisors(100) == 10
    assert count_eight_divisors(1000) == 180
    assert count_eight_divisors(10**6) == 224427

    N = 10**12
    ans = count_eight_divisors(N)
    print(ans)


if __name__ == "__main__":
    main()
