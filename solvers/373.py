#!/usr/bin/env python3
"""Project Euler 373: Circumscribed Circles

We need S(n) = sum of circumradii r (with multiplicity) over all integer-sided
triangles whose circumradius is an integer and does not exceed n.

Key known result (can be derived via representations of r as a sum of two
squares / Gaussian integers): if

    r = \prod p_i^{e_i} * q

where the p_i are exactly the primes with p_i \equiv 1 (mod 4) appearing in r's
factorization (q contains all other prime powers), then the number of integer-
sided triangles with circumradius exactly r is

    N(r) = (1/6) * ( 2*A - 3*B + 3*C - 2 )

with
    A = \prod (3e_i^2 + 3e_i + 1)
    B = \prod (2e_i + 1)
    C = \prod (2*floor(e_i/2) + 1)

Empty products are 1.

Then
    S(n) = \sum_{r=1..n} r * N(r).

This implementation builds a smallest-prime-factor table with a linear sieve
and factorizes each r to extract exponents e_i for primes \equiv 1 (mod 4).

No external libraries are used.
"""

from __future__ import annotations

from array import array
import sys


def build_spf(n: int) -> array:
    """Return array spf where spf[x] is the smallest prime factor of x (for x>=2)."""
    spf = array("I", [0]) * (n + 1)
    primes = array("I")

    for i in range(2, n + 1):
        if spf[i] == 0:
            spf[i] = i
            primes.append(i)

        si = spf[i]
        for p in primes:
            ip = i * p
            if ip > n:
                break
            spf[ip] = p
            if p == si:
                break

    return spf


def S(n: int) -> int:
    """Compute S(n) as defined in Project Euler 373."""
    if n < 1:
        return 0

    spf = build_spf(n)
    spf_local = spf

    # Max exponent needed for primes p\equiv 1 (mod 4) up to 1e7 is small.
    # (For p=5, 5^10 < 1e7 < 5^11.) 24 is a safe bound.
    MAX_E = 24
    t1 = [0] * (MAX_E + 1)  # 3e^2+3e+1
    t2 = [0] * (MAX_E + 1)  # 2e+1
    t3 = [0] * (MAX_E + 1)  # 2*(e//2)+1
    for e in range(MAX_E + 1):
        t1[e] = 3 * e * e + 3 * e + 1
        t2[e] = 2 * e + 1
        t3[e] = 2 * (e >> 1) + 1

    total = 0

    for r in range(1, n + 1):
        x = r
        prod1 = 1
        prod2 = 1
        prod3 = 1

        while x > 1:
            p = spf_local[x]
            e = 1
            x //= p
            while x % p == 0:
                x //= p
                e += 1

            if p & 3 == 1:  # p % 4 == 1
                # e is at most ~10 for p≡1 (mod 4) when n<=1e7, but keep safe.
                prod1 *= t1[e]
                prod2 *= t2[e]
                prod3 *= t3[e]

        # If no primes p≡1 (mod 4) divide r, then N(r)=0.
        if prod1 == 1:
            continue

        cnt = (2 * prod1 - 3 * prod2 + 3 * prod3 - 2) // 6
        if cnt:
            total += r * cnt

    return total


def main(argv: list[str]) -> None:
    # Problem statement test values
    assert S(100) == 4950
    assert S(1200) == 1653605

    n = 10_000_000
    if len(argv) >= 2:
        n = int(argv[1])

    print(S(n))


if __name__ == "__main__":
    main(sys.argv)
