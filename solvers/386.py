#!/usr/bin/env python3
"""
Project Euler 386: Maximum length of an antichain
https://projecteuler.net/problem=386

No external libraries are used.
"""

from __future__ import annotations

import sys
import math
import bisect
from functools import lru_cache
from array import array


# ----------------------------
# Helpers: primes + pi(x)
# ----------------------------

def sieve_primes(n: int) -> tuple[list[int], bytearray]:
    """Return (primes <= n, is_prime bytearray of length n+1)."""
    is_prime = bytearray(b"\x01") * (n + 1)
    if n >= 0:
        is_prime[0:1] = b"\x00"
    if n >= 1:
        is_prime[1:2] = b"\x00"

    # clear even numbers > 2
    for i in range(4, n + 1, 2):
        is_prime[i] = 0

    limit = int(n ** 0.5)
    for p in range(3, limit + 1, 2):
        if is_prime[p]:
            step = p * 2
            start = p * p
            is_prime[start:n + 1:step] = b"\x00" * (((n - start) // step) + 1)

    primes = [2] + [i for i in range(3, n + 1, 2) if is_prime[i]]
    return primes, is_prime


def build_pi_prefix(is_prime: bytearray) -> array:
    """pi_prefix[x] = number of primes <= x, for all 0<=x<=len(is_prime)-1."""
    n = len(is_prime) - 1
    pi = array("I", [0]) * (n + 1)
    c = 0
    for i in range(n + 1):
        if is_prime[i]:
            c += 1
        pi[i] = c
    return pi


def iroot(x: int, k: int) -> int:
    """floor(x ** (1/k)) with safe adjustment."""
    if x < 2:
        return x
    r = int(round(x ** (1.0 / k)))
    if r < 1:
        r = 1
    while (r + 1) ** k <= x:
        r += 1
    while r ** k > x:
        r -= 1
    return r


# Precompute for Lehmer prime counting
MAXN = 2_000_000
PRIMES, IS_PRIME = sieve_primes(MAXN)
PI_PREFIX = build_pi_prefix(IS_PRIME)

# Small wheel for fast phi(x, s)
WHEEL_M = 6  # primes: 2,3,5,7,11,13
WHEEL_P = 1
for i in range(WHEEL_M):
    WHEEL_P *= PRIMES[i]

# phi_mod[s][r] = phi(r, s) for 0<=r<WHEEL_P and 0<=s<=WHEEL_M
PHI_MOD = [array("I", [0]) * WHEEL_P for _ in range(WHEEL_M + 1)]
for r in range(WHEEL_P):
    PHI_MOD[0][r] = r
for s in range(1, WHEEL_M + 1):
    p = PRIMES[s - 1]
    prev = PHI_MOD[s - 1]
    cur = PHI_MOD[s]
    for r in range(WHEEL_P):
        cur[r] = prev[r] - prev[r // p]

PHI_BLOCK = [PHI_MOD[s][WHEEL_P - 1] for s in range(WHEEL_M + 1)]


@lru_cache(maxsize=None)
def phi(x: int, s: int) -> int:
    """
    phi(x, s) = count of integers n <= x that are not divisible by any of the first s primes.
    """
    if s == 0:
        return x
    if s <= WHEEL_M:
        return (x // WHEEL_P) * PHI_BLOCK[s] + PHI_MOD[s][x % WHEEL_P]
    return phi(x, s - 1) - phi(x // PRIMES[s - 1], s - 1)


@lru_cache(maxsize=None)
def prime_pi(x: int) -> int:
    """Lehmer prime counting: number of primes <= x."""
    x = int(x)
    if x < MAXN:
        return PI_PREFIX[x]
    if x < 2:
        return 0

    a = prime_pi(iroot(x, 4))
    b = prime_pi(int(math.isqrt(x)))
    c = prime_pi(iroot(x, 3))

    res = phi(x, a) + ((b + a - 2) * (b - a + 1)) // 2

    for i in range(a, b):
        w = x // PRIMES[i]
        res -= prime_pi(w)
        if i < c:
            lim = prime_pi(int(math.isqrt(w)))
            for j in range(i, lim):
                res -= prime_pi(w // PRIMES[j]) - j
    return res


# ----------------------------
# Antichains for n
# ----------------------------

def is_antichain(n: int, subset: list[int]) -> bool:
    """Return True iff subset is an antichain in S(n) under divisibility."""
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


# Asserts for the examples given in the problem statement:
assert is_antichain(30, [2, 5, 6]) is False
assert is_antichain(30, [2, 3, 5]) is True


# ----------------------------
# N(n) from prime exponents
# ----------------------------

@lru_cache(maxsize=None)
def N_from_exponents(exps_sorted: tuple[int, ...]) -> int:
    """
    For n = Π p_i^{a_i}, N(n) equals the maximum number of divisors on any rank.
    Because Π (1+x+...+x^{a_i}) is palindromic, the maximum occurs at half the degree:
        half = floor( (sum a_i) / 2 )
    Thus N(n) is the coefficient of x^half in that polynomial.
    """
    exps = list(exps_sorted)
    half = sum(exps) // 2

    # dp[t] = coefficient of x^t so far (only keep up to 'half')
    dp = [0] * (half + 1)
    dp[0] = 1

    # Convolution with (1 + x + ... + x^a) using a sliding window prefix sum
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


def count_sequence(limit: int, exps: tuple[int, ...]) -> int:
    """
    Count integers <= limit whose prime factorization has exponents exactly `exps`
    in increasing-prime order:
        n = p1^e1 * p2^e2 * ... * pk^ek, with p1 < p2 < ... < pk.
    """
    k = len(exps)
    suffix = [0] * (k + 1)
    for i in range(k - 1, -1, -1):
        suffix[i] = suffix[i + 1] + exps[i]

    @lru_cache(maxsize=None)
    def rec(pos: int, prev_prime: int, rem: int) -> int:
        if pos == k:
            return 1

        if pos == k - 1:
            p_max = iroot(rem, exps[pos])
            if p_max <= prev_prime:
                return 0
            # primes in (prev_prime, p_max]
            return prime_pi(p_max) - prime_pi(prev_prime)

        # Strong bound: remaining primes are all >= current prime p,
        # so product >= p^(sum remaining exponents).
        sum_rem = suffix[pos]
        p_max = iroot(rem, sum_rem)
        if p_max <= prev_prime:
            return 0

        start = bisect.bisect_right(PRIMES, prev_prime)
        end = bisect.bisect_right(PRIMES, p_max)
        total = 0
        e = exps[pos]
        for idx in range(start, end):
            p = PRIMES[idx]
            p_pow = p ** e
            if p_pow > rem:
                break
            total += rec(pos + 1, p, rem // p_pow)
        return total

    return rec(0, 1, limit)


def solve(limit: int = 10**8) -> int:
    """
    Compute sum_{1<=n<=limit} N(n).
    """
    if limit < 1:
        return 0

    # For limit <= 1e8 we always have at most 8 distinct prime factors
    # (since 2*3*5*7*11*13*17*19 < 1e8 but multiplying by 23 exceeds it).
    min_primes = [2, 3, 5, 7, 11, 13, 17, 19]

    sequences: list[tuple[int, ...]] = []

    def gen(pos: int, prod: int, seq: list[int]) -> None:
        if seq:
            sequences.append(tuple(seq))
        if pos == len(min_primes):
            return
        p = min_primes[pos]
        e = 1
        while True:
            new_prod = prod * (p ** e)
            if new_prod > limit:
                break
            seq.append(e)
            gen(pos + 1, new_prod, seq)
            seq.pop()
            e += 1

    gen(0, 1, [])

    total = 1  # N(1) = 1
    for exps in sequences:
        cnt = count_sequence(limit, exps)
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
    # (Optional sanity check for the original problem)
    if lim == 10**8:
        assert ans == 528755790
    print(ans)
