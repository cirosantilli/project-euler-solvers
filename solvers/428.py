#!/usr/bin/env python3
"""
Project Euler 428 solver (pure Python, no external libraries).

The core approach:
- Use Steiner necklace criterion to reduce to multiplicative counting functions.
- Express total T(n) via two summatory functions over m coprime to 6:
    F(x) = sum_{m<=x, (m,6)=1} tau(m^2)
    G(x) = sum_{m<=x, (m,6)=1} chi(m) * S(m^2)
  where chi is the non-trivial Dirichlet character mod 3, and
  S(m^2) = sum_{d|m^2} chi(d).
- Compute these sums using a Min_25-like block sieve for pi(x) and sum chi(p),
  and a recursion over primes (with memoization) for the multiplicative function.

This avoids brute force up to 1e9.
"""

import math
from functools import lru_cache


def chi_mod3(n: int) -> int:
    """Dirichlet character modulo 3: chi(0)=0, chi(1)=1, chi(2)=-1."""
    r = n % 3
    if r == 0:
        return 0
    return 1 if r == 1 else -1


def chi_prefix_integers(x: int) -> int:
    """
    Sum_{1<=k<=x} chi(k).
    chi is periodic with period 3: [1, -1, 0].
    """
    # count of 1 mod 3 minus count of 2 mod 3
    return (x + 2) // 3 - (x + 1) // 3


def primes_up_to(limit: int):
    """Simple sieve of Eratosthenes up to limit (inclusive)."""
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    r = int(limit**0.5)
    for i in range(2, r + 1):
        if sieve[i]:
            step = i
            start = i * i
            sieve[start : limit + 1 : step] = b"\x00" * (((limit - start) // step) + 1)
    return [i for i in range(limit + 1) if sieve[i]]


class PrimeTables:
    """
    Precompute, for a fixed N:
      - pi(x) for x in the Min_25 "block values"
      - sum_{p<=x} chi(p) for x in the same set

    This supports O(1) query for any x of form floor(N / k).
    """

    __slots__ = ("N", "V", "vals", "id1", "id2", "pi_tbl", "chi_tbl", "primes")

    def __init__(self, N: int):
        self.N = N
        self.V = int(math.isqrt(N))

        # Build block values: distinct floor(N / i)
        vals = []
        i = 1
        while i <= N:
            v = N // i
            vals.append(v)
            i = N // v + 1
        self.vals = vals

        m = len(vals)
        V = self.V
        id1 = [0] * (V + 1)
        id2 = [0] * (V + 1)
        for idx, v in enumerate(vals):
            if v <= V:
                id1[v] = idx
            else:
                id2[N // v] = idx
        self.id1 = id1
        self.id2 = id2

        # initial g arrays (like Legendre sieve):
        # pi_tbl starts as count of integers in [2..v] = v-1
        pi_tbl = [v - 1 for v in vals]
        # chi_tbl starts as sum_{k=2..v} chi(k) = chi_prefix(v) - chi(1)
        chi_tbl = [chi_prefix_integers(v) - 1 for v in vals]

        primes = primes_up_to(V)
        self.primes = primes

        # prefix sums of chi(p) over primes <= V
        chi_prime_pref = [0]
        s = 0
        for p in primes:
            s += chi_mod3(p)
            chi_prime_pref.append(s)

        # sieve updates for pi_tbl and chi_tbl
        # total complexity ~ O(N^(2/3)) and is fast for N=1e9
        for pi_idx, p in enumerate(primes, start=1):
            p2 = p * p
            if p2 > N:
                break
            pi_before = pi_idx - 1
            chi_before = chi_prime_pref[pi_idx - 1]
            cp = chi_mod3(p)

            # update all v >= p^2
            for idx, v in enumerate(vals):
                if v < p2:
                    break
                t = v // p
                j = self.idx_of(t)
                pi_tbl[idx] -= pi_tbl[j] - pi_before
                chi_tbl[idx] -= cp * (chi_tbl[j] - chi_before)

        self.pi_tbl = pi_tbl
        self.chi_tbl = chi_tbl

    def idx_of(self, x: int) -> int:
        """Index lookup for x in block values."""
        if x <= self.V:
            return self.id1[x]
        return self.id2[self.N // x]

    def pi(self, x: int) -> int:
        """pi(x) for x in block values."""
        return self.pi_tbl[self.idx_of(x)]

    def chi_prime_sum(self, x: int) -> int:
        """Sum_{p<=x} chi(p) for x in block values."""
        return self.chi_tbl[self.idx_of(x)]


class Summatory:
    """
    Compute:
      F(x) = sum_{m<=x, (m,6)=1} tau(m^2)
      G(x) = sum_{m<=x, (m,6)=1} chi(m) * S(m^2)
    using Min_25-style recursion with prime-block pi/chi tables.

    These are used to build T(n).
    """

    def __init__(self, N: int):
        self.N = N
        self.pt = PrimeTables(N)

        # primes used in recursion: primes >= 5 (since p=2,3 contribute 0)
        self.rec_primes = [p for p in self.pt.primes if p >= 5]

    def prime_sum_F(self, x: int) -> int:
        """
        Sum_{p<=x} f(p) for F-function:
          f(p)=0 for p=2,3
          f(p)=3 for p>=5
        """
        pi = self.pt.pi(x)
        c23 = (1 if x >= 2 else 0) + (1 if x >= 3 else 0)
        return 3 * (pi - c23)

    def prime_sum_G(self, x: int) -> int:
        """
        Sum_{p<=x} g(p) for G-function:
          g(2)=g(3)=0
          g(p)=3 if p≡1 (mod 3)
          g(p)=-1 if p≡2 (mod 3) and p>2
        Which equals: count(primes>=5) + 2*sum_{p>=5} chi(p)
        """
        pi = self.pt.pi(x)
        c23 = (1 if x >= 2 else 0) + (1 if x >= 3 else 0)
        chi_p = self.pt.chi_prime_sum(x)
        # remove chi(2)=-1 if x>=2, chi(3)=0 always
        chi_excl = chi_p + (1 if x >= 2 else 0)
        return (pi - c23) + 2 * chi_excl

    @staticmethod
    def val_F_prime_power(p: int, e: int) -> int:
        # for p>=5: tau(p^(2e)) = 2e+1
        return 2 * e + 1

    @staticmethod
    def val_G_prime_power(p: int, e: int) -> int:
        # p>=5
        if p % 3 == 1:
            return 2 * e + 1
        # p % 3 == 2
        return -1 if (e & 1) else 1

    def make_H(self, prime_sum_func, val_prime_power):
        primes = self.rec_primes

        @lru_cache(maxsize=None)
        def H(n: int, idx: int) -> int:
            """
            H(n, idx) = sum_{2<=m<=n, all prime factors >= primes[idx]} f(m)
            (excluding m=1)
            """
            prev = primes[idx - 1] if idx > 0 else 1

            # If smallest allowed prime squared exceeds n -> only primes remain
            if idx >= len(primes) or primes[idx] * primes[idx] > n:
                return prime_sum_func(n) - prime_sum_func(prev)

            res = prime_sum_func(n) - prime_sum_func(prev)

            # enumerate smallest prime factor p = primes[k]
            for k in range(idx, len(primes)):
                p = primes[k]
                if p * p > n:
                    break
                pe = p
                e = 1
                # add terms for exponents where p^(e+1) <= n
                while pe * p <= n:
                    res += val_prime_power(p, e) * H(n // pe, k + 1)
                    res += val_prime_power(p, e + 1)
                    pe *= p
                    e += 1
            return res

        return H

    def sum_F(self, x: int) -> int:
        """F(x) includes m=1 term."""
        if x <= 0:
            return 0
        if not hasattr(self, "_H_F"):
            self._H_F = self.make_H(self.prime_sum_F, self.val_F_prime_power)
        return 1 + self._H_F(x, 0)

    def sum_G(self, x: int) -> int:
        """G(x) includes m=1 term (chi(1)*S(1)=1)."""
        if x <= 0:
            return 0
        if not hasattr(self, "_H_G"):
            self._H_G = self.make_H(self.prime_sum_G, self.val_G_prime_power)
        return 1 + self._H_G(x, 0)


def T(n: int) -> int:
    """
    Compute T(n) = number of necklace triplets (a,b,c) with 1<=b<=n.

    Uses decomposition b = 2^i 3^j m with (m,6)=1 and precomputed F,G.
    """
    S = Summatory(n)
    F_cache = {}
    G_cache = {}

    def F(x):
        if x not in F_cache:
            F_cache[x] = S.sum_F(x)
        return F_cache[x]

    def G(x):
        if x not in G_cache:
            G_cache[x] = S.sum_G(x)
        return G_cache[x]

    total = 0

    # main double sum over i,j for tau(2b^2) and tau(12b^2) and j>=1 part of +1/2 case
    pow2 = 1
    i = 0
    while pow2 <= n:
        pow3 = 1
        j = 0
        while pow2 * pow3 <= n:
            x = n // (pow2 * pow3)
            Fx = F(x)

            # τ(2b²) = (2i+2)(2j+1) τ(m²)
            total += (2 * i + 2) * (2 * j + 1) * Fx

            # τ(12b²) = (2i+3)(2j+2) τ(m²)
            total += (2 * i + 3) * (2 * j + 2) * Fx

            # +1/2 case for j>=1:
            # count = (2j-1)(2i+3) τ(m²)
            if j >= 1:
                total += (2 * j - 1) * (2 * i + 3) * Fx

            pow3 *= 3
            j += 1
        pow2 *= 2
        i += 1

    # +1/2 case for j=0:
    # sum over i: ((2i+3)*F(x) - (-1)^i * G(x)) / 2
    pow2 = 1
    i = 0
    while pow2 <= n:
        x = n // pow2
        sign = 1 if (i % 2 == 0) else -1
        total += ((2 * i + 3) * F(x) - sign * G(x)) // 2
        pow2 *= 2
        i += 1

    return total


def main():
    # test values from the problem statement
    assert T(1) == 9
    assert T(20) == 732
    assert T(3000) == 438106

    # target
    print(T(10**9))


if __name__ == "__main__":
    main()
