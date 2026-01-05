#!/usr/bin/env python3
"""
Project Euler 386: Maximum Length of an Antichain

Let n be a positive integer and S(n) be the set of divisors of n.
N(n) is the maximum size of an antichain in the divisibility poset of S(n).
Compute sum_{1 <= n <= 1e8} N(n).

Key facts:
- If n = Π p_i^{a_i}, then divisors correspond to exponent vectors (e_i) with 0<=e_i<=a_i.
- The poset is a product of chains, ranked by sum(e_i).
- N(n) equals the maximum coefficient of Π (1 + x + ... + x^{a_i}).

We avoid iterating n up to 1e8 by:
- Enumerating feasible ordered exponent sequences (a_1, ..., a_k) for the prime factorization
  (ordered by increasing primes).
- Counting, for each exponent sequence, how many k-tuples of increasing primes satisfy
  Π p_i^{a_i} <= limit.
- Using a fast prime counting function π(x) (Lehmer) so we never need primes up to 1e8.
"""

from __future__ import annotations

import math
from bisect import bisect_right
from functools import lru_cache
from typing import List, Tuple


def _iroot(n: int, k: int) -> int:
    """Floor of the k-th root of n (k>=1)."""
    if k <= 1:
        return n
    if k == 2:
        return math.isqrt(n)
    # Float-based estimate + correction (safe for n up to ~1e12+ with small k)
    x = int(n ** (1.0 / k))
    while (x + 1) ** k <= n:
        x += 1
    while x**k > n:
        x -= 1
    return x


def _sieve_with_pi(n: int) -> Tuple[List[int], List[int]]:
    """Return (primes <= n, pi[0..n] where pi[x]=#primes<=x)."""
    if n < 2:
        return [], [0] * (n + 1)
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    r = int(math.isqrt(n))
    for p in range(2, r + 1):
        if sieve[p]:
            start = p * p
            step = p
            sieve[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)

    primes = [i for i in range(2, n + 1) if sieve[i]]
    pi = [0] * (n + 1)
    c = 0
    for i in range(n + 1):
        if sieve[i]:
            c += 1
        pi[i] = c
    return primes, pi


def _make_lehmer_pi(limit: int):
    """
    Build a Lehmer prime-counting function pi(x) valid for x up to 'limit'.

    For limit=1e8, we sieve only up to limit^(2/3) ~ 2.2e5.
    """
    sieve_n = int(round(limit ** (2.0 / 3.0))) + 20
    primes, pi_small = _sieve_with_pi(sieve_n)
    P = primes  # 0-based primes list

    @lru_cache(maxsize=None)
    def phi(x: int, a: int) -> int:
        # Count integers <= x not divisible by first a primes.
        if a == 0:
            return x
        if a == 1:
            return x - x // 2
        if a == 2:
            # Inclusion-exclusion for primes 2 and 3
            return x - x // 2 - x // 3 + x // 6
        return phi(x, a - 1) - phi(x // P[a - 1], a - 1)

    @lru_cache(maxsize=None)
    def lehmer_pi(x: int) -> int:
        if x < len(pi_small):
            return pi_small[x]

        x13 = _iroot(x, 3)
        x12 = math.isqrt(x)
        x14 = _iroot(x, 4)

        a = lehmer_pi(x14)
        b = lehmer_pi(x12)
        c = lehmer_pi(x13)

        # Main Lehmer formula (0-based indices adaptation)
        res = phi(x, a) + ((b + a - 2) * (b - a + 1)) // 2

        for i in range(a, b):
            p = P[i]
            w = x // p
            res -= lehmer_pi(w)

            if i < c:
                lim = lehmer_pi(math.isqrt(w))
                for j in range(i, lim):
                    res -= lehmer_pi(w // P[j]) - j
        return res

    return lehmer_pi, primes


def _max_antichain_from_exponents(exps: Tuple[int, ...], cache: dict) -> int:
    """
    Given the prime exponents of n (order irrelevant), compute N(n) as the
    maximum coefficient of Π (1 + x + ... + x^{a_i}).
    """
    key = tuple(sorted(exps))
    if key in cache:
        return cache[key]

    # DP over small total degree (<=26 for n<=1e8)
    coeffs = [1]
    for a in key:
        nxt = [0] * (len(coeffs) + a)
        for i, v in enumerate(coeffs):
            for s in range(a + 1):
                nxt[i + s] += v
        coeffs = nxt

    ans = max(coeffs) if key else 1
    cache[key] = ans
    return ans


def solve(limit: int = 100_000_000) -> int:
    lehmer_pi, primes_all = _make_lehmer_pi(limit)

    # We only ever iterate primes up to sqrt(limit), due to a tight bound in the DFS.
    max_iter = math.isqrt(limit)
    primes_iter = [p for p in primes_all if p <= max_iter]
    upper_idx = lambda x: bisect_right(primes_iter, x)

    # Enumerate all feasible ordered exponent sequences (a_1,...,a_k) for primes p_1<...<p_k.
    # Feasibility check: smallest primes 2,3,5,... with those exponents must fit in 'limit'.
    min_primes = (
        2,
        3,
        5,
        7,
        11,
        13,
        17,
        19,
    )  # enough for n<=1e8 (max distinct primes is 8)
    exponent_seqs: List[Tuple[int, ...]] = []

    def gen(pos: int, prod: int, seq: List[int]) -> None:
        if seq:
            exponent_seqs.append(tuple(seq))
        if pos == len(min_primes):
            return
        p = min_primes[pos]
        e = 1
        p_pow = p
        while prod * p_pow <= limit:
            seq.append(e)
            gen(pos + 1, prod * p_pow, seq)
            seq.pop()
            e += 1
            p_pow *= p

    gen(0, 1, [])

    # Cache for N(n) by multiset of exponents
    n_cache: dict = {}

    total = 1  # n=1 -> N(1)=1

    for exps in exponent_seqs:
        k = len(exps)

        # Tight pruning bound:
        # At position 'pos', remaining primes are >= current prime, so
        # p_pos^(sum(exps[pos:])) <= rem is necessary.
        suffix_sum = [0] * (k + 1)
        for i in range(k - 1, -1, -1):
            suffix_sum[i] = suffix_sum[i + 1] + exps[i]

        @lru_cache(maxsize=None)
        def dfs(pos: int, prev_idx: int, rem: int) -> int:
            if pos == k:
                return 1
            e = exps[pos]

            if pos == k - 1:
                # last prime: count with π()
                max_p = _iroot(rem, e)
                prev_p = primes_iter[prev_idx] if prev_idx >= 0 else 0
                return lehmer_pi(max_p) - lehmer_pi(prev_p)

            max_p = _iroot(rem, suffix_sum[pos])  # crucial tightening
            end = upper_idx(max_p)
            start = prev_idx + 1
            if start >= end:
                return 0

            acc = 0
            for idx in range(start, end):
                p = primes_iter[idx]
                if e == 1:
                    p_pow = p
                elif e == 2:
                    p_pow = p * p
                elif e == 3:
                    p_pow = p * p * p
                else:
                    p_pow = pow(p, e)
                acc += dfs(pos + 1, idx, rem // p_pow)
            return acc

        count_numbers = dfs(0, -1, limit)
        total += count_numbers * _max_antichain_from_exponents(exps, n_cache)

    return total


def _self_test() -> None:
    # Problem statement has no numeric test cases; these are small brute-force spot checks.
    assert solve(1) == 1
    assert solve(10) == 12
    assert solve(30) == 44
    assert solve(100) == 178
    assert solve(1000) == 2385


if __name__ == "__main__":
    _self_test()
    # Optional input: a different upper bound (same format as other Euler scripts)
    import sys

    data = sys.stdin.read().strip()
    n = int(data) if data else 100_000_000
    print(solve(n))
