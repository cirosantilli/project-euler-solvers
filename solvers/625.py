#!/usr/bin/env python3
"""
Project Euler 625 - Gcd sum

We need:
    G(N) = sum_{j=1..N} sum_{i=1..j} gcd(i, j)
and the problem asks for G(10^11) mod 998244353.

No external libraries are used.
"""

from __future__ import annotations

from array import array
from math import isqrt


MOD = 998244353
INV2 = (MOD + 1) // 2

TARGET_N = 10 ** 11

# Precompute phi and its prefix sum up to this bound.
# 10,000,000 is a good tradeoff for N=10^11: it keeps the memoized recursion small.
PRECOMP_LIMIT = 10_000_000


def tri(n: int) -> int:
    """Triangular number n*(n+1)/2 modulo MOD."""
    n %= MOD
    return (n * (n + 1) % MOD) * INV2 % MOD


def precompute_phi_prefix(limit: int, need_phi_upto: int) -> tuple[array, array]:
    """
    Linear sieve for Euler's totient function phi(1..limit).
    Returns:
      - phi_small: phi(0..need_phi_upto) (needed later in G(N))
      - phi_prefix: in-place prefix sums of phi modulo MOD, length limit+1
    """
    # phi will be overwritten into prefix sums after we copy out phi_small.
    phi = array("I", [0]) * (limit + 1)
    phi[1] = 1

    is_comp = bytearray(limit + 1)
    primes: list[int] = []

    for i in range(2, limit + 1):
        if not is_comp[i]:
            primes.append(i)
            phi[i] = i - 1
        for p in primes:
            ip = i * p
            if ip > limit:
                break
            is_comp[ip] = 1
            if i % p == 0:
                phi[ip] = phi[i] * p
                break
            else:
                phi[ip] = phi[i] * (p - 1)

    phi_small = array("I", phi[: need_phi_upto + 1])

    s = 0
    for i in range(1, limit + 1):
        s += phi[i]
        s %= MOD
        phi[i] = s

    return phi_small, phi


class PhiSummatory:
    """
    PhiSummatory(n) = sum_{k=1..n} phi(k) (mod MOD).

    Uses:
      - precomputed prefix sums for n <= PRECOMP_LIMIT
      - memoized recursion for larger n:
            Phi(n) = T(n) - sum_{i=2..n} Phi(floor(n/i))
        split into:
            i <= sqrt(n)   (large quotients, recurse)
            i  > sqrt(n)   (small quotients, use prefix sums)
    """

    __slots__ = ("prefix", "limit", "cache")

    def __init__(self, prefix: array, limit: int):
        self.prefix = prefix
        self.limit = limit
        self.cache: dict[int, int] = {}

    def __call__(self, n: int) -> int:
        if n <= self.limit:
            return int(self.prefix[n])
        hit = self.cache.get(n)
        if hit is not None:
            return hit

        s = isqrt(n)
        ans = tri(n)

        pref = self.prefix

        # Contribution of i > sqrt(n):
        # For each m = floor(n/i) (which is <= n//sqrt(n)), count how many i give that m.
        m_max = n // s  # slightly loose upper bound; extra terms have zero coefficient.
        for m in range(1, m_max):
            coef = n // m - n // (m + 1)
            if coef:
                ans -= coef * int(pref[m])

        # Contribution of i <= sqrt(n): sum Phi(n//i), grouped by equal quotients.
        i = 2
        while i <= s:
            q = n // i
            j = min(s, n // q)
            ans -= (j - i + 1) * self(q)
            i = j + 1

        ans %= MOD
        self.cache[n] = ans
        return ans


def gcd_sum_G(n: int, phi_small: array, Phi: PhiSummatory) -> int:
    """
    Computes G(n) modulo MOD using a hyperbola split:
      G(n) = sum_{k<=s} k*Phi(n//k) + sum_{k<=s} phi(k)*T(n//k) - T(s)*Phi(s),
      where s = floor(sqrt(n)), Phi(x) = sum_{i<=x} phi(i), T(x)=x(x+1)/2.
    """
    s = isqrt(n)
    ans = 0

    # sum_{k<=s} k*Phi(n//k), grouped by equal quotients
    k = 1
    while k <= s:
        q = n // k
        j = min(s, n // q)
        cnt = j - k + 1
        sum_k = (k + j) * cnt // 2
        ans += (sum_k % MOD) * Phi(q)
        k = j + 1

    # sum_{k<=s} phi(k)*T(n//k)
    for k in range(1, s + 1):
        ans += int(phi_small[k]) * tri(n // k)

    # subtract T(s)*Phi(s)
    ans -= tri(s) * Phi(s)

    return ans % MOD


def solve() -> None:
    n = TARGET_N
    s = isqrt(n)

    phi_small, phi_prefix = precompute_phi_prefix(PRECOMP_LIMIT, s)
    Phi = PhiSummatory(phi_prefix, PRECOMP_LIMIT)

    # Test value given in the problem statement
    assert gcd_sum_G(10, phi_small, Phi) == 122

    print(gcd_sum_G(n, phi_small, Phi))


if __name__ == "__main__":
    solve()
