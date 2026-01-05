#!/usr/bin/env python3
"""Project Euler 441: The inverse summation of coprime couples.

No external libraries are used.

The program prints S(10^7) rounded to 4 decimal places.

It also includes asserts for the sample values given in the problem statement.
"""

from __future__ import annotations

from array import array
from math import gcd
import sys


def brute_S(n: int) -> float:
    """Brute force computation of S(n) for small n (used for sample asserts)."""

    def R(m: int) -> float:
        s = 0.0
        for q in range(2, m + 1):
            for p in range(1, q):
                if p + q >= m and gcd(p, q) == 1:
                    s += 1.0 / (p * q)
        return s

    return sum(R(m) for m in range(2, n + 1))


def mobius_sieve(limit: int) -> array:
    """Return Möbius mu[0..limit] as array('b') using a linear sieve."""
    mu = array("b", [0]) * (limit + 1)
    mu[1] = 1

    is_comp = bytearray(limit + 1)
    primes: list[int] = []

    for i in range(2, limit + 1):
        if not is_comp[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            ip = i * p
            if ip > limit:
                break
            is_comp[ip] = 1
            if i % p == 0:
                mu[ip] = 0
                break
            mu[ip] = -mu[i]

    return mu


def harmonic_arrays(n: int) -> tuple[array, array]:
    """Return (H, H2) where

    H[k]  = sum_{i=1..k} 1/i
    H2[k] = sum_{i=1..k} 1/i^2

    Stored as array('d') for memory efficiency and O(1) access.

    Note on numeric stability:
    We build the prefix sums with **Kahan compensated summation**. For n = 10^7,
    naive summation accumulates enough rounding error to shift the final answer in
    the 4th decimal place, while compensation keeps the result stable.
    """
    H = array("d", [0.0]) * (n + 1)
    H2 = array("d", [0.0]) * (n + 1)

    h = 0.0
    c = 0.0  # compensation for H
    h2 = 0.0
    c2 = 0.0  # compensation for H2

    for i in range(1, n + 1):
        inv = 1.0 / i

        # Kahan summation for h
        y = inv - c
        t = h + y
        c = (t - h) - y
        h = t
        H[i] = h

        inv2 = inv * inv

        # Kahan summation for h2
        y = inv2 - c2
        t = h2 + y
        c2 = (t - h2) - y
        h2 = t
        H2[i] = h2

    return H, H2


def solve(n: int = 10_000_000) -> float:
    """Compute S(n) as defined in the problem."""
    half = n // 2

    # Möbius values are only needed up to n//2 for this derivation.
    mu = mobius_sieve(half)

    # Harmonic numbers up to n.
    H, H2 = harmonic_arrays(n)

    # Helpers using closed forms to avoid extra prefix arrays.
    # P1(t) = sum_{k=1..t} H_{k-1} / k = (H_t^2 - H2_t) / 2
    def P1(t: int) -> float:
        if t <= 0:
            return 0.0
        ht = H[t]
        return 0.5 * (ht * ht - H2[t])

    # sum_H(t) = sum_{k=1..t} H_k = (t+1)*H_t - t
    def sum_H(t: int) -> float:
        if t <= 0:
            return 0.0
        return (t + 1) * H[t] - t

    # sum_Hm1(t) = sum_{k=1..t} H_{k-1} = sum_{j=0..t-1} H_j
    #           = t*H_{t-1} - (t-1)   for t>=2, else 0
    def sum_Hm1(t: int) -> float:
        if t <= 1:
            return 0.0
        return t * H[t - 1] - (t - 1)

    # Part 1: q <= n/2
    s_phi_over_q = 0.0
    s_btotal_over_q = 0.0

    for d in range(1, half + 1):
        md = mu[d]
        if md == 0:
            continue
        inv_d = 1.0 / d
        inv_d2 = inv_d * inv_d
        k = half // d
        s_phi_over_q += md * k * inv_d
        s_btotal_over_q += md * P1(k) * inv_d2

    # Remove q=1 term from phi(q)/q sum (phi(1)/1 = 1).
    s_phi_over_q -= 1.0

    # Parts for q > n/2: computed by swapping the Möbius/divisor sums.
    s_A = 0.0
    s_weighted_btotal = 0.0
    s_B_combined = 0.0

    # Cache for S2(M,L) = sum_{r=1..L} H_r / (M-r)
    # Used in the B(q, n-q) term. Many (M,L) pairs repeat for large d.
    s2_cache: dict[tuple[int, int], float] = {}
    H_local = H

    def S2_prefix(M: int, L: int) -> float:
        if L <= 0:
            return 0.0
        key = (M, L)
        cached = s2_cache.get(key)
        if cached is not None:
            return cached
        # Sum_{r=1..L} H[r] / (M-r)
        s = 0.0
        denom = M - 1
        # denom decreases by 1 each step, avoiding recomputing (M-r).
        for r in range(1, L + 1):
            s += H_local[r] / denom
            denom -= 1
        s2_cache[key] = s
        return s

    for d in range(1, half + 1):
        md = mu[d]
        if md == 0:
            continue
        inv_d = 1.0 / d
        inv_d2 = inv_d * inv_d

        M = n // d
        a = n // (2 * d) + 1  # lower bound for k (since q=d*k > n/2)

        # A(q, n-q)/q contribution (counting coprime p in a range)
        inner_A = M * (H[M] - H[a - 1]) - (M - a + 1)
        s_A += md * inner_A * inv_d

        # (n-q+1)/q * B_total(q) contribution
        s_over_k = P1(M) - P1(a - 1)
        s_hm1 = sum_Hm1(M) - sum_Hm1(a - 1)
        s_weighted_btotal += md * ((n + 1) * s_over_k * inv_d2 - s_hm1 * inv_d)

        # Combined coefficient for B(q, n-q): (q-N)/q
        L = M - a
        s_rev = sum_H(L)  # sum_{r=1..L} H_r (H_0=0)
        s2 = S2_prefix(M, L)
        s_B_combined += md * (s_rev * inv_d - n * s2 * inv_d2)

    return s_phi_over_q + s_btotal_over_q + s_A + s_weighted_btotal + s_B_combined


def _run_sample_asserts() -> None:
    # Samples from the problem statement:
    # S(2) = 1/2
    # S(10) ≈ 6.9147
    # S(100) ≈ 58.2962
    s2 = brute_S(2)
    s10 = brute_S(10)
    s100 = brute_S(100)

    assert abs(s2 - 0.5) < 1e-12
    assert round(s10, 4) == 6.9147
    assert round(s100, 4) == 58.2962


def main() -> None:
    _run_sample_asserts()

    n = 10_000_000
    if len(sys.argv) >= 2:
        n = int(sys.argv[1])

    ans = solve(n)
    # Problem asks for rounded to 4 decimal places.
    print(f"{ans:.4f}")


if __name__ == "__main__":
    main()
