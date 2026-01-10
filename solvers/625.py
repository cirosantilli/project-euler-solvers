#!/usr/bin/env python3
"""
Project Euler 625 — Gcd Sum

Compute:
  G(N) = sum_{j=1..N} sum_{i=1..j} gcd(i, j)

Need:
  G(10^11) mod 998244353

Optimized sublinear solution (pure Python, no third-party libs):

1) Identity:
     G(N) = sum_{k=1..N} phi(k) * T(floor(N/k)),
   where T(x)=x(x+1)/2.

2) Outer sum is evaluated in O(sqrt(N)) blocks by grouping constant quotients q=floor(N/k).

3) The only hard part is Phi(n)=sum_{k<=n} phi(k). We use a Dujiao-style recursion
   with quotient grouping + memoization.

4) Practical Python performance tricks:
   - Use a sieve cutoff L ≈ N^(2/3).
   - Compute Phi(N) ONCE up-front to populate the memo, avoiding repeated expensive
     independent Phi calls during the outer sum.
   - Keep all modular values reduced with branch-only arithmetic inside hot loops
     (avoid '%' in the inner loop except for cnt%MOD).

No external libraries.
"""

from __future__ import annotations

import sys
from array import array

MOD = 998244353


def tri_mod(n: int) -> int:
    """T(n)=n(n+1)/2 mod MOD, without modular inverse."""
    a = n
    b = n + 1
    if (a & 1) == 0:
        a //= 2
    else:
        b //= 2
    return (a % MOD) * (b % MOD) % MOD


def icbrt_floor(n: int) -> int:
    """Integer floor cube-root."""
    if n <= 0:
        return 0
    x = int(round(n ** (1.0 / 3.0)))
    while (x + 1) * (x + 1) * (x + 1) <= n:
        x += 1
    while x * x * x > n:
        x -= 1
    return x


def build_phi_prefix(limit: int) -> array:
    """Linear sieve phi up to limit; return prefix sums modulo MOD in array('I')."""
    if limit <= 0:
        return array("I", [0])

    phi = array("I", [0]) * (limit + 1)
    is_comp = bytearray(limit + 1)
    primes: list[int] = []

    phi[1] = 1

    phi_local = phi
    is_comp_local = is_comp
    primes_append = primes.append

    for i in range(2, limit + 1):
        if not is_comp_local[i]:
            primes_append(i)
            phi_local[i] = i - 1
        for p in primes:
            v = i * p
            if v > limit:
                break
            is_comp_local[v] = 1
            if i % p == 0:
                phi_local[v] = phi_local[i] * p
                break
            else:
                phi_local[v] = phi_local[i] * (p - 1)

    # prefix sums mod MOD; since limit << MOD, one subtraction is enough each step
    s = 0
    for i in range(1, limit + 1):
        s += phi_local[i]
        if s >= MOD:
            s -= MOD
        phi_local[i] = s

    return phi_local


def gcd_sum(N: int) -> int:
    if N <= 0:
        return 0

    # Sieve cutoff: classic Dujiao sweet spot L ~ N^(2/3)
    c = icbrt_floor(N)
    L = c * c
    if L < 1_000_000:
        L = min(N, 1_000_000)
    else:
        L = min(L, N)

    pref = build_phi_prefix(L)

    memo: dict[int, int] = {}
    memo_get = memo.get
    memo_set = memo.__setitem__
    pref_ = pref
    LIM = L
    tri = tri_mod
    MOD_ = MOD

    sys.setrecursionlimit(1_000_000)

    def Phi(n: int) -> int:
        """Summatory totient Phi(n)=sum_{k<=n} phi(k) mod MOD."""
        if n <= 0:
            return 0
        if n <= LIM:
            return pref_[n]
        v = memo_get(n)
        if v is not None:
            return v

        # Phi(n) = T(n) - sum_{l=2..n} (r-l+1)*Phi(n//l), grouped by quotient
        res = tri(n)  # 0 <= res < MOD
        l = 2
        while l <= n:
            q = n // l
            r = n // q
            cnt = r - l + 1

            sub = pref_[q] if q <= LIM else Phi(q)
            t = (cnt % MOD_) * sub % MOD_
            res -= t
            if res < 0:
                res += MOD_
            l = r + 1

        memo_set(n, res)
        return res

    # Warm memo once (big speed win): this fills memo with all large Phi values the outer sum needs.
    Phi(N)

    def Phi_fast(n: int) -> int:
        if n <= 0:
            return 0
        if n <= LIM:
            return pref_[n]
        return memo[n]

    # Outer sum in O(sqrt N) blocks:
    ans = 0
    l = 1
    while l <= N:
        q = N // l
        r = N // q
        sum_phi = (Phi_fast(r) - Phi_fast(l - 1)) % MOD_
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

