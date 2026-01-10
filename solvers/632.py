#!/usr/bin/env python3
"""
Project Euler 632: Square Prime Factors

Computes:
    P(N) = product of all non-zero C_k(N) (mod 1_000_000_007)
for N = 10^16, where C_k(N) counts integers 1..N with exactly k square prime factors.

No external libraries are used.
"""

from __future__ import annotations

import math
import bisect
import array
from functools import lru_cache

MOD = 1_000_000_007


def sieve_primes_upto(n: int) -> array.array:
    """Return array('I') of all primes <= n using an odd-only sieve."""
    if n < 2:
        return array.array("I")
    # Index i represents odd number (2*i + 1). Size counts odds <= n.
    size = (n + 1) // 2
    sieve = bytearray(b"\x01") * size
    sieve[0] = 0  # 1 is not prime

    limit = int(math.isqrt(n))
    # i corresponds to p = 2*i+1, so p <= limit <=> i <= limit//2
    for i in range(1, limit // 2 + 1):
        if sieve[i]:
            p = 2 * i + 1
            start = (p * p) // 2
            sieve[start::p] = b"\x00" * (((size - start - 1) // p) + 1)

    primes = array.array("I", [2])
    ap = primes.append
    for i in range(1, size):
        if sieve[i]:
            ap(2 * i + 1)
    return primes


def linear_sieve_mu_omega(n: int) -> tuple[array.array, bytearray]:
    """
    Linear sieve up to n producing:
      - mu: Möbius function values as array('b')
      - omega: number of distinct prime factors as bytearray
    """
    mu = array.array("b", [0]) * (n + 1)
    omega = bytearray(n + 1)
    is_comp = bytearray(n + 1)
    primes: list[int] = []

    mu[1] = 1
    for i in range(2, n + 1):
        if not is_comp[i]:
            primes.append(i)
            mu[i] = -1
            omega[i] = 1
        for p in primes:
            ip = i * p
            if ip > n:
                break
            is_comp[ip] = 1
            if i % p == 0:
                mu[ip] = 0
                omega[ip] = omega[i]
                break
            else:
                mu[ip] = -mu[i]
                omega[ip] = omega[i] + 1
    return mu, omega


def kth_root_floor(n: int, k: int) -> int:
    """Floor of the integer k-th root of n (k>=2)."""
    if k == 2:
        return math.isqrt(n)
    # Small n in this problem, but do an exact integer binary search.
    x = int(n ** (1.0 / k)) + 2
    lo, hi = 1, x
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid**k <= n:
            lo = mid
        else:
            hi = mid
    return lo


def comb_table(kmax: int) -> list[list[int]]:
    """Binomial coefficients up to kmax."""
    c = [[0] * (kmax + 1) for _ in range(kmax + 1)]
    for n in range(kmax + 1):
        c[n][0] = c[n][n] = 1
        for r in range(1, n):
            c[n][r] = c[n - 1][r - 1] + c[n - 1][r]
    return c


def max_possible_k(sqrt_n: int, primes_small: list[int]) -> int:
    """Maximum k such that product of first k primes <= sqrt_n."""
    prod = 1
    k = 0
    for p in primes_small:
        if prod * p <= sqrt_n:
            prod *= p
            k += 1
        else:
            break
    return k


def counts_Ck(
    N: int, primes_full: array.array | None = None, L0_cap: int = 5_000_000
) -> list[int]:
    """
    Return list [C_0(N), C_1(N), ..., C_kmax(N)].

    Strategy:
      1) Compute S_r(N) = sum_{squarefree d, omega(d)=r} floor(N / d^2),
         which equals sum_{n<=N} binom(f(n), r) where f(n)=#square prime factors.
      2) Recover C_k by binomial inversion on S_r.
      3) To compute S_r for large N, split d into:
         - d <= L0: enumerate with a linear Möbius/omega sieve
         - d >  L0: group by q = floor(N/d^2) which is small when d is large,
                   and use a recursive counter of squarefree numbers with r prime factors.
    """
    if N < 1:
        return []

    sqrtN = int(math.isqrt(N))

    # Prime list for pi(x) queries up to sqrtN.
    if primes_full is None or (len(primes_full) == 0 or primes_full[-1] < sqrtN):
        primes_full = sieve_primes_upto(sqrtN)

    # Small primes used for the combinatorial recursion (only need up to 10000 here).
    primes_small = []
    for p in primes_full:
        if p <= 10_000:
            primes_small.append(int(p))
        else:
            break

    kmax = max_possible_k(sqrtN, primes_small)
    comb = comb_table(kmax)

    # Enumerate small d up to L0.
    L0 = min(sqrtN, L0_cap)
    mu, omega = linear_sieve_mu_omega(L0)

    S = [0] * (kmax + 1)
    for d in range(1, L0 + 1):
        if mu[d] != 0:  # squarefree
            r = omega[d]
            if r <= kmax:
                S[r] += N // (d * d)

    # If we fully covered d <= sqrtN, we're done.
    if L0 == sqrtN:
        C = [0] * (kmax + 1)
        for k in range(kmax, -1, -1):
            val = S[k]
            for j in range(k + 1, kmax + 1):
                val -= C[j] * comb[j][k]
            C[k] = val
        return C

    # Prime counting pi(x) via binary search on the full prime list.
    def pi(x: int) -> int:
        return bisect.bisect_right(primes_full, x)

    @lru_cache(maxsize=None)
    def count_squarefree_products(x: int, k: int, start: int) -> int:
        """
        Count of numbers <= x that are products of exactly k distinct primes,
        with all primes chosen from primes_small[start:], strictly increasing.
        """
        if k == 0:
            return 1
        if k == 1:
            return pi(x) - start

        limit = kth_root_floor(x, k)
        end = bisect.bisect_right(primes_small, limit)

        res = 0
        for i in range(start, end):
            p = primes_small[i]
            res += count_squarefree_products(x // p, k - 1, i + 1)
        return res

    def prefix_count(x: int, r: int) -> int:
        """#squarefree d <= x with omega(d)=r."""
        if r == 0:
            return 1 if x >= 1 else 0
        return count_squarefree_products(x, r, 0)

    # For d > L0, q = floor(N/d^2) <= N/(L0+1)^2 is small.
    qmax = N // ((L0 + 1) * (L0 + 1))
    for q in range(1, qmax + 1):
        hi = int(math.isqrt(N // q))
        lo = int(math.isqrt(N // (q + 1)))
        a = max(lo, L0)  # we'll count d in (a, hi]
        if hi <= a:
            continue
        for r in range(kmax + 1):
            cnt = prefix_count(hi, r) - prefix_count(a, r)
            if cnt:
                S[r] += q * cnt

    # Binomial inversion to get C_k from S_r.
    C = [0] * (kmax + 1)
    for k in range(kmax, -1, -1):
        val = S[k]
        for j in range(k + 1, kmax + 1):
            val -= C[j] * comb[j][k]
        C[k] = val
    return C


def product_of_nonzero(values: list[int], mod: int = MOD) -> int:
    ans = 1
    for v in values:
        if v:
            ans = (ans * (v % mod)) % mod
    return ans


def _run_statement_asserts() -> None:
    # Values from the problem statement table:
    table = {
        10: [7, 3, 0, 0, 0, 0],
        10**2: [61, 36, 3, 0, 0, 0],
        10**3: [608, 343, 48, 1, 0, 0],
        10**4: [6083, 3363, 533, 21, 0, 0],
        10**5: [60794, 33562, 5345, 297, 2, 0],
        10**6: [607926, 335438, 53358, 3218, 60, 0],
        10**7: [6079291, 3353956, 533140, 32777, 834, 2],
        10**8: [60792694, 33539196, 5329747, 329028, 9257, 78],
    }
    for N, expected in table.items():
        got = counts_Ck(N)
        # Pad to C_0..C_5 for comparison
        got_pad = got + [0] * (6 - len(got))
        got_pad = got_pad[:6]
        assert got_pad == expected, (N, got_pad, expected)


def main() -> None:
    _run_statement_asserts()

    N = 10**16
    primes = sieve_primes_upto(int(math.isqrt(N)))  # primes up to 1e8
    C = counts_Ck(N, primes_full=primes)
    print(product_of_nonzero(C, MOD))


if __name__ == "__main__":
    main()
