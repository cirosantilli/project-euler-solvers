#!/usr/bin/env python3
"""
Project Euler 362 - Squarefree factors

We need S(10^10) where:
- Fsf(n) = number of factorizations of n into squarefree factors > 1, order ignored.
- S(n) = sum_{k=2..n} Fsf(k)

This solution avoids iterating over all k <= 1e10 by:
1) Counting Fsf(n) from only the exponent multiset of n's prime factorization.
2) Enumerating possible exponent *sequences* (e1,e2,...,ek) for increasing primes p1 < p2 < ... < pk,
   and counting how many prime tuples realize those exponents with product <= N.
3) Using Lehmer's prime counting algorithm pi(x) to count primes quickly for large x.
"""

from __future__ import annotations

import math
from functools import lru_cache

TARGET_N = 10_000_000_000

# For Lehmer pi(x) up to 1e10, sieve up to x^(2/3) ~ 4.64e6 is sufficient.
SIEVE_LIMIT = 5_000_000

# Cache phi(x, s) only for small x to keep memory bounded.
PHI_CACHE_X_MAX = 10_000


def prime_sieve(n: int):
    """Return (primes, pi) for all <= n using a simple sieve."""
    bs = bytearray(b"\x01") * (n + 1)
    bs[:2] = b"\x00\x00"
    m = int(n**0.5)
    for i in range(2, m + 1):
        if bs[i]:
            step = i
            start = i * i
            bs[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    primes = [i for i in range(n + 1) if bs[i]]
    pi = [0] * (n + 1)
    c = 0
    for i in range(n + 1):
        if bs[i]:
            c += 1
        pi[i] = c
    return primes, pi


PRIMES, PI_SMALL = prime_sieve(SIEVE_LIMIT)


def iroot(n: int, k: int) -> int:
    """Floor of the k-th root of n (k>=1), exact for large ints."""
    if k == 1:
        return n
    if n <= 0:
        return 0
    x = int(round(n ** (1.0 / k)))
    while (x + 1) ** k <= n:
        x += 1
    while x**k > n:
        x -= 1
    return x


# ---- Lehmer prime counting pi(x) ----

_phi_cache: dict[tuple[int, int], int] = {}
_pi_cache: dict[int, int] = {}


def phi(x: int, s: int) -> int:
    """Count integers in [1..x] not divisible by the first s primes."""
    if s == 0:
        return x
    if s == 1:
        return x - x // 2
    if s == 2:
        # Inclusion-exclusion for primes 2 and 3
        return x - x // 2 - x // 3 + x // 6
    if x == 0:
        return 0

    if x < PHI_CACHE_X_MAX:
        key = (x, s)
        v = _phi_cache.get(key)
        if v is not None:
            return v
        v = phi(x, s - 1) - phi(x // PRIMES[s - 1], s - 1)
        _phi_cache[key] = v
        return v

    return phi(x, s - 1) - phi(x // PRIMES[s - 1], s - 1)


def pi_lehmer(x: int) -> int:
    """Lehmer's prime counting function pi(x)."""
    if x < SIEVE_LIMIT:
        return PI_SMALL[x]
    if x < 2:
        return 0
    v = _pi_cache.get(x)
    if v is not None:
        return v

    a = pi_lehmer(iroot(x, 4))
    b = pi_lehmer(int(math.isqrt(x)))
    c = pi_lehmer(iroot(x, 3))

    res = phi(x, a) + ((b + a - 2) * (b - a + 1)) // 2
    for i in range(a, b):
        w = x // PRIMES[i]
        res -= pi_lehmer(w)
        if i < c:
            lim = pi_lehmer(int(math.isqrt(w)))
            for j in range(i, lim):
                res -= pi_lehmer(w // PRIMES[j]) - j

    _pi_cache[x] = res
    return res


def prime_pi(x: int) -> int:
    """pi(x) wrapper."""
    if x < SIEVE_LIMIT:
        return PI_SMALL[x]
    return pi_lehmer(x)


# ---- Fsf(n) from exponent multiset ----


def bell_numbers(nmax: int) -> list[int]:
    """Bell numbers up to nmax via Stirling numbers of the 2nd kind."""
    S = [[0] * (nmax + 1) for _ in range(nmax + 1)]
    S[0][0] = 1
    for n in range(1, nmax + 1):
        for k in range(1, n + 1):
            S[n][k] = S[n - 1][k - 1] + k * S[n - 1][k]
    return [sum(S[n]) for n in range(nmax + 1)]


# Max distinct primes for n <= 1e10 is 10 (2*3*...*29 <= 1e10 < *31).
BELL = bell_numbers(10)

# Precompute subset bit lists for k <= 10.
SUBSET_BITS_BY_K: dict[int, list[tuple[int, ...]]] = {}
for k in range(1, 11):
    bits_list = []
    for mask in range(1, 1 << k):
        bits = tuple(i for i in range(k) if (mask >> i) & 1)
        bits_list.append(bits)
    SUBSET_BITS_BY_K[k] = bits_list


@lru_cache(maxsize=None)
def fsf_from_sorted_exponents(exps_sorted: tuple[int, ...]) -> int:
    """
    Count solutions to:
      for each prime i: sum_{A contains i} m_A = e_i
    where A ranges over nonempty subsets and m_A are nonnegative integers.

    This is the coefficient of:
      prod_{A != empty} 1/(1 - prod_{i in A} x_i)
    at x_i^{e_i}.
    """
    k = len(exps_sorted)
    if k == 0:
        return 0
    if k == 1:
        return 1
    if all(e == 1 for e in exps_sorted):
        return BELL[k]

    bases = [e + 1 for e in exps_sorted]
    mult = [1] * k
    for i in range(1, k):
        mult[i] = mult[i - 1] * bases[i - 1]
    total_states = mult[-1] * bases[-1]

    # digits[i][s] = i-th coordinate of state s
    digits = []
    for i in range(k):
        m = mult[i]
        base = bases[i]
        digits.append([(s // m) % base for s in range(total_states)])

    dp = [0] * total_states
    dp[0] = 1

    # For each subset (unbounded), standard increasing-order DP update:
    # dp[state] += dp[state - delta] if adding one subset stays within bounds.
    for bits in SUBSET_BITS_BY_K[k]:
        delta = 0
        for i in bits:
            delta += mult[i]
        for s in range(delta, total_states):
            prev = s - delta
            ok = True
            for i in bits:
                if digits[i][prev] >= exps_sorted[i]:
                    ok = False
                    break
            if ok:
                dp[s] += dp[prev]

    # target index in mixed radix
    target_idx = 0
    for i, e in enumerate(exps_sorted):
        target_idx += e * mult[i]
    return dp[target_idx]


def factor_exponents(n: int) -> list[int]:
    """Return exponent list for prime factorization of n (order irrelevant)."""
    exps = []
    x = n
    for p in PRIMES:
        if p * p > x:
            break
        if x % p == 0:
            e = 0
            while x % p == 0:
                x //= p
                e += 1
            exps.append(e)
    if x > 1:
        exps.append(1)
    return exps


# ---- Counting numbers with a fixed ordered exponent sequence ----


def min_suffix_product(exps: tuple[int, ...], start_idx: int) -> int:
    """Minimal product of consecutive primes starting at start_idx with exponents exps."""
    prod = 1
    for j, e in enumerate(exps):
        prod *= pow(PRIMES[start_idx + j], e)
    return prod


def count_prime_tuples(exps: tuple[int, ...], start_idx: int, limit: int) -> int:
    """
    Count tuples of distinct primes p0 < p1 < ... matching 'exps' such that
      prod_i p_i^{exps[i]} <= limit
    where p0 is PRIMES[start_idx] or larger.

    Uses recursion + early break using minimal achievable suffix product.
    """
    if not exps:
        return 1
    if limit < 2:
        return 0

    if len(exps) == 1:
        e = exps[0]
        max_p = limit if e == 1 else iroot(limit, e)
        if max_p < 2:
            return 0
        res = prime_pi(max_p) - start_idx
        return res if res > 0 else 0

    e0 = exps[0]
    suffix = exps[1:]
    total = 0

    # Ensure we have enough primes left in PRIMES to evaluate min_suffix_product safely.
    max_i = len(PRIMES) - len(exps)
    for i in range(start_idx, max_i + 1):
        p = PRIMES[i]
        p_pow = pow(p, e0)
        if p_pow > limit:
            break
        new_limit = limit // p_pow
        if min_suffix_product(suffix, i + 1) > new_limit:
            break
        total += count_prime_tuples(suffix, i + 1, new_limit)
    return total


# ---- Enumerate all exponent sequences that can occur for n <= N ----

FIRST_10_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29)


def generate_exponent_sequences(limit: int) -> list[tuple[int, ...]]:
    """
    Generate all ordered exponent sequences (e1, e2, ..., ek), k>=1,
    such that using the smallest k primes yields a product <= limit.
    This is a necessary and sufficient existence condition.
    """
    seqs: list[tuple[int, ...]] = []

    def rec(i: int, prod: int, seq: list[int]) -> None:
        if seq:
            seqs.append(tuple(seq))
        if i >= len(FIRST_10_PRIMES):
            return
        p = FIRST_10_PRIMES[i]
        pe = p
        e = 1
        while prod * pe <= limit:
            seq.append(e)
            rec(i + 1, prod * pe, seq)
            seq.pop()
            e += 1
            pe *= p

    rec(0, 1, [])
    return seqs


def S(limit: int) -> int:
    """Compute S(limit) = sum_{k=2..limit} Fsf(k)."""
    seqs = generate_exponent_sequences(limit)
    total = 0
    for exps in seqs:
        # Fsf depends only on multiset of exponents
        pattern = tuple(sorted(exps, reverse=True))
        w = fsf_from_sorted_exponents(pattern)
        c = count_prime_tuples(exps, 0, limit)
        total += w * c
    return total


def main() -> None:
    # Asserts from the problem statement
    assert (
        fsf_from_sorted_exponents(tuple(sorted(factor_exponents(54), reverse=True)))
        == 2
    )
    assert S(100) == 193

    print(S(TARGET_N))


if __name__ == "__main__":
    main()
