#!/usr/bin/env python3
"""
Project Euler 465: Polar Polygons

Compute P(7^13) mod 1,000,000,007.

No external libraries are used (only Python standard library).
"""

from __future__ import annotations

import os
import sys
from array import array
from typing import Dict, Tuple

MOD = 1_000_000_007


def polar_polygons_exact(n: int) -> int:
    """
    Exact P(n) for small n (used only for the given sample asserts).
    Uses the closed-form reduction, but evaluates with Python big integers.
    """
    if n <= 0:
        return 0

    # Simple totient sieve up to n (tiny for the sample values 1..3).
    phi = list(range(n + 1))
    for i in range(2, n + 1):
        if phi[i] == i:
            for j in range(i, n + 1, i):
                phi[j] -= phi[j] // i

    B = 1
    S1 = 0
    S2 = 0
    for m in range(1, n + 1):
        q = n // m
        c = 4 * phi[m]
        B *= (q + 1) ** c
        S1 += c * q
        S2 += c * q * q

    return B * B - 2 * B * S1 + S2 - 1


def build_totient_prefix(limit: int) -> array:
    """
    Build prefix sums of Euler's totient function:
        pref[x] = sum_{k=1..x} phi(k)
    using an O(limit) linear sieve.

    Memory-friendly:
      - phi: array('I') (4 bytes per entry)
      - prefix: array('Q') (8 bytes per entry)
    """
    if limit < 1:
        return array("Q", [0])

    phi = array("I", [0]) * (limit + 1)
    phi[1] = 1
    primes = []  # Python list is fast for iteration

    for i in range(2, limit + 1):
        if phi[i] == 0:  # i is prime
            phi[i] = i - 1
            primes.append(i)
        for p in primes:
            ip = i * p
            if ip > limit:
                break
            if i % p == 0:
                phi[ip] = phi[i] * p
                break
            else:
                phi[ip] = phi[i] * (p - 1)

    pref = array("Q", [0]) * (limit + 1)
    s = 0
    for i in range(1, limit + 1):
        s += phi[i]
        pref[i] = s
    return pref


def make_totient_sum(limit: int):
    """
    Returns a function TotSum(n) = sum_{k=1..n} phi(k) for n up to the problem size,
    using:
      - precomputed prefix sums up to `limit`
      - Du Jiao-style recursion with memoization for larger n

    This is the workhorse for handling n as large as 7^13.
    """
    pref = build_totient_prefix(limit)
    cache: Dict[int, int] = {}

    sys.setrecursionlimit(1_000_000)

    def tot_sum(n: int) -> int:
        if n <= limit:
            return int(pref[n])
        v = cache.get(n)
        if v is not None:
            return v

        # Standard recursion:
        #   S(n) = n(n+1)/2 - sum_{l=2..n} (r-l+1)*S(floor(n/l))
        res = n * (n + 1) // 2
        l = 2
        while l <= n:
            q = n // l
            r = n // q
            res -= (r - l + 1) * tot_sum(q)
            l = r + 1

        cache[n] = res
        return res

    return tot_sum


def polar_polygons_mod(n: int, tot_sum) -> int:
    """
    Compute P(n) mod MOD using the derived closed form:

        Let q(m) = floor(n/m).
        Let c_m = 4*phi(m).

        B  = Π_{m=1..n} (1 + q(m))^{c_m}
        S1 = Σ_{m=1..n} c_m * q(m)
        S2 = Σ_{m=1..n} c_m * q(m)^2

        P(n) = B^2 - 2*B*S1 + S2 - 1   (mod MOD)

    We group by constant q(m): for m in [l..r], q is constant.
    The needed totient sums over [l..r] are obtained from TotSum(r)-TotSum(l-1).
    """
    B = 1
    S1 = 0
    S2 = 0

    l = 1
    prev_phi_sum = 0  # TotSum(l-1); we update incrementally so we only call TotSum(r) once per block
    modm1 = MOD - 1

    B_zero = False  # once B becomes 0 (mod MOD) it stays 0

    while l <= n:
        q = n // l
        r = n // q

        curr_phi_sum = tot_sum(r)
        sum_phi_block = curr_phi_sum - prev_phi_sum
        prev_phi_sum = curr_phi_sum

        # c_block = 4 * sum_phi_block
        sum_phi_mod = sum_phi_block % MOD
        c_block_mod = (sum_phi_mod * 4) % MOD

        q_mod = q % MOD
        S1 = (S1 + c_block_mod * q_mod) % MOD

        q2_mod = (q_mod * q_mod) % MOD
        S2 = (S2 + c_block_mod * q2_mod) % MOD

        if not B_zero:
            base = (q + 1) % MOD
            if base == 0:
                # exponent is positive for any non-empty block, so this factor forces B ≡ 0 (mod MOD).
                B = 0
                B_zero = True
            else:
                # Fermat reduction is valid because base != 0 (mod MOD) and MOD is prime.
                exp = ((sum_phi_block % modm1) * 4) % modm1
                B = (B * pow(base, exp, MOD)) % MOD

        l = r + 1

    return (B * B - 2 * B * S1 + S2 - 1) % MOD


def main() -> None:
    # Sample asserts from the problem statement
    assert polar_polygons_exact(1) == 131
    assert polar_polygons_exact(2) == 1648531
    assert polar_polygons_exact(3) == 1099461296175

    # Target (default) or optional CLI input
    if len(sys.argv) >= 2 and sys.argv[1].lstrip("-").isdigit():
        n = int(sys.argv[1])
    else:
        n = 7**13

    # Totient-sum precompute size:
    # Default is tuned for a reasonable memory footprint in Python.
    # You can override with environment variable PE465_LIMIT.
    default_limit = 5_000_000
    limit_env = os.getenv("PE465_LIMIT")
    if limit_env is not None:
        try:
            default_limit = int(limit_env)
        except ValueError:
            pass
    limit = min(default_limit, n)

    tot_sum = make_totient_sum(limit)

    # Sample modular check from the statement (uses the same machinery)
    assert polar_polygons_mod(343, tot_sum) == 937293740

    ans = polar_polygons_mod(n, tot_sum)
    print(ans)


if __name__ == "__main__":
    main()
