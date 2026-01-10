#!/usr/bin/env python3
"""
Project Euler 639 — Summing a Multiplicative Function
----------------------------------------------------

We are given multiplicative functions f_k with:
  f_k(p^e) = p^k for prime p and e > 0

Thus:
  f_k(n) = (rad(n))^k   where rad(n) is the product of distinct primes dividing n

Define:
  S_k(n) = sum_{i=1..n} f_k(i)

We must compute:
  sum_{k=1..50} S_k(10^12) mod 1_000_000_007

Technique used:
  Dirichlet generating function factorisation gives:
    f_k = id^k * h_k
  where h_k is multiplicative, supported only on powerful numbers (all prime exponents >= 2),
  and for prime powers:
    h_k(p^e) = p^k - p^{2k}  for e>=2,  and 0 for e=1

So:
  S_k(n) = sum_{d powerful<=n} h_k(d) * (sum_{m<=n/d} m^k)

We enumerate powerful numbers by DFS over primes and exponents >=2.
We precompute power sums sum_{m<=t} m^k for t <= 10^6 for all k<=50,
and use a Stirling/falling-factorial formula for the few cases where t > 10^6.

No external libraries are used.
"""

import sys
import math
from array import array
from bisect import bisect_right

MOD = 1_000_000_007
KMAX = 50
N_TARGET = 10**12
MAX_PRECOMP = int(math.isqrt(N_TARGET))  # 1_000_000
STRIDE = MAX_PRECOMP + 1


# -------------------------- prime sieve --------------------------


def sieve_primes(limit: int):
    """Return list of all primes <= limit using an odd-only sieve."""
    if limit < 2:
        return []
    size = (limit // 2) + 1
    is_prime = bytearray(b"\x01") * size
    is_prime[0] = 0  # 1 is not prime
    r = int(math.isqrt(limit))
    for x in range(3, r + 1, 2):
        if is_prime[x // 2]:
            step = x
            start = (x * x) // 2
            is_prime[start::step] = b"\x00" * (((size - start - 1) // step) + 1)
    primes = [2]
    primes.extend(2 * i + 1 for i in range(1, size) if is_prime[i])
    return primes


# -------------------------- Stirling numbers + coeffs --------------------------


def build_stirling_and_coeff():
    """
    Build Stirling numbers of second kind S2[n][k] for n,k<=KMAX,
    and coeff[n][j] = S2[n][j] / (j+1) mod MOD (using modular inverse).
    """
    S2 = [[0] * (KMAX + 1) for _ in range(KMAX + 1)]
    S2[0][0] = 1
    for n in range(1, KMAX + 1):
        for k in range(1, n + 1):
            S2[n][k] = (S2[n - 1][k - 1] + k * S2[n - 1][k]) % MOD

    inv = [0] * (KMAX + 2)
    inv[1] = 1
    for i in range(2, KMAX + 2):
        inv[i] = (MOD - (MOD // i)) * inv[MOD % i] % MOD

    coeff = [[0] * (KMAX + 1) for _ in range(KMAX + 1)]
    for n in range(1, KMAX + 1):
        for j in range(1, n + 1):
            coeff[n][j] = S2[n][j] * inv[j + 1] % MOD
    return coeff


COEFF = build_stirling_and_coeff()


# -------------------------- precompute power sums for t<=1e6 --------------------------


def build_power_sum_table():
    """
    ps[k, t] = sum_{m=1..t} m^k mod MOD for k<=50, t<=1e6.
    Stored in a flattened array('I') of length (KMAX+1)*(MAX_PRECOMP+1).
    """
    total_size = (KMAX + 1) * STRIDE
    ps = array("I", [0]) * total_size
    bases = [k * STRIDE for k in range(KMAX + 1)]

    # For each t from 1..MAX_PRECOMP compute all powers t^k incrementally.
    for t in range(1, STRIDE):
        x = t  # t < MOD here
        p = x
        for k in range(1, KMAX + 1):
            idx = bases[k] + t
            ps[idx] = (ps[idx - 1] + p) % MOD
            p = (p * x) % MOD

    return ps, bases


PS_TABLE, BASES = build_power_sum_table()


# -------------------------- power sum for large t (>1e6) --------------------------


def power_sum_large(t: int, k: int, row):
    """
    Compute sum_{m<=t} m^k mod MOD using the falling-factorial formula:
      sum_{m=1}^t m^k = sum_{j=1}^k S2(k,j)/(j+1) * (t+1)_{j+1}
    where (t+1)_{j+1} is the falling factorial:
      (t+1)*(t)*...*(t-j)
    """
    n = t % MOD
    prod = (n + 1) % MOD  # will become (n+1)_{j+1} after multiplying factors
    res = 0
    for j in range(1, k + 1):
        prod = (prod * ((n + 1 - j) % MOD)) % MOD
        res = (res + row[j] * prod) % MOD
    return res


# -------------------------- core computation: S_k(n) --------------------------


def compute_Sk(n: int, k: int, primes_full, p2_full):
    """
    Compute S_k(n) mod MOD using:
      S_k(n) = sum_{d powerful<=n} h_k(d) * sum_{m<=n/d} m^k
    where h_k is multiplicative with:
      h_k(p^e)=p^k - p^{2k} for e>=2
    """
    limit = int(math.isqrt(n))
    m = bisect_right(primes_full, limit)
    primes = primes_full[:m]
    p2 = p2_full[:m]

    # Build c[i] = p^k - p^{2k} mod MOD
    c = array("I", [0]) * m
    for i, p in enumerate(primes):
        pk = pow(p, k, MOD)
        c[i] = (pk - (pk * pk) % MOD) % MOD

    base = BASES[k]
    row = COEFF[k]
    ps = PS_TABLE
    mod = MOD
    max_pre = MAX_PRECOMP

    cache_large = {}

    def powsum(t: int) -> int:
        if t <= max_pre:
            return ps[base + t]
        v = cache_large.get(t)
        if v is not None:
            return v
        v = power_sum_large(t, k, row)
        cache_large[t] = v
        return v

    sys.setrecursionlimit(10_000)
    ans = 0

    def dfs(start_idx: int, v: int, w: int):
        nonlocal ans
        ans = (ans + powsum(n // v) * w) % mod

        # enumerate next prime factor (with exponent >=2)
        for i in range(start_idx, m):
            vv = v * p2[i]
            if vv > n:
                break
            ww = (w * c[i]) % mod
            p = primes[i]
            while vv <= n:
                dfs(i + 1, vv, ww)
                if vv > n // p:
                    break
                vv *= p

    dfs(0, 1, 1)
    return ans


# -------------------------- optimized total solve for k=1..50 at n=1e12 --------------------------


def solve_total():
    """
    Compute sum_{k=1..50} S_k(10^12) mod MOD.
    Uses incremental p^k updates for primes to avoid repeated pow().
    """
    n = N_TARGET
    limit = int(math.isqrt(n))
    primes = sieve_primes(limit)
    p2 = [p * p for p in primes]
    m = len(primes)

    ps = PS_TABLE
    bases = BASES
    coeff = COEFF
    mod = MOD
    max_pre = MAX_PRECOMP

    pk = array("I", [1]) * m  # pk[i] will hold p_i^k mod MOD
    c = array("I", [0]) * m

    sys.setrecursionlimit(10_000)

    total = 0

    for k in range(1, KMAX + 1):
        # Update pk and c for this k
        for i, p in enumerate(primes):
            pkv = (pk[i] * p) % mod
            pk[i] = pkv
            c[i] = (pkv - (pkv * pkv) % mod) % mod

        base = bases[k]
        row = coeff[k]
        cache_large = {}

        def powsum(t: int) -> int:
            if t <= max_pre:
                return ps[base + t]
            v = cache_large.get(t)
            if v is not None:
                return v
            v = power_sum_large(t, k, row)
            cache_large[t] = v
            return v

        ans_k = 0

        def dfs(start_idx: int, v: int, w: int):
            nonlocal ans_k
            ans_k = (ans_k + powsum(n // v) * w) % mod
            for i in range(start_idx, m):
                vv = v * p2[i]
                if vv > n:
                    break
                ww = (w * c[i]) % mod
                p = primes[i]
                while vv <= n:
                    dfs(i + 1, vv, ww)
                    if vv > n // p:
                        break
                    vv *= p

        dfs(0, 1, 1)
        total = (total + ans_k) % mod

    return total


# -------------------------- test helpers (for statement asserts) --------------------------


def run_asserts():
    primes_full = sieve_primes(MAX_PRECOMP)
    p2_full = [p * p for p in primes_full]

    # Given examples in statement
    assert compute_Sk(10, 1, primes_full, p2_full) == 41
    assert compute_Sk(100, 1, primes_full, p2_full) == 3512
    assert compute_Sk(100, 2, primes_full, p2_full) == 208090
    assert compute_Sk(10000, 1, primes_full, p2_full) == 35252550

    # Given example: sum_{k=1..3} S_k(10^8) mod MOD == 338787512
    n = 10**8
    s = 0
    for k in (1, 2, 3):
        s = (s + compute_Sk(n, k, primes_full, p2_full)) % MOD
    assert s == 338787512


def main():
    run_asserts()
    print(solve_total())


if __name__ == "__main__":
    main()
