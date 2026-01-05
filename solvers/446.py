#!/usr/bin/env python3
"""
Project Euler 446 - Retractions B

Compute:
    F(N) = sum_{n=1..N} R(n^4 + 4)  (mod 1_000_000_007)
where R(m) counts affine "retractions" f(x)=a x + b (mod m) with:
    0 < a < m, 0 <= b < m
and f(f(x)) ≡ f(x) (mod m) for all x.

Run:
    python3 main.py            # computes F(10^7) mod 1e9+7
    python3 main.py 1024       # computes F(1024) mod 1e9+7

No external libraries are used.
"""
from __future__ import annotations

import sys
from array import array
from math import isqrt

MOD = 1_000_000_007


# -------------------------
# Number theory utilities
# -------------------------
def primes_upto(limit: int) -> list[int]:
    """Return all primes <= limit using an odd-only sieve (bytearray)."""
    if limit < 2:
        return []
    # sieve[i] represents odd number (2*i+1)
    sieve = bytearray(b"\x01") * (limit // 2 + 1)
    sieve[0] = 0  # 1 is not prime
    r = isqrt(limit)
    for x in range(3, r + 1, 2):
        if sieve[x // 2]:
            start = x * x // 2
            step = x
            sieve[start::step] = b"\x00" * (((len(sieve) - start - 1) // step) + 1)
    primes = [2]
    primes.extend(2 * i + 1 for i in range(1, len(sieve)) if sieve[i])
    return primes


# For primes p ≡ 1 (mod 4), sqrt(-1) exists mod p.
# If g is a quadratic non-residue mod p, then g^((p-1)/4)^2 = g^((p-1)/2) ≡ -1 (mod p).
_NONRES_CANDIDATES = (
    2,
    3,
    5,
    7,
    11,
    13,
    17,
    19,
    23,
    29,
    31,
    37,
    41,
    43,
    47,
    53,
    59,
    61,
    67,
    71,
    73,
    79,
    83,
    89,
    97,
    101,
    103,
    107,
    109,
    113,
)


def sqrt_minus_one_mod_prime(p: int) -> int:
    """
    Return r such that r^2 ≡ -1 (mod p), for an odd prime p ≡ 1 (mod 4).
    """
    assert p % 4 == 1
    leg_exp = (p - 1) // 2
    quarter = (p - 1) // 4
    # Find a small quadratic non-residue g via Euler's criterion.
    for g in _NONRES_CANDIDATES:
        if g >= p:
            break
        if pow(g, leg_exp, p) == p - 1:
            return pow(g, quarter, p)
    # Very rare fallback: scan odd g until a non-residue is found.
    g = 115
    while True:
        if pow(g, leg_exp, p) == p - 1:
            return pow(g, quarter, p)
        g += 2


# -------------------------
# Small exact check (from statement)
# -------------------------
def _prime_powers_small(x: int) -> list[int]:
    """Return prime powers p^k (not (p,k)) in the factorization of x. For small x."""
    res: list[int] = []
    d = 2
    while d * d <= x:
        if x % d == 0:
            pe = 1
            while x % d == 0:
                x //= d
                pe *= d
            res.append(pe)
        d = 3 if d == 2 else d + 2
    if x > 1:
        res.append(x)
    return res


def F_exact_small(N: int) -> int:
    """
    Exact F(N) for small N (used only for assertions).
    Uses:
        n^4+4 = ((n-1)^2+1)*((n+1)^2+1)
    and the fact that odd primes cannot divide both factors; only 2 can (when n is even).
    """
    K = N + 1
    C = [k * k + 1 for k in range(K + 1)]  # k=0..N+1
    P = [1] * (K + 1)
    for k in range(K + 1):
        prod = 1
        for pe in _prime_powers_small(C[k]):
            prod *= 1 + pe
        P[k] = prod

    total = 0
    for n in range(1, N + 1):
        left_k = n - 1
        right_k = n + 1
        m = C[left_k] * C[right_k]
        if n % 2 == 0:
            # Both C[left_k] and C[right_k] are divisible by 2 exactly once,
            # so P[left_k] and P[right_k] each contain a factor (1+2)=3.
            pm = (P[left_k] // 3) * (P[right_k] // 3) * (1 + 4)
        else:
            pm = P[left_k] * P[right_k]
        total += pm - m
    return total


# -------------------------
# Main fast solver
# -------------------------
def solve(N: int = 10_000_000) -> int:
    """
    Compute F(N) mod MOD for N up to 10^7.

    Key identity:
        n^4 + 4 = ((n-1)^2 + 1) * ((n+1)^2 + 1)

    Let C_k = k^2 + 1 and P_k = Π_{p^e || C_k} (1 + p^e) (mod MOD).
    For odd n: gcd(C_{n-1}, C_{n+1}) = 1
    For even n: gcd(C_{n-1}, C_{n+1}) = 2 and each has only one factor of 2

    Then:
        R(n^4+4) ≡ P_{n-1} * P_{n+1} (adjusted for 2)  -  (C_{n-1} * C_{n+1})   (mod MOD)
    """
    if N < 1:
        return 0

    k_max = N + 1  # we need k=0..N+1
    prime_limit = k_max  # since max(C_k) ~= k_max^2, sqrt(max(C_k)) <= k_max

    # Precompute primes <= prime_limit and roots of x^2 ≡ -1 (mod p) for p ≡ 1 (mod 4).
    primes = primes_upto(prime_limit)
    p_list = array("I", [2])
    r_list = array("I", [1])  # root for p=2 is 1 (since 1^2+1 is even)
    for p in primes[1:]:
        if (p & 3) == 1:  # p % 4 == 1
            p_list.append(p)
            r_list.append(sqrt_minus_one_mod_prime(p))

    # Correction factor for n even:
    # P_{n-1} includes (1+2), P_{n+1} includes (1+2), but in product the 2-adic part is 2^2.
    # So multiply by (1+4)/((1+2)^2) = 5/9 in mod arithmetic.
    correction_even = (5 * pow(9, MOD - 2, MOD)) % MOD

    # Stream through k = 0..N+1 in blocks and accumulate F(N).
    block_size = 1_000_000  # tuneable; larger => fewer prime-loops
    total = 0

    prev2_P = None  # P_{k-2}
    prev1_P = None  # P_{k-1}
    prev2_C = None  # C_{k-2} mod MOD
    prev1_C = None  # C_{k-1} mod MOD

    for L in range(0, k_max + 1, block_size):
        R = min(k_max + 1, L + block_size)
        size = R - L

        rem = array("Q", [0]) * size  # remaining unfactored part of C_k
        prod = array("I", [1]) * size  # P_k mod MOD
        cmod = array("I", [0]) * size  # C_k mod MOD

        # Fill rem and cmod for k in [L, R)
        k = L
        v = k * k + 1
        for i in range(size):
            rem[i] = v
            cmod[i] = v % MOD
            v += 2 * k + 1  # next (k+1)^2 + 1
            k += 1

        # Sieve prime factors using modular roots of k^2 ≡ -1 (mod p)
        mod = MOD
        rem_arr = rem
        prod_arr = prod
        for j in range(len(p_list)):
            p = p_list[j]
            r = r_list[j]
            if p == 2:
                # k^2+1 is even iff k is odd, and then v2(k^2+1)=1 always.
                start = (1 - L) & 1
                for idx in range(start, size, 2):
                    rem_arr[idx] //= 2
                    prod_arr[idx] = (prod_arr[idx] * 3) % mod  # (1 + 2)
                continue

            # root r
            start = (r - L) % p
            for idx in range(start, size, p):
                x = rem_arr[idx] // p
                pe = p
                # check for higher powers (rare)
                while x % p == 0:
                    x //= p
                    pe *= p
                rem_arr[idx] = x
                t = pe + 1
                if t >= mod:
                    t %= mod
                prod_arr[idx] = (prod_arr[idx] * t) % mod

            # root p-r
            r2 = p - r
            start = (r2 - L) % p
            for idx in range(start, size, p):
                x = rem_arr[idx] // p
                pe = p
                while x % p == 0:
                    x //= p
                    pe *= p
                rem_arr[idx] = x
                t = pe + 1
                if t >= mod:
                    t %= mod
                prod_arr[idx] = (prod_arr[idx] * t) % mod

        # Any remaining factor is 1 or a prime > prime_limit
        for i in range(size):
            x = rem_arr[i]
            if x > 1:
                t = x + 1
                if t >= mod:
                    t %= mod
                prod_arr[i] = (prod_arr[i] * t) % mod

        # Stream k in this block and accumulate R(n^4+4) for n = k-1
        for i in range(size):
            k = L + i
            Pk = prod_arr[i]
            Ck = cmod[i]

            if prev2_P is not None:
                n = k - 1
                if n <= N:
                    pm = (prev2_P * Pk) % mod
                    if (n & 1) == 0:
                        pm = (pm * correction_even) % mod
                    mm = (prev2_C * Ck) % mod
                    total = (total + pm - mm) % mod

            prev2_P, prev1_P = prev1_P, Pk
            prev2_C, prev1_C = prev1_C, Ck

    return total % MOD


def _self_test() -> None:
    # Test value from the problem statement:
    assert F_exact_small(1024) == 77532377300600
    # And its modulo form should match the fast solver:
    assert solve(1024) == (77532377300600 % MOD)


def main() -> None:
    _self_test()
    if len(sys.argv) > 2:
        print("Usage: python3 main.py [N]")
        raise SystemExit(2)
    N = int(sys.argv[1]) if len(sys.argv) == 2 else 10_000_000
    print(solve(N))


if __name__ == "__main__":
    main()
