#!/usr/bin/env python3
"""
Project Euler 578: Integers with Decreasing Prime Powers

An integer n is a "decreasing prime power" if, writing
    n = p1^a1 * p2^a2 * ... * pk^ak   with p1 < p2 < ... < pk,
we have
    a1 >= a2 >= ... >= ak.
(Also n = 1 counts.)

Let C(N) be the number of such integers <= N. The problem statement gives:
    C(100)   = 94
    C(10^6)  = 922052
We compute C(10^13).

Core approach:
- Enumerate the "powerful part" (prime powers with exponent >= 2) via recursion.
- Whenever the remaining max exponent becomes 1, the rest must be squarefree.
- Count squarefree tails using the Möbius function:
      Q(x) = sum_{i<=sqrt(x)} mu(i) * floor(x / i^2),
  grouped in O(#distinct floor(x / i^2)) using prefix sums of mu.
- To enforce a minimum prime (all primes >= PRIMES[start_idx]) in the tail, use a
  smallest-prime-factor decomposition:
      f(x, a) = Q(x) - sum_{i<a} f(x / p_i, i+1),
  where the subtracted term counts squarefree numbers whose smallest prime is p_i.

No external libraries are used (standard library only).
"""

from __future__ import annotations

import math
import sys
from array import array
from functools import lru_cache

N_TARGET = 10**13
SIEVE_LIMIT = int(math.isqrt(N_TARGET)) + 5000  # primes needed up to sqrt(N)


def build_primes_and_mobius(n: int):
    """Linear sieve up to n. Returns (primes, mu, prefix_mu)."""
    lp = array("I", [0]) * (n + 1)
    mu = array("b", [0]) * (n + 1)
    primes: list[int] = []
    mu[1] = 1

    for i in range(2, n + 1):
        if lp[i] == 0:
            lp[i] = i
            primes.append(i)
            mu[i] = -1
        for p in primes:
            ip = i * p
            if ip > n:
                break
            lp[ip] = p
            if p == lp[i]:
                mu[ip] = 0
                break
            mu[ip] = -mu[i]

    pref = array("i", [0]) * (n + 1)
    s = 0
    for i in range(1, n + 1):
        s += int(mu[i])
        pref[i] = s

    return primes, mu, pref


PRIMES, MU, PREFIX_MU = build_primes_and_mobius(SIEVE_LIMIT)


@lru_cache(maxsize=None)
def squarefree_upto(x: int) -> int:
    """
    Q(x): number of squarefree integers <= x (including 1).

    Q(x) = sum_{i=1..floor(sqrt(x))} mu(i) * floor(x / i^2)

    Group i where floor(x / i^2) is constant, using prefix sums of mu.
    """
    if x <= 0:
        return 0
    r = int(math.isqrt(x))
    pref = PREFIX_MU
    res = 0
    i = 1
    while i <= r:
        t = x // (i * i)
        j = int(math.isqrt(x // t))
        res += t * (pref[j] - pref[i - 1])
        i = j + 1
    return res


@lru_cache(maxsize=None)
def squarefree_min_prime_index(x: int, start_idx: int) -> int:
    """
    f(x, start_idx): count of squarefree n <= x whose prime factors are all >= PRIMES[start_idx].
    Includes n=1.

    Using smallest-prime-factor decomposition over excluded primes:
      f(x, a) = Q(x) - sum_{i=0..a-1} f(x / p_i, i+1),
    where the subtracted term counts squarefree numbers with smallest prime exactly p_i.
    """
    if x <= 0:
        return 0
    if x == 1:
        return 1
    if start_idx == 0:
        return squarefree_upto(x)

    # If the minimum allowed prime is already > x, only 1 is possible.
    if start_idx < len(PRIMES) and PRIMES[start_idx] > x:
        return 1

    total = squarefree_upto(x)
    primes = PRIMES

    # Subtract contributions for excluded primes p_0..p_{start_idx-1}.
    for i in range(start_idx):
        p = primes[i]
        if p > x:
            break  # x//p == 0 hence term would be 0
        total -= squarefree_min_prime_index(x // p, i + 1)

    return total


def max_possible_exponent(n: int) -> int:
    """Maximum e such that 2^e <= n."""
    e = 0
    v = 1
    while v * 2 <= n:
        v *= 2
        e += 1
    return e


@lru_cache(maxsize=None)
def count_dpowers(limit: int, start_idx: int, max_exp: int) -> int:
    """
    Count decreasing-prime-power integers <= limit using primes >= PRIMES[start_idx],
    with exponents non-increasing and bounded by max_exp.

    If max_exp == 1, the remainder must be squarefree:
      => squarefree_min_prime_index(limit, start_idx)

    Otherwise:
      - Count all exp=1 tails (squarefree numbers from allowed primes)
      - For each prime p and exponent e in [2..max_exp], include p^e and recurse with max_exp := e.
    """
    if limit <= 0:
        return 0
    if limit == 1:
        return 1
    if max_exp <= 1:
        return squarefree_min_prime_index(limit, start_idx)

    res = squarefree_min_prime_index(limit, start_idx)

    primes = PRIMES
    for i in range(start_idx, len(primes)):
        p = primes[i]
        p2 = p * p
        if p2 > limit:
            break
        pe = p2
        e = 2
        while e <= max_exp and pe <= limit:
            res += count_dpowers(limit // pe, i + 1, e)
            e += 1
            pe *= p

    return res


def C(n: int) -> int:
    return count_dpowers(n, 0, max_possible_exponent(n))


def main(argv: list[str]) -> None:
    # Required asserts from the problem statement
    assert C(100) == 94
    assert C(10**6) == 922052

    if len(argv) == 2:
        n = int(argv[1])
        print(C(n))
        return

    print(C(N_TARGET))


if __name__ == "__main__":
    sys.setrecursionlimit(1_000_000)
    main(sys.argv)
