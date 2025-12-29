#!/usr/bin/env python3
"""Project Euler 272: Modular Cubes, Part 2

Find the sum of all positive integers n <= 10^11 such that

  C(n) = #{ x : 1 < x < n and x^3 ≡ 1 (mod n) } = 242.

Equivalently, the total number of solutions to x^3 ≡ 1 (mod n), including x=1,
is 243 = 3^5.
"""

from __future__ import annotations

import math
from typing import List, Tuple


N = 10**11


def sieve_primes(limit: int) -> List[int]:
    """Return all primes <= limit (simple bytearray sieve)."""
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    # remove evens
    if limit >= 4:
        sieve[4 : limit + 1 : 2] = b"\x00" * (((limit - 4) // 2) + 1)
    r = int(math.isqrt(limit))
    for p in range(3, r + 1, 2):
        if sieve[p]:
            step = p * 2
            start = p * p
            sieve[start : limit + 1 : step] = b"\x00" * (((limit - start) // step) + 1)
    primes = [2]
    primes.extend(i for i in range(3, limit + 1, 2) if sieve[i])
    return primes


def brute_C(n: int) -> int:
    """Brute-force C(n) for small n (for asserts / sanity checks)."""
    cnt = 0
    for x in range(2, n):
        if pow(x, 3, n) == 1:
            cnt += 1
    return cnt


def inert_prefix_sums(limit: int) -> Tuple[List[int], List[int]]:
    """Prefix sums for the 'inert' factor b.

    Any prime power p^a contributes 3 cube-roots of 1 iff:
      - p ≡ 1 (mod 3), any a>=1, or
      - p = 3 and a>=2.
    All other primes are inert (contribute only the trivial root).

    In the final decomposition n = (good-part) * b:
      - b must NOT contain any prime p ≡ 1 (mod 3)
      - b must NOT be divisible by 9 (else it would contribute p=3 as a good prime)
      - for the 'no-3' variant, b must also not be divisible by 3.

    Returns:
      pref_allow3[t] = sum of all b<=t allowed to include a single factor 3 (not 9)
      pref_no3[t]    = sum of all b<=t with the same restriction and additionally 3∤b
    """
    primes = sieve_primes(limit)
    allow3 = bytearray(b"\x01") * (limit + 1)
    allow3[0] = 0

    # forbid 3^2
    if limit >= 9:
        allow3[9 : limit + 1 : 9] = b"\x00" * (((limit - 9) // 9) + 1)

    # forbid primes p ≡ 1 (mod 3)
    for p in primes:
        if p % 3 == 1:
            allow3[p : limit + 1 : p] = b"\x00" * (((limit - p) // p) + 1)

    no3 = allow3[:]  # copy
    if limit >= 3:
        no3[3 : limit + 1 : 3] = b"\x00" * (((limit - 3) // 3) + 1)

    pref_allow3 = [0] * (limit + 1)
    pref_no3 = [0] * (limit + 1)
    s1 = 0
    s2 = 0
    for i in range(1, limit + 1):
        if allow3[i]:
            s1 += i
        if no3[i]:
            s2 += i
        pref_allow3[i] = s1
        pref_no3[i] = s2
    return pref_allow3, pref_no3


def solve() -> int:
    """Compute the required sum for n <= 10^11 with C(n)=242."""

    # Largest possible good prime happens in the factorization
    #   n = 3^2 * 7 * 13 * 19 * p
    # so p <= N / (9*7*13*19).
    max_good_prime = N // (9 * 7 * 13 * 19)
    primes_all = sieve_primes(max_good_prime)
    primes_mod1 = [p for p in primes_all if p % 3 == 1]  # all good primes except 3

    # With 5 good primes, the smallest good-part is 3^2 * 7 * 13 * 19 * 31.
    min_good_part = 9 * 7 * 13 * 19 * 31
    b_limit_max = N // min_good_part
    pref_allow3, pref_no3 = inert_prefix_sums(b_limit_max)

    primes = primes_mod1
    L = len(primes)

    # Precompute minimal products for pruning: min_prod[k][i] is the product of the
    # k smallest primes in primes[i:], capped at N+1.
    min_prod = [[1] * (L + 1) for _ in range(6)]  # up to 5
    for k in range(1, 6):
        min_prod[k][L] = N + 1
    for i in range(L - 1, -1, -1):
        min_prod[0][i] = 1
        pi = primes[i]
        for k in range(1, 6):
            v = pi * min_prod[k - 1][i + 1]
            min_prod[k][i] = (N + 1) if v > N else v

    def sum_pick(rem: int, pref: List[int], initial_prod: int = 1) -> int:
        """Sum over products of `rem` distinct primes (each to any exponent >=1)
        from `primes`, multiplied by `initial_prod`.

        Each generated good-part g contributes:
            g * sum_{b<=N/g, b inert} b
        where the inert sum is provided as a prefix array `pref`.
        """

        total = 0
        primes_loc = primes
        min_prod_loc = min_prod
        pref_loc = pref
        Nl = N
        Lloc = L

        def dfs(start: int, remaining: int, prod: int) -> None:
            nonlocal total
            if remaining == 1:
                max_n = Nl // prod
                for j in range(start, Lloc):
                    pj = primes_loc[j]
                    if pj > max_n:
                        break
                    powv = pj
                    while powv <= max_n:
                        n0 = prod * powv
                        total += n0 * pref_loc[Nl // n0]
                        powv *= pj
                return

            last = Lloc - remaining
            for j in range(start, last + 1):
                pj = primes_loc[j]
                if prod * pj * min_prod_loc[remaining - 1][j + 1] > Nl:
                    break
                max_pow = Nl // (prod * min_prod_loc[remaining - 1][j + 1])
                powv = pj
                while powv <= max_pow:
                    dfs(j + 1, remaining - 1, prod * powv)
                    powv *= pj

        dfs(0, rem, initial_prod)
        return total

    # Case B: 3 is NOT a good prime factor => we need 5 primes p≡1 (mod 3).
    total = sum_pick(5, pref_allow3)

    # Case A: 3 IS a good prime factor => include 3^e (e>=2), pick 4 primes p≡1 (mod 3).
    p3 = 9
    while p3 * min_prod[4][0] <= N:
        total += sum_pick(4, pref_no3, initial_prod=p3)
        p3 *= 3

    return total


def main() -> None:
    # Assert from the problem statement.
    assert brute_C(91) == 8

    print(solve())


if __name__ == "__main__":
    main()
