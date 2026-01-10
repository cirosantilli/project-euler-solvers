#!/usr/bin/env python3
"""
Project Euler 580: Squarefree Hilbert numbers

A Hilbert number is a positive integer congruent to 1 mod 4.
A Hilbert number n is "squarefree" if there is no Hilbert number h > 1 with h^2 | n.

This program computes C(10^16), with an assert for the sample given in the statement:
C(10^7) = 2327192
"""
from __future__ import annotations

import math


# ------------------------- small utilities -------------------------


def icbrt(n: int) -> int:
    """floor(cuberoot(n)) for n>=0."""
    if n <= 0:
        return 0
    x = int(round(n ** (1.0 / 3.0)))
    # Adjust around floating rounding errors
    while (x + 1) * (x + 1) * (x + 1) <= n:
        x += 1
    while x * x * x > n:
        x -= 1
    return x


def primes_upto(n: int) -> list[int]:
    """Simple sieve, returns all primes <= n."""
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    r = int(n**0.5)
    for p in range(2, r + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i in range(2, n + 1) if sieve[i]]


# ------------------------- Möbius + Mertens (Du Jiao sieve) -------------------------


def mobius_sieve(limit: int) -> list[int]:
    """Linear sieve for Möbius function mu[0..limit]."""
    mu = [0] * (limit + 1)
    mu[1] = 1
    primes: list[int] = []
    is_comp = bytearray(limit + 1)
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


class Mertens:
    """
    Computes M(n) = sum_{k<=n} mu(k) for large n using Du Jiao sieve,
    with precomputed mu prefix up to a fixed limit.
    """

    __slots__ = ("limit", "mu", "prefix", "cache", "cache_odd")

    def __init__(self, limit: int):
        self.limit = limit
        self.mu = mobius_sieve(limit)
        pref = [0] * (limit + 1)
        s = 0
        for i in range(1, limit + 1):
            s += self.mu[i]
            pref[i] = s
        self.prefix = pref
        self.cache: dict[int, int] = {}
        self.cache_odd: dict[int, int] = {}

    def M(self, n: int) -> int:
        """Mertens function M(n) = sum_{k<=n} mu(k)."""
        if n <= self.limit:
            return self.prefix[n]
        got = self.cache.get(n)
        if got is not None:
            return got
        res = 1
        l = 2
        # Group equal quotients
        while l <= n:
            q = n // l
            r = n // q
            res -= (r - l + 1) * self.M(q)
            l = r + 1
        self.cache[n] = res
        return res

    def Modd(self, n: int) -> int:
        """
        Sum of mu(k) over odd k<=n.
        Identity: sum_{k odd<=n} mu(k) = sum_{j>=0} M(floor(n/2^j)).
        """
        if n <= 0:
            return 0
        got = self.cache_odd.get(n)
        if got is not None:
            return got
        res = 0
        x = n
        while x:
            res += self.M(x)
            x //= 2
        self.cache_odd[n] = res
        return res


# ------------------------- counting squarefree numbers ≡ 1 (mod 4) -------------------------


def _C_mod4_prefix(q: int) -> int:
    """
    C(q) = sum_{m<=q} chi(m), where chi is the non-principal Dirichlet character mod 4:
      chi(m)=0 if m even, 1 if m≡1 mod4, -1 if m≡3 mod4.
    The partial sums are periodic:
      C(q)=1 if q mod 4 in {1,2} else 0
    """
    r = q & 3
    return 1 if (r == 1 or r == 2) else 0


def make_sq1_counter(n_max: int) -> tuple[callable, Mertens]:
    """
    Returns function SQ1(x): # { n<=x : n is squarefree and n≡1 (mod 4) }.

    Uses:
      - Möbius inversion for squarefree indicator
      - splitting the sum at D=floor(x^(1/3)) to make the computation O(x^(1/3))
      - Du Jiao sieve for fast Mertens queries.
    """
    # We need mu up to max(x^(1/3)) used in direct summation.
    mu_limit = max(300_000, icbrt(n_max) + 10)
    mert = Mertens(mu_limit)
    mu = mert.mu

    def SQ1(x: int) -> int:
        if x <= 0:
            return 0
        D = icbrt(x)
        sqrtx = math.isqrt(x)
        D = min(D, sqrtx)

        # O(x): odd squarefree count; T(x): odd squarefree weighted by chi (mod 4)
        O = 0
        T = 0

        # Direct sum over odd d <= D
        for d in range(1, D + 1, 2):
            md = mu[d]
            if md:
                q = x // (d * d)
                O += md * ((q + 1) // 2)  # odd m <= q
                T += md * _C_mod4_prefix(q)

        # Group the tail where q = floor(x / d^2) is small (<= x/(D+1)^2)
        qmax = x // ((D + 1) * (D + 1))
        for q in range(1, qmax + 1):
            r = math.isqrt(x // q)
            if r <= D:
                continue
            l = math.isqrt(x // (q + 1)) + 1
            if l <= D:
                l = D + 1
            if l > r:
                continue
            s = mert.Modd(r) - mert.Modd(l - 1)  # sum_{odd d in [l,r]} mu(d)
            if s:
                O += s * ((q + 1) // 2)
                T += s * _C_mod4_prefix(q)

        # For odd squarefree numbers, chi(n)=±1, so:
        # count(chi=+1) = (O + T)/2
        return (O + T) // 2

    return SQ1, mert


# ------------------------- small SQ1 prefix for fast lookup (x up to ~ N^(1/3)) -------------------------


def sq1_prefix_small(limit: int) -> list[int]:
    """
    Prefix table P where P[x] = # { n<=x : n is squarefree and n≡1 (mod 4) }.
    Works for small limit (here around N^(1/3)).
    """
    if limit <= 0:
        return [0]
    is_sqfree = bytearray(b"\x01") * (limit + 1)
    is_sqfree[0] = 0
    # Sieve out multiples of p^2
    for p in primes_upto(math.isqrt(limit)):
        sq = p * p
        is_sqfree[sq : limit + 1 : sq] = b"\x00" * (((limit - sq) // sq) + 1)

    pref = [0] * (limit + 1)
    c = 0
    for n in range(1, limit + 1):
        if is_sqfree[n] and (n & 3) == 1:
            c += 1
        pref[n] = c
    return pref


# ------------------------- segmented sieve sum over large primes -------------------------


def segmented_prime_sum(N: int, p_min: int, sq1_small: list[int]) -> int:
    """
    Returns:
      sum_{p prime, p>p_min, p<=sqrt(N), p≡3 (mod 4)} SQ1_small[ floor(N/p^2) ]
    where SQ1_small is a prefix table valid for all possible quotients.
    """
    limit = math.isqrt(N)
    base = primes_upto(math.isqrt(limit) + 1)  # primes up to 10000 for N=1e16

    low = max(p_min + 1, 3)
    if (low & 1) == 0:
        low += 1

    seg_odds = 1 << 20  # number of odd candidates per segment (~1e6 bytes)
    total = 0

    while low <= limit:
        high = min(limit + 1, low + 2 * seg_odds)  # [low, high)
        size = ((high - low) + 1) // 2  # number of odd numbers in the segment
        seg = bytearray(b"\x01") * size

        # cross out composites
        for p in base[1:]:  # skip p=2
            pp = p * p
            if pp >= high:
                break
            start = (low + p - 1) // p * p
            if start < pp:
                start = pp
            if (start & 1) == 0:
                start += p
            idx = (start - low) // 2
            step = p  # because we store only odds, increment of 2p -> index step p
            seg[idx::step] = b"\x00" * (((size - 1 - idx) // step) + 1)

        # scan primes and add contributions
        for i, flag in enumerate(seg):
            if flag:
                prime = low + 2 * i
                if (prime & 3) == 3 and prime > p_min:
                    q = N // (prime * prime)
                    total += sq1_small[q]

        low = high
        if (low & 1) == 0:
            low += 1

    return total


# ------------------------- main solve -------------------------


def solve(N: int) -> int:
    """
    C(N) = # squarefree Hilbert numbers <= N.
    Key identity:
      C(N) = SQ1(N) + sum_{p≡3 (mod 4), p^2<=N} SQ1( floor(N/p^2) )
    where SQ1(x) counts squarefree integers <=x with ≡1 (mod 4).
    """
    SQ1, _ = make_sq1_counter(N)

    V = icbrt(N)  # split point
    # For primes p>V, the quotient floor(N/p^2) is small (≈<=V), so use a prefix table.
    qmax = N // ((V + 1) * (V + 1))
    small_limit = max(V, qmax) + 8
    sq1_small = sq1_prefix_small(small_limit)

    # Sum for primes p <= V directly using SQ1 (large x)
    ans = SQ1(N)
    for p in primes_upto(V):
        if (p & 3) == 3:
            ans += SQ1(N // (p * p))

    # Remaining primes p>V via segmented sieve up to sqrt(N)
    ans += segmented_prime_sum(N, V, sq1_small)
    return ans


def main() -> None:
    # Problem statement check:
    assert solve(10**7) == 2327192

    print(solve(10**16))


if __name__ == "__main__":
    main()
