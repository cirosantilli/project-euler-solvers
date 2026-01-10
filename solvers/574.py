#!/usr/bin/env python3
"""
Project Euler 574 - Verifying Primes

Compute S(3800) where:
- q is a prime, A >= B > 0, gcd(A,B)=1
- AB divisible by every prime < q
- p is verified prime if p = A+B < q^2 or p = A-B with 1<p<q^2

Let V(p) be the smallest possible A in any verifying representation.
Let S(n) = sum_{prime p < n} V(p).

This program prints S(3800).
"""

from __future__ import annotations

import bisect
import math


def sieve(limit: int) -> list[int]:
    """Sieve of Eratosthenes (returns all primes <= limit)."""
    if limit < 2:
        return []
    is_prime = bytearray(b"\x01") * (limit + 1)
    is_prime[0:2] = b"\x00\x00"
    r = int(math.isqrt(limit))
    for p in range(2, r + 1):
        if is_prime[p]:
            start = p * p
            step = p
            is_prime[start : limit + 1 : step] = b"\x00" * (
                ((limit - start) // step) + 1
            )
    return [i for i in range(2, limit + 1) if is_prime[i]]


def _egcd(a: int, b: int) -> tuple[int, int, int]:
    """Extended Euclid: returns (g,x,y) with ax+by=g=gcd(a,b)."""
    if b == 0:
        return a, 1, 0
    g, x1, y1 = _egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def modinv(a: int, m: int) -> int:
    """Modular inverse of a mod m (m is prime in this problem)."""
    a %= m
    g, x, _y = _egcd(a, m)
    if g != 1:
        raise ValueError("No modular inverse")
    return x % m


class CRTData:
    __slots__ = ("q", "primes_lt_q", "modulus", "bases")

    def __init__(
        self, q: int, primes_lt_q: list[int], modulus: int, bases: list[int]
    ) -> None:
        self.q = q
        self.primes_lt_q = primes_lt_q
        self.modulus = modulus
        self.bases = bases


def build_crt_data(primes_for_q: list[int]) -> dict[int, CRTData]:
    """
    For each prime q, precompute:
    - P = primes < q
    - M = product(P)
    - CRT basis elements base_r such that:
        base_r ≡ 1 (mod r)
        base_r ≡ 0 (mod s) for every other prime s in P
    """
    data: dict[int, CRTData] = {}
    for q in primes_for_q:
        P = [r for r in primes_for_q if r < q]
        M = 1
        for r in P:
            M *= r
        bases: list[int] = []
        for r in P:
            Mr = M // r
            inv = modinv(Mr % r, r)
            bases.append((Mr * inv) % M)
        data[q] = CRTData(q, P, M, bases)
    return data


def subset_sums_mod(terms: list[int], mod: int) -> list[int]:
    """All subset sums modulo mod. (len(terms) <= 9 in our meet-in-middle halves)."""
    sums = [0]
    for t in terms:
        sums += [(x + t) % mod for x in sums]
    return sums


def q_for_p(p: int, prime_list: list[int]) -> int:
    """Smallest prime q with q*q > p."""
    for q in prime_list:
        if q * q > p:
            return q
    raise ValueError("q not found (increase sieve bound)")


def min_B_difference(p: int, crt: CRTData) -> int:
    """
    Difference case: p = A - B, A = B + p.

    For each prime r<q, either r|B (=> B ≡ 0 mod r) or r|A (=> B ≡ -p mod r).
    Each set of choices gives a unique residue class B ≡ b0 (mod M), where
      M = ∏_{r<q} r.

    We want the smallest positive B with gcd(A,B)=1.
    For prime p, gcd(B+p, B) = gcd(B, p), so we only need B not divisible by p.

    Because p ∤ M, any residue b0 in 1..M-1 that is divisible by p would force B=b0 (invalid)
    and the next B in that class is b0+M (>M), which can never beat any valid residue < M.
    So we only search for the smallest residue b0 in 1..M-1 with b0 % p != 0;
    if none exists, the best we can do is b0=0 -> B=M.
    """
    P = crt.primes_lt_q
    M = crt.modulus
    if not P:
        return 1  # no constraints: smallest B

    terms = [(((-p) % r) * base) % M for r, base in zip(P, crt.bases)]
    k = len(terms)
    mid = k // 2

    L = subset_sums_mod(terms[:mid], M)
    R = subset_sums_mod(terms[mid:], M)
    R.sort()

    best: int | None = None

    # Subsets entirely from one half (other half empty).
    for arr in (L, R):
        for x in arr:
            if x != 0 and (x % p) != 0:
                if best is None or x < best:
                    best = x

    if best is None:
        best = M  # b0==0 -> B=M

    # Wrap-around combinations can yield very small residues.
    for l in L:
        target = M - l
        idx = bisect.bisect_left(R, target)
        j = idx
        while j < len(R):
            s = l + R[j]
            if s == M:
                j += 1
                continue  # residue 0 invalid
            if s < M:
                break  # no wrap; residue won't beat current best
            res = s - M
            if res >= best:
                break
            if (res % p) != 0:
                best = res
                break
            j += 1

    return best


def max_B_sum(p: int, crt: CRTData) -> int | None:
    """
    Sum case: p = A + B, A = p - B, with A>=B => B <= floor(p/2).

    For each prime r<q, either r|B (=> B ≡ 0 mod r) or r|A (=> B ≡ p mod r).

    We maximize B <= floor(p/2). Return max B, or None if impossible.
    """
    P = crt.primes_lt_q
    M = crt.modulus
    limit = p // 2

    if not P:
        return limit

    # If the required primorial exceeds the maximum possible A*B, no sum solution exists.
    Amax = p - limit
    Bmax = limit
    if M > Amax * Bmax:
        return None

    terms = [((p % r) * base) % M for r, base in zip(P, crt.bases)]
    residues = subset_sums_mod(terms, M)

    bestB = 0
    for b0 in residues:
        if b0 == 0:
            if M <= limit:
                B = (limit // M) * M
                if B > bestB:
                    bestB = B
        else:
            if b0 <= limit:
                B = b0 + ((limit - b0) // M) * M
                if B > bestB:
                    bestB = B

    return None if bestB == 0 else bestB


def V_of_prime(p: int, prime_qs: list[int], crt_by_q: dict[int, CRTData]) -> int:
    """
    Compute V(p) for a prime p using q = smallest prime with q^2 > p.
    """
    q = q_for_p(p, prime_qs)
    crt = crt_by_q[q]

    # Difference representation (always considered).
    Adiff = p + min_B_difference(p, crt)

    # Sum representation (only if feasible).
    Bsum = max_B_sum(p, crt)
    if Bsum is None:
        return Adiff
    Asum = p - Bsum
    return Asum if Asum < Adiff else Adiff


def S(n: int) -> int:
    primes_all = sieve(max(100, n + 10))
    primes_under_n = [p for p in primes_all if p < n]

    # q needed up to next prime above sqrt(n)
    max_q_needed = 0
    for p in primes_under_n:
        q = q_for_p(p, primes_all)
        if q > max_q_needed:
            max_q_needed = q
    prime_qs = [q for q in primes_all if q <= max_q_needed]

    crt_by_q = build_crt_data(prime_qs)

    total = 0
    for p in primes_under_n:
        total += V_of_prime(p, prime_qs, crt_by_q)
    return total


def _self_test() -> None:
    # Test values from the problem statement.
    primes_all = sieve(5000)
    prime_qs = [q for q in primes_all if q <= 100]
    crt_by_q = build_crt_data(prime_qs)

    def V_local(p: int) -> int:
        return V_of_prime(p, prime_qs, crt_by_q)

    assert V_local(2) == 1
    assert V_local(37) == 22
    assert V_local(151) == 165
    assert S(10) == 10
    assert S(200) == 7177


def main() -> None:
    _self_test()
    print(S(3800))


if __name__ == "__main__":
    main()
