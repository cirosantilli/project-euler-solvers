#!/usr/bin/env python3
"""Project Euler 432: Totient Sum

Let S(n, m) = \sum_{i=1..m} phi(n*i).
Given S(510510, 10^6) = 45480596821125120.
Find S(510510, 10^11) and give the last 9 digits.

This program prints those last 9 digits (zero-padded to 9 digits).

No third-party libraries are used.
"""

from __future__ import annotations

from array import array
from math import isqrt

MOD = 1_000_000_000
# A moderate sieve limit is enough because the summatory totient routine
# only needs Phi(x) for x up to about sqrt(1e11) during its recursion.
# Increasing this limit reduces recursion work at the cost of memory/time.
SIEVE_LIMIT = 5_000_000


def build_totients(limit: int) -> tuple[array, array, list[int]]:
    """Euler (linear) sieve computing phi(1..limit) and prefix sums mod MOD."""
    phi = array("I", [0]) * (limit + 1)
    phi[1] = 1
    primes: list[int] = []

    for i in range(2, limit + 1):
        if phi[i] == 0:
            phi[i] = i - 1
            primes.append(i)
        for p in primes:
            ip = i * p
            if ip > limit:
                break
            if i % p == 0:
                phi[ip] = phi[i] * p
                break
            phi[ip] = phi[i] * (p - 1)

    prefix_mod = array("I", [0]) * (limit + 1)
    acc = 0
    for i in range(1, limit + 1):
        acc += phi[i]
        acc %= MOD
        prefix_mod[i] = acc

    return phi, prefix_mod, primes


def distinct_prime_factors(n: int, primes: list[int]) -> list[int]:
    """Distinct prime factors of n (n is small here)."""
    x = n
    res: list[int] = []
    for p in primes:
        if p * p > x:
            break
        if x % p == 0:
            res.append(p)
            while x % p == 0:
                x //= p
    if x > 1:
        res.append(x)
    return res


def subset_products_with_sign(prime_factors: list[int]) -> list[tuple[int, int]]:
    """All non-empty subset products, with sign = +1 (odd size) or -1 (even size)."""
    pf = prime_factors
    k = len(pf)
    out: list[tuple[int, int]] = []
    for mask in range(1, 1 << k):
        prod = 1
        bits = 0
        mm = mask
        idx = 0
        while mm:
            if mm & 1:
                prod *= pf[idx]
                bits += 1
            idx += 1
            mm >>= 1
        sign = 1 if (bits & 1) else -1
        out.append((prod, sign))
    out.sort(key=lambda t: t[0])
    return out


def solve() -> str:
    n = 510510
    m = 10**11

    phi, Phi_small_mod, primes = build_totients(SIEVE_LIMIT)

    # Prime factors of n (n = 2*3*5*7*11*13*17).
    pf = distinct_prime_factors(n, primes)
    subset_list = subset_products_with_sign(pf)

    phi_n = int(phi[n])
    phi_n_mod = phi_n % MOD

    # ----------------------------
    # Summatory totient Phi(x) mod MOD
    # ----------------------------
    Phi_cache: dict[int, int] = {}

    def Phi_mod(x: int) -> int:
        """Phi_mod(x) = sum_{k<=x} phi(k) (mod MOD), for huge x."""
        if x <= SIEVE_LIMIT:
            return Phi_small_mod[x]
        got = Phi_cache.get(x)
        if got is not None:
            return got

        # T(x) = 1 + 2 + ... + x
        ans = (x * (x + 1) // 2) % MOD

        r = isqrt(x)
        upper = x // r  # = floor(x / floor(sqrt(x)))

        # Handle terms where floor(x / k) takes large values (> r)
        # using precomputed Phi_small_mod.
        # This matches the common hyperbola decomposition:
        #   Phi(x) = T(x) - sum_{t=1..upper-1} Phi(t) * (floor(x/t) - floor(x/(t+1)))
        #           - sum_{k=2..r} Phi(floor(x/k))
        for t in range(1, upper):
            ans -= Phi_small_mod[t] * (x // t - x // (t + 1))
            ans %= MOD

        for k in range(2, r + 1):
            ans -= Phi_mod(x // k)
            ans %= MOD

        ans %= MOD
        Phi_cache[x] = ans
        return ans

    # ----------------------------
    # S(n, m) mod MOD via inclusion-exclusion over primes dividing n
    # ----------------------------
    S_cache: dict[int, int] = {}

    def S_mod(mm: int) -> int:
        if mm <= 0:
            return 0
        if mm == 1:
            return phi_n_mod
        got = S_cache.get(mm)
        if got is not None:
            return got

        ans = (phi_n_mod * Phi_mod(mm)) % MOD

        # Inclusion-exclusion over non-empty subsets of prime factors.
        for prod, sign in subset_list:
            if prod > mm:
                break
            q = mm // prod
            if q == 0:
                break
            if sign == 1:
                ans += S_mod(q)
            else:
                ans -= S_mod(q)
            ans %= MOD

        ans %= MOD
        S_cache[mm] = ans
        return ans

    # ----------------------------
    # Assert the statement's check value (exact integer, no modulus)
    # ----------------------------
    EXACT_M = 1_000_000
    Phi_exact = array("Q", [0]) * (EXACT_M + 1)
    acc = 0
    for i in range(1, EXACT_M + 1):
        acc += phi[i]
        Phi_exact[i] = acc

    S_cache_exact: dict[int, int] = {}

    def S_exact(mm: int) -> int:
        if mm <= 0:
            return 0
        if mm == 1:
            return phi_n
        got = S_cache_exact.get(mm)
        if got is not None:
            return got

        ans = phi_n * int(Phi_exact[mm])
        for prod, sign in subset_list:
            if prod > mm:
                break
            q = mm // prod
            if q == 0:
                break
            ans += sign * S_exact(q)
        S_cache_exact[mm] = ans
        return ans

    assert S_exact(EXACT_M) == 45480596821125120

    # Compute the requested result.
    last9 = S_mod(m) % MOD
    return f"{last9:09d}"


if __name__ == "__main__":
    print(solve())
