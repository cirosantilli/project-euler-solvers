#!/usr/bin/env python3
"""
Project Euler 608
Compute D(200!, 10^12) mod 1_000_000_007

No external libraries used.
"""

from __future__ import annotations

import math
import bisect
from collections import defaultdict

MOD = 1_000_000_007


def primes_upto(n: int) -> list[int]:
    """Simple sieve of Eratosthenes."""
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    r = int(n**0.5)
    for i in range(2, r + 1):
        if sieve[i]:
            step = i
            start = i * i
            sieve[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i in range(2, n + 1) if sieve[i]]


def v_factorial(n: int, p: int) -> int:
    """Exponent of prime p in n!"""
    e = 0
    while n:
        n //= p
        e += n
    return e


def modinv(a: int) -> int:
    return pow(a, MOD - 2, MOD)


def tau_prefix_summatory(B: int) -> list[int]:
    """
    Build prefix sums of tau(k) for k=1..B in O(B) using a linear sieve.
    Returns pref where pref[x] = sum_{k<=x} tau(k).
    """
    if B <= 0:
        return [0]
    lp = [0] * (B + 1)
    exp = [0] * (B + 1)  # exponent of lp[i] in i
    tau = [0] * (B + 1)
    primes: list[int] = []
    tau[1] = 1

    for i in range(2, B + 1):
        if lp[i] == 0:
            lp[i] = i
            exp[i] = 1
            tau[i] = 2
            primes.append(i)
        for p in primes:
            ip = i * p
            if ip > B:
                break
            lp[ip] = p
            if p == lp[i]:
                exp[ip] = exp[i] + 1
                # tau(i) = tau(m) * (exp[i] + 1); tau(ip) = tau(m) * (exp[i] + 2)
                tau[ip] = (tau[i] // (exp[i] + 1)) * (exp[i] + 2)
                break
            else:
                exp[ip] = 1
                tau[ip] = tau[i] * 2

    pref = [0] * (B + 1)
    s = 0
    for i in range(1, B + 1):
        s += tau[i]
        pref[i] = s
    return pref


def T_summatory(n: int, pref_small: list[int], B: int, cache: dict[int, int]) -> int:
    """
    T(n) = sum_{k<=n} tau(k) = sum_{i=1..n} floor(n/i).
    For n<=B use precomputed prefix; else compute in O(sqrt(n)) and memoize.
    """
    if n <= B:
        return pref_small[n]
    v = cache.get(n)
    if v is not None:
        return v
    r = int(math.isqrt(n))
    nn = n
    s = 0
    # 2*sum_{i<=sqrt(n)} floor(n/i) - floor(sqrt(n))^2
    for i in range(1, r + 1):
        s += nn // i
    res = 2 * s - r * r
    cache[n] = res
    return res


def gen_products_weights(
    primes: list[int], weights: list[int], limit: int
) -> tuple[list[int], list[int]]:
    """
    Enumerate all squarefree products from the given primes with product <= limit,
    along with their multiplicative weights.
    Returns parallel lists (products, weights_mod).
    """
    prods: list[int] = []
    wgts: list[int] = []
    stack = [(0, 1, 1)]
    P = primes
    W = weights
    L = len(P)

    while stack:
        i, prod, w = stack.pop()
        prods.append(prod)
        wgts.append(w)
        for j in range(i, L):
            np = prod * P[j]
            if np <= limit:
                stack.append((j + 1, np, (w * W[j]) % MOD))
    return prods, wgts


def prefix_g_map(
    primes: list[int], weights: list[int], limit: int, x_values: list[int]
) -> dict[int, int]:
    """
    Compute G(x) = sum_{q<=x} g(q) for each x in x_values, where
    g is squarefree multiplicative on the given primes with g(p)=weights[p].

    Uses meet-in-the-middle:
      - enumerate all products in first half and build prefix sums
      - enumerate all products in second half
      - for each x, sum_{b in half2} w_b * Prefix1(x//b)
    """
    L = len(primes)
    mid = L // 2
    p1, w1 = primes[:mid], weights[:mid]
    p2, w2 = primes[mid:], weights[mid:]

    prods1, wgts1 = gen_products_weights(p1, w1, limit)
    prods2, wgts2 = gen_products_weights(p2, w2, limit)

    pairs1 = sorted(zip(prods1, wgts1), key=lambda t: t[0])
    prods1 = [p for p, _ in pairs1]
    pref1 = [0] * len(pairs1)
    s = 0
    for i, (_, w) in enumerate(pairs1):
        s += w
        s %= MOD
        pref1[i] = s

    pairs2 = sorted(zip(prods2, wgts2), key=lambda t: t[0])
    prods2 = [p for p, _ in pairs2]
    wgts2 = [w for _, w in pairs2]

    bisect_right = bisect.bisect_right
    sentinel = object()
    cache: dict[int, int] = {}  # u -> Prefix1(u)
    out: dict[int, int] = {}

    for x in x_values:
        total = 0
        for pb, wb in zip(prods2, wgts2):
            u = x // pb
            v = cache.get(u, sentinel)
            if v is sentinel:
                pos = bisect_right(prods1, u)
                v = pref1[pos - 1] if pos else 0
                cache[u] = v
            total = (total + wb * v) % MOD
        out[x] = total
    return out


def D_factorial(M: int, n: int) -> int:
    """
    Compute D(M!, n) mod MOD, where
      D(m,n)= sum_{d|m} sum_{k=1..n} tau(kd).
    Specialized to m=M! using multiplicativity and a Dirichlet-series factorization.
    """
    primes = primes_upto(M)

    A = 1
    C = 1
    inv2 = modinv(2)

    # g(p) = -a/(a+2) mod MOD, where a=v_p(M!)
    weights: list[int] = []
    for p in primes:
        a = v_factorial(M, p)
        A = (A * (a + 1)) % MOD
        C = (C * (a + 2)) % MOD
        weights.append((-a * modinv(a + 2)) % MOD)

    C = (C * pow(inv2, len(primes), MOD)) % MOD
    K = (A * C) % MOD

    B = int(math.isqrt(n))
    pref_small = tau_prefix_summatory(B)
    cache_T: dict[int, int] = {}

    # Split on q (squarefree from primes<=M): enumerate q<=y, handle q>y via prefix sums G(x)
    y = n if n <= 1_000_000_000 else 1_000_000_000

    # Accumulate weights grouped by quotient t = n//q for q<=y
    sums = defaultdict(int)
    stack = [(0, 1, 1)]
    P = primes
    W = weights
    L = len(P)

    while stack:
        i, prod, wg = stack.pop()
        t = n // prod
        sums[t] = (sums[t] + wg) % MOD
        for j in range(i, L):
            np = prod * P[j]
            if np <= y:
                stack.append((j + 1, np, (wg * W[j]) % MOD))

    H = 0
    for t, ws in sums.items():
        Tt = T_summatory(t, pref_small, B, cache_T) % MOD
        H = (H + ws * Tt) % MOD

    if y < n:
        tmax = n // y  # for n=1e12,y=1e9 this is 1000
        xset = {y}
        for k in range(1, tmax + 2):
            xset.add(n // k)
        x_values = sorted(xset)
        G = prefix_g_map(primes, weights, n, x_values)

        for t in range(1, tmax + 1):
            R = n // t
            Lb = max(y, n // (t + 1))
            interval = (G[R] - G[Lb]) % MOD
            Tt = T_summatory(t, pref_small, B, cache_T) % MOD
            H = (H + interval * Tt) % MOD

    return (K * H) % MOD


def main() -> None:
    # Asserts from the problem statement
    assert D_factorial(3, 10**2) == 3398
    assert D_factorial(4, 10**6) == 268882292

    print(D_factorial(200, 10**12))


if __name__ == "__main__":
    main()
