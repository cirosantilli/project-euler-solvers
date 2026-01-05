from __future__ import annotations

import math
from array import array
from functools import lru_cache
from typing import List


def sieve_primes(n: int) -> List[int]:
    sieve = bytearray(b"\x01") * (n + 1)
    primes: List[int] = []
    for i in range(2, n + 1):
        if sieve[i]:
            primes.append(i)
            if i * i <= n:
                step = i
                start = i * i
                sieve[start : n + 1 : step] = b"\x00" * ((n - start) // step + 1)
    return primes


def build_pi_table(limit: int, sieve: bytearray) -> array:
    pi = array("I", [0]) * (limit + 1)
    count = 0
    for i in range(2, limit + 1):
        if sieve[i]:
            count += 1
        pi[i] = count
    return pi


def build_prefix_h(limit: int, primes: List[int]) -> array:
    omega = bytearray(limit + 1)
    for p in primes:
        if p > limit:
            break
        for j in range(p, limit + 1, p):
            omega[j] += 1
    pref = array("Q", [0]) * (limit + 1)
    for i in range(1, limit + 1):
        pref[i] = pref[i - 1] + (1 << omega[i])
    return pref


def compute_g(n: int) -> int:
    limit = int(math.isqrt(n))
    sieve = bytearray(b"\x01") * (limit + 1)
    primes: List[int] = []
    for i in range(2, limit + 1):
        if sieve[i]:
            primes.append(i)
            if i * i <= limit:
                step = i
                start = i * i
                sieve[start : limit + 1 : step] = b"\x00" * (
                    (limit - start) // step + 1
                )

    pi_small = build_pi_table(limit, sieve)

    # Precompute prefix sum of h(n)=2^omega(n) up to sqrt(n).
    pref_h = build_prefix_h(limit, primes)

    # Precompute phi table for small x and s to speed Lehmer pi.
    phi_n = 200_000
    phi_m = 100
    phi = [[0] * (phi_m + 1) for _ in range(phi_n + 1)]
    for x in range(phi_n + 1):
        phi[x][0] = x
    for s in range(1, phi_m + 1):
        p = primes[s - 1]
        for x in range(phi_n + 1):
            phi[x][s] = phi[x][s - 1] - phi[x // p][s - 1]

    @lru_cache(None)
    def phi_big(x: int, s: int) -> int:
        if s == 0:
            return x
        if s <= phi_m and x <= phi_n:
            return phi[x][s]
        return phi_big(x, s - 1) - phi_big(x // primes[s - 1], s - 1)

    @lru_cache(None)
    def pi_lehmer(x: int) -> int:
        if x <= limit:
            return pi_small[x]
        x14 = int(x**0.25)
        while (x14 + 1) ** 4 <= x:
            x14 += 1
        while x14**4 > x:
            x14 -= 1
        x13 = int(round(x ** (1.0 / 3.0)))
        while (x13 + 1) ** 3 <= x:
            x13 += 1
        while x13**3 > x:
            x13 -= 1
        a = pi_lehmer(x14)
        b = pi_lehmer(int(math.isqrt(x)))
        c = pi_lehmer(x13)
        res = phi_big(x, a) + (b + a - 2) * (b - a + 1) // 2
        for i in range(a + 1, b + 1):
            w = x // primes[i - 1]
            res -= pi_lehmer(w)
            if i <= c:
                lim = pi_lehmer(int(math.isqrt(w)))
                for j in range(i, lim + 1):
                    res -= pi_lehmer(w // primes[j - 1]) - (j - 1)
        return res

    @lru_cache(None)
    def s_sum(x: int, idx: int) -> int:
        if idx >= len(primes) or primes[idx] > x:
            return 0
        res = 0
        sq = int(math.isqrt(x))
        for i in range(idx, len(primes)):
            p = primes[i]
            if p > sq:
                break
            pe = p
            while pe <= x:
                res += 2 * (1 + s_sum(x // pe, i + 1))
                if pe > x // p:
                    break
                pe *= p
        start = primes[idx]
        lo = max(start, sq + 1)
        if lo <= x:
            res += 2 * (pi_lehmer(x) - pi_lehmer(lo - 1))
        return res

    @lru_cache(None)
    def h_sum(x: int) -> int:
        if x <= limit:
            return pref_h[x]
        return 1 + s_sum(x, 0)

    total = 0
    l = 1
    while l <= n:
        q = n // l
        r = n // q
        total += (h_sum(r) - h_sum(l - 1)) * q
        l = r + 1
    return (n + total) // 2


def main() -> None:
    assert compute_g(10**6) == 37429395
    result = compute_g(10**12)
    print(result)


if __name__ == "__main__":
    main()
