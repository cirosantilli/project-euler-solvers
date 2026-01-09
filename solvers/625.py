#!/usr/bin/env python3
"""
Project Euler 625 — Gcd Sum

G(N) = sum_{j=1..N} sum_{i=1..j} gcd(i, j)

We need G(10^11) mod 998244353.

No external libraries are used (only Python standard library).
"""

from __future__ import annotations

import sys
import math
from array import array

MOD = 998244353
INV2 = (MOD + 1) // 2


def tri_mod(n: int) -> int:
    """n*(n+1)/2 (mod MOD)."""
    n %= MOD
    return (n * (n + 1) % MOD) * INV2 % MOD


def sieve_phi(limit: int) -> array:
    """
    Linear sieve for Euler's totient up to `limit`.
    Returns an array('I') phi where phi[i] fits in 32 bits for i<=limit.
    """
    phi = array("I", [0]) * (limit + 1)
    is_comp = bytearray(limit + 1)
    primes = array("I")

    if limit >= 1:
        phi[1] = 1

    for i in range(2, limit + 1):
        if not is_comp[i]:
            primes.append(i)
            phi[i] = i - 1
        for p in primes:
            v = i * p
            if v > limit:
                break
            is_comp[v] = 1
            if i % p == 0:
                phi[v] = phi[i] * p
                break
            else:
                phi[v] = phi[i] * (p - 1)

    return phi


def gcd_sum_prefix(N: int, sieve_limit: int = 10_000_000) -> int:
    """
    Compute G(N) modulo MOD.

    `sieve_limit` is a speed/space tuning parameter: larger limits reduce recursion.
    10,000,000 is a good default for N=10^11.
    """
    # Ensure we have phi up to sqrt(N) because the final hyperbola split uses those values directly.
    sieve_limit = max(sieve_limit, math.isqrt(N) + 2)

    phi = sieve_phi(sieve_limit)

    # Prefix sums of phi modulo MOD: Phi(n) = sum_{k<=n} phi(k) (mod MOD) for n<=sieve_limit.
    cphi = array("I", [0]) * (sieve_limit + 1)
    s = 0
    for i in range(1, sieve_limit + 1):
        s += phi[i]
        # keep `s` small-ish without doing an expensive modulo each iteration
        if s >= MOD:
            s %= MOD
        cphi[i] = s
    s %= MOD

    memo: dict[int, int] = {}
    sys.setrecursionlimit(1_000_000)

    # Local bindings for speed
    isqrt = math.isqrt
    MOD_ = MOD
    tri = tri_mod
    cphi_ = cphi
    phi_ = phi
    memo_get = memo.get
    memo_set = memo.__setitem__
    lim = sieve_limit

    def Phi(n: int) -> int:
        """
        Summatory totient: sum_{k<=n} phi(k) (mod MOD).

        Uses a hyperbola-method recursion that only needs exact values up to `lim`,
        and memoizes the remaining queries.
        """
        if n <= lim:
            return cphi_[n]
        cached = memo_get(n)
        if cached is not None:
            return cached

        sq = isqrt(n)
        k = n // sq  # roughly sqrt(n)

        # Start from T(n) = n(n+1)/2 = sum_{d<=n} d
        ans = tri(n)

        # First correction term (uses small prefix sums only)
        sub = 0
        for m in range(1, k):
            sub += (n // m - n // (m + 1)) * cphi_[m]
        ans -= sub % MOD_

        # Second correction term: split recursion so we only recurse when n//m > lim
        thresh = n // lim
        if thresh > sq:
            thresh = sq

        sub2 = 0
        for m in range(2, thresh + 1):
            sub2 += Phi(n // m)
        if thresh < sq:
            for m in range(thresh + 1, sq + 1):
                sub2 += cphi_[n // m]

        ans -= sub2 % MOD_
        ans %= MOD_

        memo_set(n, ans)
        return ans

    def G(n: int) -> int:
        """
        Compute G(n) = sum_{j<=n} sum_{i<=j} gcd(i,j) (mod MOD),
        using a sqrt(n) hyperbola split.
        """
        sq = isqrt(n)

        # Hyperbola method:
        # G(n) = sum_{k<=n} phi(k) * T(floor(n/k)).
        # Split at k<=sq and use Phi(·) for the rest.
        ans = (-tri(sq) * Phi(sq)) % MOD_

        tmp = 0
        for i in range(1, sq + 1):
            tmp += Phi(n // i) * i
        ans = (ans + tmp) % MOD_

        tmp = 0
        for i in range(1, sq + 1):
            tmp += phi_[i] * tri(n // i)
        ans = (ans + tmp) % MOD_

        return ans

    return G(N)


def main() -> None:
    # Default: the actual Project Euler input
    N = 10**11

    data = sys.stdin.read().strip()
    if data:
        N = int(data)

    # Problem statement test value:
    assert gcd_sum_prefix(10, sieve_limit=100_000) == 122 % MOD

    print(gcd_sum_prefix(N))


if __name__ == "__main__":
    main()
