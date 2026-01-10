#!/usr/bin/env python3
"""
Project Euler 548 - Gozinta Chains

A gozinta chain for n is a sequence {1, a, b, ..., n} where each element properly
divides the next. Let g(n) be the number of gozinta chains for n.

We need: sum of n <= 10^16 such that g(n) = n.

Key observation:
A chain 1=a0<a1<...<ak=n corresponds to the ordered factorization
(n1, n2, ..., nk) where ni = ai/ai-1 (>1) and n1*n2*...*nk = n.
So g(n) equals the number of ordered factorizations of n (factors > 1).
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple

LIMIT = 10**16

# For n having prime-exponent sum S, we always have g(n) >= g(p^S) = 2^(S-1).
# Therefore if g(n)=n<=LIMIT then 2^(S-1) <= LIMIT, hence S <= LIMIT.bit_length().
MAX_EXP_SUM = LIMIT.bit_length()  # 54 for 10^16


# ---------------------------
# Small primes (sieve)
# ---------------------------


def primes_upto(n: int) -> List[int]:
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, int(n**0.5) + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i in range(n + 1) if sieve[i]]


SMALL_PRIMES = primes_upto(100000)
FIRST_PRIMES = SMALL_PRIMES[:60]  # enough for minimal-number pruning


# ---------------------------
# Deterministic Miller-Rabin for 64-bit
# ---------------------------

# Deterministic bases for n < 2^64
# (well-known set used in many implementations)
_MR_BASES_64 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    # quick small-prime checks
    small = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small:
        if n == p:
            return True
        if n % p == 0:
            return False

    # write n-1 = d * 2^s with d odd
    d = n - 1
    s = 0
    while (d & 1) == 0:
        s += 1
        d >>= 1

    for a in _MR_BASES_64:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


# ---------------------------
# Pollard Rho factorization (64-bit safe in Python ints)
# ---------------------------

_rng_state = 0x9E3779B97F4A7C15  # arbitrary nonzero seed


def _rand64() -> int:
    # xorshift64*
    global _rng_state
    x = _rng_state & ((1 << 64) - 1)
    x ^= (x >> 12) & ((1 << 64) - 1)
    x ^= (x << 25) & ((1 << 64) - 1)
    x ^= (x >> 27) & ((1 << 64) - 1)
    _rng_state = x
    return (x * 2685821657736338717) & ((1 << 64) - 1)


def _randrange(n: int) -> int:
    # n > 0
    return _rand64() % n


def pollard_rho(n: int) -> int:
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3

    while True:
        c = _randrange(n - 1) + 1
        x = _randrange(n)
        y = x

        # f(x) = x^2 + c mod n
        def f(v: int) -> int:
            return (v * v + c) % n

        d = 1
        while d == 1:
            x = f(x)
            y = f(f(y))
            d = math.gcd(abs(x - y), n)
        if d != n:
            return d


def factorize(n: int, out: Dict[int, int]) -> None:
    """Fill out with prime -> exponent for n (n <= 1e16 in this problem)."""
    if n == 1:
        return
    if is_probable_prime(n):
        out[n] = out.get(n, 0) + 1
        return

    # trial division by a modest number of small primes helps Pollard Rho a lot
    for p in SMALL_PRIMES[:2000]:
        if p * p > n:
            break
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            out[p] = out.get(p, 0) + e
            factorize(n, out)
            return

    if n == 1:
        return
    if is_probable_prime(n):
        out[n] = out.get(n, 0) + 1
        return

    d = pollard_rho(n)
    factorize(d, out)
    factorize(n // d, out)


def prime_signature(n: int) -> Tuple[int, ...]:
    """Return the prime signature of n: exponents sorted descending."""
    if n == 1:
        return ()
    fac: Dict[int, int] = {}
    factorize(n, fac)
    return tuple(sorted(fac.values(), reverse=True))


# ---------------------------
# Count g(n) from a prime signature
# ---------------------------

# Precompute binomial coefficients up to needed size:
# comb argument is (a+t-1) where a<=MAX_EXP_SUM and t<=sum(a)=MAX_EXP_SUM, so <=2*MAX_EXP_SUM.
_MAX_N = 2 * MAX_EXP_SUM + 2
_COMB = [[0] * (_MAX_N + 1) for _ in range(_MAX_N + 1)]
for n in range(_MAX_N + 1):
    _COMB[n][0] = 1
    for k in range(1, n + 1):
        _COMB[n][k] = _COMB[n - 1][k - 1] + _COMB[n - 1][k] if k < n else 1

_BINOM = [[0] * (MAX_EXP_SUM + 1) for _ in range(MAX_EXP_SUM + 1)]
for n in range(MAX_EXP_SUM + 1):
    for k in range(n + 1):
        _BINOM[n][k] = _COMB[n][k]


def gozinta_from_signature(sig: Tuple[int, ...], limit: int | None = None) -> int:
    """
    sig is the multiset of exponents (sorted descending) of n.
    g depends only on this signature.

    Inclusion-exclusion count:
    A chain corresponds to splitting the exponent-vector into m nonempty "steps".
    For fixed m, count m-step chains via inclusion-exclusion over empty steps.

    Complexity is O(S^2 * k) where S=sum(sig), k=len(sig), and here S<=54.
    """
    s = sum(sig)
    if s == 0:
        return 1

    # P[t] = product_i C(ai+t-1, t-1)
    # where t is the number of nonempty steps after inclusion-exclusion
    P = [0] * (s + 1)
    for t in range(1, s + 1):
        prod = 1
        tt = t - 1
        for a in sig:
            prod *= _COMB[a + t - 1][tt]
        P[t] = prod

    total = 0
    for m in range(1, s + 1):
        # A_m = sum_{t=1..m} (-1)^(m-t) * C(m,t) * P[t]
        A_m = 0
        for t in range(1, m + 1):
            term = _BINOM[m][t] * P[t]
            if (m - t) & 1:
                A_m -= term
            else:
                A_m += term
        total += A_m
        if limit is not None and total > limit:
            return limit + 1
    return total


def gozinta(n: int, limit: int | None = None) -> int:
    return gozinta_from_signature(prime_signature(n), limit=limit)


# ---------------------------
# Enumerate signatures that could possibly produce a solution
# ---------------------------


def generate_signatures(max_sum: int, limit: int) -> Tuple[int, ...]:
    """
    Enumerate all exponent signatures (nonincreasing sequences of positive ints)
    with sum <= max_sum and whose *minimal* number (assigning smallest primes
    in order) is <= limit.

    This pruning keeps the search tiny (about 17k signatures for 10^16).
    """
    sig: List[int] = []

    def rec(pos: int, prev_e: int, sum_used: int, prod: int):
        if sig:
            yield tuple(sig)
        if sum_used == max_sum or pos >= len(FIRST_PRIMES):
            return

        p = FIRST_PRIMES[pos]
        max_e = min(prev_e, max_sum - sum_used)

        power = p
        for e in range(1, max_e + 1):
            new_prod = prod * power
            if new_prod > limit:
                break
            sig.append(e)
            yield from rec(pos + 1, e, sum_used + e, new_prod)
            sig.pop()
            power *= p

    yield from rec(0, max_sum, 0, 1)


def solve(limit: int = LIMIT) -> int:
    # Tests from the problem statement
    assert gozinta(12) == 8
    assert gozinta(48) == 48
    assert gozinta(120) == 132

    solutions = [1]  # g(1)=1

    for sig in generate_signatures(MAX_EXP_SUM, limit):
        g = gozinta_from_signature(sig, limit=limit)
        if g > limit:
            continue
        if prime_signature(g) == sig:
            solutions.append(g)

    # signatures are unique; g is unique per signature here, but de-dup for safety
    return sum(sorted(set(solutions)))


def main() -> None:
    print(solve())


if __name__ == "__main__":
    main()
