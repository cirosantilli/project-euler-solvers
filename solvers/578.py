#!/usr/bin/env python3
"""
Project Euler 578: Integers with Decreasing Prime Powers

C(N) counts integers n <= N whose prime factorization
    n = p1^a1 * p2^a2 * ... * pk^ak  (p1 < p2 < ... < pk)
satisfies a1 >= a2 >= ... >= ak, and includes n = 1.

Key idea:
  - If the remaining maximum exponent becomes 1, the rest of the number must be
    squarefree (all exponents are 1), with primes larger than the last chosen prime.
  - Squarefree counts up to x can be computed using the Möbius function:
        Q(x) = sum_{i=1..floor(sqrt(x))} mu(i) * floor(x / i^2)
    and grouped in O(number of distinct floor(x / i^2)) using prefix sums of mu.

This avoids the need for a heavy prime-counting function π(x) at 10^13.
"""

from __future__ import annotations

import math
import sys
from array import array
from functools import lru_cache


N_TARGET = 10**13
SIEVE_LIMIT = int(math.isqrt(N_TARGET)) + 5000  # primes needed for exponent>=2


def build_primes_and_mobius(n: int):
    """
    Linear sieve up to n producing:
      - primes list (ascending)
      - Möbius mu[0..n]
      - prefix sums M[k] = sum_{i<=k} mu[i]
    """
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
    Q(x) = number of squarefree integers <= x (including 1).

    Uses:
      Q(x) = sum_{i=1..floor(sqrt(x))} mu(i) * floor(x / i^2)

    Grouping trick:
      For t = floor(x / i^2), the maximum i with same t is floor(sqrt(x / t)).
      With prefix sums of mu we can accumulate ranges in O(#groups).
    """
    if x <= 0:
        return 0
    r = int(math.isqrt(x))
    i = 1
    res = 0
    pref = PREFIX_MU
    while i <= r:
        t = x // (i * i)
        j = int(math.isqrt(x // t))
        res += t * (pref[j] - pref[i - 1])
        i = j + 1
    return res


# For small start index we can compute "tail squarefree" by subtracting smallest-prime-factor
# contributions from Q(x), which avoids enumerating huge prime ranges.
SMALL_START_LIMIT = 10


@lru_cache(maxsize=None)
def squarefree_enum(x: int, start_idx: int) -> int:
    """
    Explicitly count squarefree products of primes PRIMES[start_idx:] with product <= x.
    Includes the empty product (1). Used only when x is small and start_idx is large.
    """
    if x <= 1:
        return 1
    res = 1
    primes = PRIMES
    for i in range(start_idx, len(primes)):
        p = primes[i]
        if p > x:
            break
        res += squarefree_enum(x // p, i + 1)
    return res


@lru_cache(maxsize=None)
def squarefree_with_min_prime_index(x: int, start_idx: int) -> int:
    """
    Count of squarefree numbers <= x whose prime factors are all >= PRIMES[start_idx].
    Includes 1.

    For small start_idx:
      result = Q(x) - sum_{i < start_idx} count(numbers whose smallest prime factor is PRIMES[i])
    Each squarefree number has a unique smallest prime factor p:
      n = p * m, where m is squarefree and all prime factors > p.
    So the count for smallest prime p=PRIMES[i] is squarefree_with_min_prime_index(x//p, i+1).

    For large start_idx, x is small in our recursion and we enumerate.
    """
    if x <= 1:
        return 1

    if start_idx <= SMALL_START_LIMIT:
        total = squarefree_upto(x)
        for i in range(start_idx):
            total -= squarefree_with_min_prime_index(x // PRIMES[i], i + 1)
        return total

    return squarefree_enum(x, start_idx)


def max_possible_exponent(n: int) -> int:
    """Maximum e such that 2^e <= n."""
    e = 0
    v = 1
    while v * 2 <= n:
        v *= 2
        e += 1
    return e


@lru_cache(maxsize=None)
def count_decreasing_prime_powers(limit: int, start_idx: int, max_exp: int) -> int:
    """
    Count numbers <= limit using primes PRIMES[start_idx:] with exponents nonincreasing
    and each exponent <= max_exp.

    If max_exp == 1: the rest must be squarefree => squarefree_with_min_prime_index(limit, start_idx).

    Otherwise:
      - Count all exponent-1 completions (squarefree tail)
      - For every next prime p and exponent e in [2..max_exp] with p^e <= limit,
        take p^e and recurse with:
          limit' = limit // p^e
          start' = index(p) + 1
          max_exp' = e
    """
    if limit <= 1:
        return 1
    if max_exp <= 1:
        return squarefree_with_min_prime_index(limit, start_idx)

    res = squarefree_with_min_prime_index(limit, start_idx)

    primes = PRIMES
    for i in range(start_idx, len(primes)):
        p = primes[i]
        p2 = p * p
        if p2 > limit:
            break

        pe = p2
        e = 2
        while e <= max_exp and pe <= limit:
            res += count_decreasing_prime_powers(limit // pe, i + 1, e)
            e += 1
            pe *= p

    return res


def C(n: int) -> int:
    return count_decreasing_prime_powers(n, 0, max_possible_exponent(n))


def main() -> None:
    # Required test values from the problem statement
    assert C(100) == 94
    assert C(10**6) == 922052

    print(C(N_TARGET))


if __name__ == "__main__":
    sys.setrecursionlimit(1_000_000)
    main()

