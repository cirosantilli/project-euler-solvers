#!/usr/bin/env python3
"""
Project Euler 354: Distances in a Bee's Honeycomb

We work with the centres of the hexagonal cells. Those centres form a triangular (hexagonal) lattice.
With side length 1 for each hexagon, the distance between adjacent centres is sqrt(3).

Using integer coordinates (x, y) in a 2D basis for the triangular lattice, squared distances are:

    L^2 = 3 * (x^2 + x*y + y^2)

So for n = (L^2)/3, B(L) is the number of integer solutions to:
    x^2 + x*y + y^2 = n

A classical result for the Eisenstein integers gives:
    B(sqrt(3n)) = 6 * sum_{d|n} chi(d)

where chi is the Dirichlet character modulo 3:
    chi(d) =  1 if d ≡ 1 (mod 3)
           = -1 if d ≡ 2 (mod 3)
           =  0 if 3 | d

Let R(n) = sum_{d|n} chi(d). Then B = 6*R.

We need to count radii L <= 5e11 such that B(L)=450 -> R(n)=75, with n <= floor((5e11)^2/3).
"""

from __future__ import annotations

from bisect import bisect_left, bisect_right
from math import isqrt
from typing import Dict, List, Tuple


# ---------- small helpers (tests) ----------


def _trial_factorize(n: int) -> Dict[int, int]:
    """Trial division factorization. Fast enough for the problem statement asserts."""
    factors: Dict[int, int] = {}
    if n <= 1:
        return factors
    # factor out 2
    c = 0
    while n % 2 == 0:
        n //= 2
        c += 1
    if c:
        factors[2] = c
    d = 3
    while d * d <= n:
        if n % d == 0:
            c = 0
            while n % d == 0:
                n //= d
                c += 1
            factors[d] = c
        d += 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def _R_from_factors(factors: Dict[int, int]) -> int:
    """Compute R(n) = sum_{d|n} chi(d) from prime factorization of n."""
    r = 1
    for p, e in factors.items():
        if p == 3:
            continue
        if p % 3 == 1:
            r *= e + 1
        else:
            # p % 3 == 2
            if e & 1:
                return 0
    return r


def _B_from_n_small(n: int) -> int:
    """B(sqrt(3n)) for small n using trial factorization."""
    return 6 * _R_from_factors(_trial_factorize(n))


def _B_for_integer_L(L: int) -> int:
    """
    B(L) for integer L. For our assert we only need L divisible by 3.
    If L not attainable on the lattice, returns 0.
    """
    if L <= 0:
        return 0
    if L % 3 != 0:
        return 0  # then L^2/3 not an integer
    k = L // 3
    # n = L^2 / 3 = 3 * k^2, factor k and square exponents
    fk = _trial_factorize(k)
    fn: Dict[int, int] = {}
    for p, e in fk.items():
        fn[p] = 2 * e
    fn[3] = fn.get(3, 0) + 1
    return 6 * _R_from_factors(fn)


def _self_test() -> None:
    # From the problem statement:
    # B(sqrt(3)) = 6  -> n = 1
    assert _B_from_n_small(1) == 6
    # B(sqrt(21)) = 12 -> 21/3 = 7
    assert _B_from_n_small(7) == 12
    # B(111111111) = 54
    assert _B_for_integer_L(111_111_111) == 54


# ---------- core solution ----------


def _int_nth_root(n: int, k: int) -> int:
    """Return floor(n^(1/k)) for integers n>=0, k>=1 (binary search, exact)."""
    if n < 2:
        return n
    if k == 1:
        return n
    # upper bound from bit length
    hi = 1 << ((n.bit_length() + k - 1) // k)
    lo = 1
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**k <= n:
            lo = mid
        else:
            hi = mid
    return lo


def _sieve_primes(limit: int) -> List[int]:
    """Odd-only sieve of Eratosthenes: primes <= limit."""
    if limit < 2:
        return []
    size = limit // 2 + 1  # index i represents odd number 2*i+1
    sieve = bytearray(b"\x01") * size
    sieve[0] = 0  # 1 is not prime
    root = isqrt(limit)
    for i in range(1, root // 2 + 1):
        if sieve[i]:
            p = 2 * i + 1
            start = (p * p) // 2
            sieve[start::p] = b"\x00" * (((size - start - 1) // p) + 1)
    primes = [2]
    primes.extend(2 * i + 1 for i in range(1, size) if sieve[i])
    return primes


def _build_prefix_B(Bmax: int, primes: List[int]) -> List[int]:
    """
    Count of integers b <= x whose prime factors are all ≡ 2 (mod 3).
    (We keep 3 out of b and handle 3-powers separately.)
    """
    good = bytearray(b"\x01") * (Bmax + 1)
    good[0] = 0
    for p in primes:
        if p > Bmax:
            break
        if p == 3 or (p % 3) == 1:
            good[p::p] = b"\x00" * (((Bmax - p) // p) + 1)

    prefix = [0] * (Bmax + 1)
    s = 0
    for i in range(1, Bmax + 1):
        if good[i]:
            s += 1
        prefix[i] = s
    return prefix


def solve() -> int:
    Lmax = 5 * 10**11
    N = (Lmax * Lmax) // 3  # n <= N where L = sqrt(3n)

    # We need primes up to max r in the heaviest case p=7, q=13 in pattern (4,4,2).
    base_7_13 = (7**4) * (13**4)
    max_prime = isqrt(N // base_7_13)

    primes = _sieve_primes(max_prime)
    primes1 = [p for p in primes if (p % 3) == 1]  # primes ≡ 1 (mod 3)

    # Largest possible remaining factor comes from the smallest A in pattern (4,4,2):
    # A_min = 7^4 * 13^4 * 19^2
    A_min = (7**4) * (13**4) * (19**2)
    Bmax = isqrt(N // A_min)
    prefix_B = _build_prefix_B(Bmax, primes)

    def count_B(x: int) -> int:
        if x <= 0:
            return 0
        if x > Bmax:
            x = Bmax
        return prefix_B[x]

    # G(limit) = sum_{a>=0} count_B(floor(sqrt(limit/3^a)))
    G_cache: Dict[int, int] = {}

    def G(limit: int) -> int:
        got = G_cache.get(limit)
        if got is not None:
            return got
        m = limit
        total = 0
        while m:
            total += count_B(isqrt(m))
            m //= 3
        G_cache[limit] = total
        return total

    # Prime counting in an interval for primes ≡ 1 (mod 3)
    bL = bisect_left
    bR = bisect_right

    def count_primes1(lo: int, hi: int) -> int:
        if hi < lo:
            return 0
        return bR(primes1, hi) - bL(primes1, lo)

    def sum_over_r(C: int, excl1: int, excl2: int) -> int:
        """
        Sum_{r prime≡1 mod3, r<=sqrt(C), r!=excl1, r!=excl2}  G( C // r^2 )
        using quotient-grouping for floor(C/r^2).
        """
        Rmax = isqrt(C)
        if Rmax < 7:
            return 0
        r_low = 7
        total = 0
        while r_low <= Rmax:
            t = C // (r_low * r_low)
            if t == 0:
                break
            r_high = isqrt(C // t)
            if r_high > Rmax:
                r_high = Rmax
            cnt = count_primes1(r_low, r_high)
            if r_low <= excl1 <= r_high:
                cnt -= 1
            if excl2 != excl1 and r_low <= excl2 <= r_high:
                cnt -= 1
            if cnt > 0:
                total += cnt * G(t)
            r_low = r_high + 1
        return total

    ans = 0

    # R(n)=75 -> product (e_i+1) over primes≡1 mod3 equals 75.
    # Factorisations of 75 yield exponent patterns:
    #   25*3 -> (24,2)
    #   15*5 -> (14,4)
    #   5*5*3 -> (4,4,2)

    # Pattern (24,2): p^24 * q^2, with p,q primes≡1 mod3 and distinct.
    p = 7
    p24 = p**24
    qmax = isqrt(N // p24)
    q_end = bR(primes1, qmax)
    for q in primes1[:q_end]:
        if q == p:
            continue
        A = p24 * q * q
        ans += G(N // A)

    # Pattern (14,4): p^14 * q^4, ordered (swap gives different A), p!=q.
    for p in primes1:
        p14 = p**14
        if p14 > N:
            break
        max_q = _int_nth_root(N // p14, 4)
        q_end = bR(primes1, max_q)
        q4_cache: Dict[int, int] = {}
        for q in primes1[:q_end]:
            if q == p:
                continue
            q4 = q4_cache.get(q)
            if q4 is None:
                q4 = q**4
                q4_cache[q] = q4
            ans += G(N // (p14 * q4))

    # Pattern (4,4,2): p^4 * q^4 * r^2, with p<q, r distinct from both.
    # Since q>=p, we have p^8 * 7^2 <= N as a safe bound for p.
    p_max = _int_nth_root(N // 49, 8)
    p_candidates = [pp for pp in primes1 if pp <= p_max]

    for p in p_candidates:
        p4 = p**4
        rem = N // (p4 * 49)
        if rem == 0:
            break
        qmax = _int_nth_root(rem, 4)
        q_start = bR(primes1, p)  # enforce p < q
        q_end = bR(primes1, qmax)
        for q in primes1[q_start:q_end]:
            base = p4 * (q**4)
            C = N // base
            if C:
                ans += sum_over_r(C, p, q)

    return ans


def main() -> None:
    _self_test()
    print(solve())


if __name__ == "__main__":
    main()
