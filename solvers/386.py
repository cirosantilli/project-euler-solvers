#!/usr/bin/env python3
"""
Project Euler 386: Maximum length of an antichain
https://projecteuler.net/problem=386

Optimized Python (no external libraries):
- Uses an odd-only sieve up to 'limit' to get all primes and allow O(log n) pi(x) via bisect.
- Enumerates feasible exponent sequences and counts how many n<=limit realize each pattern.
- Computes N(n) as a middle coefficient of Π (1+x+...+x^{a_i}).

If run with no input, uses limit=10^8 and asserts the known Project Euler answer.
"""

from __future__ import annotations

import sys
import math
import bisect
from functools import lru_cache
from array import array


# ----------------------------
# Problem statement examples
# ----------------------------

def is_antichain(n: int, subset: list[int]) -> bool:
    """True iff subset is an antichain in S(n) under divisibility."""
    for x in subset:
        if x <= 0 or n % x != 0:
            return False
    m = len(subset)
    for i in range(m):
        a = subset[i]
        for j in range(i + 1, m):
            b = subset[j]
            if a % b == 0 or b % a == 0:
                return False
    return True


# Examples from the statement:
assert is_antichain(30, [2, 5, 6]) is False
assert is_antichain(30, [2, 3, 5]) is True


# ----------------------------
# Prime sieve up to limit (odd-only)
# ----------------------------

def sieve_primes_upto(n: int) -> array:
    """Return array('I') of all primes <= n. (Odd-only bytearray sieve.)"""
    if n < 2:
        return array("I")
    if n == 2:
        return array("I", [2])

    # Represent odd number (2*i+1) by index i. Size includes n if n is odd.
    size = (n // 2) + 1
    sieve = bytearray(b"\x01") * size
    sieve[0] = 0  # 1 is not prime

    r = int(math.isqrt(n))
    # i corresponds to p = 2*i+1, so p<=r => i<=r//2
    max_i = r // 2
    for i in range(1, max_i + 1):
        if sieve[i]:
            p = 2 * i + 1
            start = (p * p) // 2
            sieve[start::p] = b"\x00" * (((size - 1 - start) // p) + 1)

    primes = array("I", [2])
    append = primes.append
    find = sieve.find

    idx = find(1, 1)
    while idx != -1:
        append(2 * idx + 1)
        idx = find(1, idx + 1)

    return primes


# ----------------------------
# Integer k-th root
# ----------------------------

def iroot(x: int, k: int) -> int:
    """floor(x ** (1/k)) with safe adjustment (k>=1)."""
    if k <= 1 or x < 2:
        return x
    if k == 2:
        return int(math.isqrt(x))
    # float seed + fix-up
    r = int(x ** (1.0 / k))
    if r < 1:
        r = 1
    while (r + 1) ** k <= x:
        r += 1
    while r ** k > x:
        r -= 1
    return r


# ----------------------------
# N(n) from exponent multiset
# ----------------------------

@lru_cache(maxsize=None)
def N_from_exponents(exps_sorted: tuple[int, ...]) -> int:
    """
    For n = Π p_i^{a_i}, N(n) is the maximum size of a rank layer in the divisor poset.
    Rank is Ω(d)=sum exponents in divisor, and the rank generating polynomial is:
        Π (1 + x + ... + x^{a_i})
    This polynomial is palindromic, so the maximum occurs at:
        half = floor(sum a_i / 2)
    Therefore N(n) is coefficient of x^half.
    """
    exps = exps_sorted
    half = sum(exps) // 2
    dp = [0] * (half + 1)
    dp[0] = 1

    # Convolution with (1 + x + ... + x^a) via sliding window sum
    for a in exps:
        new = [0] * (half + 1)
        window = 0
        for t in range(half + 1):
            window += dp[t]
            drop = t - (a + 1)
            if drop >= 0:
                window -= dp[drop]
            new[t] = window
        dp = new

    return dp[half]


# ----------------------------
# Count numbers with a fixed exponent pattern
# ----------------------------

def count_sequence(limit: int, primes: array, iter_end: int, exps: tuple[int, ...]) -> int:
    """
    Count integers <= limit with factorization:
        n = p1^e1 * p2^e2 * ... * pk^ek, with p1 < p2 < ... < pk
    where exps = (e1,...,ek) is in increasing-prime order.

    For k>=2, all non-last recursion levels only iterate primes <= sqrt(limit),
    so we restrict iteration to primes[0:iter_end].
    """
    k = len(exps)
    if k == 0:
        return 1

    suffix = [0] * (k + 1)
    for i in range(k - 1, -1, -1):
        suffix[i] = suffix[i + 1] + exps[i]

    bisr = bisect.bisect_right

    @lru_cache(maxsize=None)
    def rec(pos: int, prev_idx: int, rem: int) -> int:
        # prev_idx is index in primes of last chosen prime; -1 means "previous prime = 1"
        if pos == k:
            return 1

        e = exps[pos]

        if pos == k - 1:
            p_max = iroot(rem, e)
            hi = bisr(primes, p_max)
            start = prev_idx + 1
            return hi - start if hi > start else 0

        # Strong bound: remaining primes are all >= next prime p,
        # so remaining product >= p^(sum of remaining exponents).
        p_max = iroot(rem, suffix[pos])
        end = bisr(primes, p_max, 0, iter_end)
        start = prev_idx + 1
        if start >= end:
            return 0

        total = 0
        # Iterate candidate primes for this position (all are within primes[:iter_end])
        for idx in range(start, end):
            p = primes[idx]
            p_pow = p if e == 1 else pow(p, e)
            if p_pow > rem:
                break
            total += rec(pos + 1, idx, rem // p_pow)
        return total

    return rec(0, -1, limit)


# ----------------------------
# Main solve
# ----------------------------

def solve(limit: int = 10**8) -> int:
    """
    Compute sum_{1<=n<=limit} N(n).
    """
    if limit < 1:
        return 0

    primes = sieve_primes_upto(limit)
    # For k>=2 recursion levels, primes never exceed sqrt(limit)
    iter_end = bisect.bisect_right(primes, int(math.isqrt(limit)))

    # Bound on number of distinct prime factors for limit<=1e8 is 8 (2*...*19 < 1e8; *23 > 1e8)
    min_primes = [2, 3, 5, 7, 11, 13, 17, 19]

    sequences: list[tuple[int, ...]] = []

    # Enumerate feasible exponent sequences using minimal consecutive primes for pruning
    def gen(pos: int, prod: int, seq: list[int]) -> None:
        if seq:
            sequences.append(tuple(seq))
        if pos == len(min_primes):
            return
        p = min_primes[pos]
        e = 1
        pe = p
        while True:
            new_prod = prod * pe
            if new_prod > limit:
                break
            seq.append(e)
            gen(pos + 1, new_prod, seq)
            seq.pop()
            e += 1
            pe *= p

    gen(0, 1, [])

    # Cache counts per exponent sequence (many repeats are unlikely, but cheap)
    count_cache: dict[tuple[int, ...], int] = {}

    total = 1  # N(1) = 1
    for exps in sequences:
        cnt = count_cache.get(exps)
        if cnt is None:
            cnt = count_sequence(limit, primes, iter_end, exps)
            count_cache[exps] = cnt
        if cnt:
            total += cnt * N_from_exponents(tuple(sorted(exps)))
    return total


def _read_limit() -> int:
    data = sys.stdin.read().strip().split()
    if not data:
        return 10**8
    return int(data[0])


if __name__ == "__main__":
    lim = _read_limit()
    ans = solve(lim)
    # Sanity check for the original Project Euler target
    if lim == 10**8:
        assert ans == 528755790
    print(ans)
