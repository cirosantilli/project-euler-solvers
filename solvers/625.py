#!/usr/bin/env python3
"""Project Euler 625 — Gcd Sum

Compute:
    G(N) = \sum_{j=1..N} \sum_{i=1..j} gcd(i, j)

Required:
    G(10^11) mod 998244353

Fast pure-Python approach:
  - Reduce to a single sum with Euler's totient.
  - Use quotient grouping so the outer sum has ~2*sqrt(N) terms.
  - Compute the summatory totient Phi(n)=\sum_{k<=n} phi(k) using a
    Dujiao-style recursion with quotient grouping + memoization.

No external libraries are used.
"""

from __future__ import annotations

import sys
from array import array

MOD = 998244353


def tri_mod(n: int) -> int:
    """T(n) = n(n+1)/2 (mod MOD), computed without modular inverse."""
    a = n
    b = n + 1
    if (a & 1) == 0:
        a //= 2
    else:
        b //= 2
    return (a % MOD) * (b % MOD) % MOD


def build_phi_prefix(limit: int) -> array:
    """Return pref array where pref[n] = sum_{k<=n} phi(k) (mod MOD) for n<=limit.

    Uses a linear sieve to compute phi up to `limit`, then converts in-place to
    prefix sums modulo MOD.

    The returned value is an array('I') of length limit+1.
    """
    if limit <= 0:
        return array("I", [0])

    # phi will be overwritten with prefix sums at the end.
    phi = array("I", [0]) * (limit + 1)
    is_comp = bytearray(limit + 1)
    primes = array("I")

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

    # In-place prefix sums mod MOD.
    # We keep limit < MOD in this program (default limit=5e6), so phi[i] < MOD.
    s = 0
    for i in range(1, limit + 1):
        s += phi[i]
        if s >= MOD:
            s -= MOD
        phi[i] = s

    return phi


def gcd_sum(N: int) -> int:
    """Compute G(N) mod MOD."""
    if N <= 0:
        return 0

    # Sieve limit trade-off: larger is faster for Phi(n) but costs more memory/time to sieve.
    # 5e6 is a good sweet spot for N=1e11 in pure Python.
    LIMIT = 5_000_000
    if N < LIMIT:
        LIMIT = N

    pref = build_phi_prefix(LIMIT)

    memo: dict[int, int] = {}
    memo_get = memo.get
    MOD_ = MOD
    tri = tri_mod
    LIM = LIMIT
    pref_ = pref

    def Phi(n: int) -> int:
        """Phi(n) = sum_{k<=n} phi(k) (mod MOD) with Dujiao recursion."""
        if n <= 0:
            return 0
        if n <= LIM:
            return pref_[n]
        cached = memo_get(n)
        if cached is not None:
            return cached

        # Dujiao recursion (grouped by constant floor(n/l)):
        # Phi(n) = T(n) - sum_{l=2..n} (r-l+1) * Phi(n//l)
        res = tri(n)
        l = 2
        while l <= n:
            q = n // l
            r = n // q
            res = (res - ((r - l + 1) % MOD_) * Phi(q)) % MOD_
            l = r + 1

        memo[n] = res
        return res

    # G(N) = sum_{k=1..N} phi(k) * T(N//k)
    # Group k by constant q = N//k:
    ans = 0
    l = 1
    while l <= N:
        q = N // l
        r = N // q
        sum_phi = (Phi(r) - Phi(l - 1)) % MOD_
        ans = (ans + sum_phi * tri(q)) % MOD_
        l = r + 1

    return ans


def main() -> None:
    N = 10**11

    data = sys.stdin.read().strip()
    if data:
        N = int(data)

    # Test value from the problem statement:
    assert gcd_sum(10) == 122 % MOD

    print(gcd_sum(N))


if __name__ == "__main__":
    main()
