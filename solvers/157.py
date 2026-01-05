#!/usr/bin/env python3
"""
Project Euler 157: Base-10 Diophantine Reciprocal.

Count solutions (a,b,p) in positive integers with a <= b to:
    1/a + 1/b = p / 10^n
for n = 1..9, and output the total number of solutions.

Key transformation:
Let N = 10^n.
We need p = N*(a+b)/(ab) to be an integer, i.e.:
    ab | N*(a+b)

Write a = g*x, b = g*y with gcd(x,y)=1.
Then:
    g*x*y | N*(x+y)

Because gcd(xy, x+y) = 1 when gcd(x,y)=1, we must have xy | N.
Let N = xy*m. Then the condition becomes:
    g | m*(x+y)

So for each coprime pair (x,y) with x<=y and xy|N, the number of valid g is:
    d(m*(x+y))  (number of positive divisors)

We sum this over all valid (x,y).
"""

from __future__ import annotations

from functools import lru_cache
from math import gcd, isqrt
from typing import Dict, List


def sieve_primes(limit: int) -> List[int]:
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, isqrt(limit) + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start : limit + 1 : step] = b"\x00" * (((limit - start) // step) + 1)
    return [i for i, v in enumerate(sieve) if v]


PRIMES = sieve_primes(
    50000
)  # enough for factoring numbers up to ~2e9 after removing 2s/5s


@lru_cache(maxsize=None)
def factorize_oddish(n: int) -> Dict[int, int]:
    """Factorize n after 2 and 5 have been removed (so it's small-ish)."""
    res: Dict[int, int] = {}
    x = n
    for p in PRIMES:
        if p * p > x:
            break
        if x % p == 0:
            e = 0
            while x % p == 0:
                x //= p
                e += 1
            res[p] = e
    if x > 1:
        res[x] = 1
    return res


def divisor_count_for_m_times_s(m: int, s: int) -> int:
    """
    Compute d(m*s) where m is of the form 2^a*5^b and s is up to about 2*10^9.
    Factorization of s' = s with 2s and 5s removed is cached.
    """
    a2 = 0
    a5 = 0

    # Extract 2s and 5s from m
    mm = m
    while mm % 2 == 0:
        mm //= 2
        a2 += 1
    while mm % 5 == 0:
        mm //= 5
        a5 += 1
    assert mm == 1

    # Extract 2s and 5s from s
    ss = s
    while ss % 2 == 0:
        ss //= 2
        a2 += 1
    while ss % 5 == 0:
        ss //= 5
        a5 += 1

    # Now ss is not divisible by 2 or 5
    factors = factorize_oddish(ss)

    # Compute divisor count
    d = (a2 + 1) * (a5 + 1)
    for e in factors.values():
        d *= e + 1
    return d


def count_solutions_for_n(n: int) -> int:
    N = 10**n

    # Divisors of 10^n are 2^i * 5^j.
    divs = [2**i * 5**j for i in range(n + 1) for j in range(n + 1)]
    divs = sorted(set(divs))

    total = 0
    for i, x in enumerate(divs):
        for y in divs[i:]:
            if gcd(x, y) != 1:
                continue
            xy = x * y
            if xy > N:
                continue
            m = N // xy
            total += divisor_count_for_m_times_s(m, x + y)
    return total


def solve() -> int:
    return sum(count_solutions_for_n(n) for n in range(1, 10))


def _asserts_from_statement() -> None:
    # Statement test: for n = 1 there are 20 solutions.
    assert count_solutions_for_n(1) == 20


if __name__ == "__main__":
    _asserts_from_statement()
    ans = solve()
    print(ans)
