#!/usr/bin/env python3
"""
Project Euler 484 - Arithmetic Derivative

Compute:
    S(N) = sum_{1 < k <= N} gcd(k, k')
where k' is the arithmetic derivative.

This solution uses only the Python standard library.
"""

from __future__ import annotations

import math
import sys
from typing import List


def primes_upto(n: int) -> List[int]:
    """Return all primes <= n using an odd-only sieve."""
    if n < 2:
        return []
    # sieve[i] represents whether (2*i+1) is prime
    size = n // 2 + 1
    sieve = bytearray(b"\x01") * size
    sieve[0] = 0  # 1 is not prime

    limit = int(math.isqrt(n))
    for p in range(3, limit + 1, 2):
        if sieve[p // 2]:
            start = (p * p) // 2
            sieve[start::p] = b"\x00" * ((size - start - 1) // p + 1)

    primes = [2]
    append = primes.append
    for i in range(1, size):
        if sieve[i]:
            append(2 * i + 1)
    return primes


def arithmetic_derivative(n: int) -> int:
    """
    Arithmetic derivative n' for small n (trial division factorization).
    Used for asserts only.
    """
    if n <= 1:
        return 0
    m = n
    res = 0

    # factor 2
    if (m & 1) == 0:
        a = 0
        while (m & 1) == 0:
            m >>= 1
            a += 1
        res += a * (n // 2)

    p = 3
    while p * p <= m:
        if m % p == 0:
            a = 0
            while m % p == 0:
                m //= p
                a += 1
            res += a * (n // p)
        p += 2

    if m > 1:
        # remaining prime factor with exponent 1
        res += n // m
    return res


def solve(N: int = 5 * 10**15) -> int:
    """
    Main solver.

    Let g(n) = gcd(n, n'). One can show g is multiplicative and for prime powers:
        g(p^a) = p^(a-1)           if p ∤ a
               = p^a              if p | a

    Define f(p^a) = g(p^a) - g(p^(a-1)). Then f is multiplicative and f(p)=0,
    so f(n) is supported only on powerful numbers (all prime exponents are 0 or >=2).

    Using Dirichlet convolution:
        g(n) = sum_{d|n} f(d)
    hence
        sum_{n<=N} g(n) = sum_{d<=N} f(d) * floor(N/d)

    The d that matter are powerful; we enumerate them implicitly with a DFS.
    """
    limit = math.isqrt(N)
    primes = primes_upto(limit)
    plen = len(primes)

    sys.setrecursionlimit(10000)

    def dfs(i0: int, L0: int) -> int:
        """
        Returns:
            sum_{d powerful, primes(d) >= primes[i0]} f(d) * floor(L0/d),
        excluding d=1.

        Called initially as dfs(0, N).
        """
        res = 0
        primes_local = primes  # local binding for speed

        for i in range(i0, plen):
            p = primes_local[i]
            q = p * p
            L = L0 // q
            if not L:
                break

            # Walk through exponents a >= 2 for this prime, updating g(p^a)
            # and thus c = f(p^a) = g(p^a) - g(p^(a-1)).
            e = 1  # we maintain e modulo p, with 0 meaning "multiple of p"
            g = 1
            while L:
                gp = g
                e += 1
                if e != 1:  # when e == 1, g doesn't change => f(p^a)=0
                    if e == p:
                        g *= q
                        e = 0
                    else:
                        g *= p
                    c = g - gp
                    res += c * L
                    if L > q:
                        res += c * dfs(i + 1, L)
                L //= p

        return res

    # subtract g(1)=1 to switch from sum_{k<=N} to sum_{1<k<=N}
    return N - 1 + dfs(0, N)


def _self_test() -> None:
    # Test value given in the problem statement:
    assert arithmetic_derivative(20) == 24

    # Extra sanity checks (small N) against known/bruteforce values.
    assert solve(10) == 17
    assert solve(100) == 440
    assert solve(1000) == 9249


if __name__ == "__main__":
    _self_test()
    print(solve())
