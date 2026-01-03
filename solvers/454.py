#!/usr/bin/env python3
"""
Project Euler 454: Diophantine reciprocals III

Count solutions (x, y, n) in positive integers of:
    1/x + 1/y = 1/n
subject to:
    x < y <= L

We compute F(L) and print F(10^12).

No external libraries are used.
"""

import math
import sys


def build_spf(limit: int) -> list[int]:
    """Smallest prime factor sieve (linear time)."""
    spf = [0] * (limit + 1)
    primes: list[int] = []
    if limit >= 1:
        spf[1] = 1
    for i in range(2, limit + 1):
        if spf[i] == 0:
            spf[i] = i
            primes.append(i)
        for p in primes:
            v = i * p
            if v > limit:
                break
            spf[v] = p
            if p == spf[i]:
                break
    return spf


def sum_floor_segment(x: int, lo: int, hi: int) -> int:
    """
    Compute sum_{i=lo+1..hi} floor(x / i) in O(#distinct quotients) time
    using quotient grouping.
    """
    if hi <= lo or x <= 0:
        return 0

    res = 0
    i = lo + 1
    while i <= hi:
        q = x // i
        if q == 0:
            break
        j = x // q  # largest index with the same quotient q
        if j > hi:
            j = hi
        res += q * (j - i + 1)
        i = j + 1
    return res


def F(L: int) -> int:
    """
    Compute F(L) for the problem.
    """
    B = math.isqrt(L)
    spf = build_spf(B)

    total = 0
    sum_floor = sum_floor_segment  # local binding for speed

    for n in range(2, B + 1):
        # Factor n into DISTINCT prime factors using spf.
        tmp = n
        primes = []
        last = 0
        while tmp > 1:
            p = spf[tmp]
            tmp //= p
            if p != last:
                primes.append(p)
                last = p

        # Enumerate all squarefree divisors d of n with their Möbius value mu(d).
        # For squarefree d, mu(d) = (-1)^(#primes in d).
        divs = [1]
        mus = [1]
        for p in primes:
            m = len(divs)
            for i in range(m):
                divs.append(divs[i] * p)
                mus.append(-mus[i])

        Ln = L // n  # used as x = (L//n)//d

        # Contribution:
        # For each squarefree d|n:
        #   k = n/d
        #   x = floor(L/(n*d)) = (L//n)//d
        #   add mu(d) * sum_{i=k+1..2k-1} floor(x/i)
        # derived via Möbius inversion and a divisor-sum compression.
        for idx in range(len(divs)):
            d = divs[idx]
            mu = mus[idx]

            k = n // d
            if k <= 1:
                continue

            x = Ln // d
            if x == 0:
                continue

            total += mu * sum_floor(x, k, 2 * k - 1)

    return total


def main() -> None:
    # Test values from the problem statement.
    assert F(15) == 4
    assert F(1000) == 1069

    L = 10**12
    if len(sys.argv) >= 2:
        L = int(sys.argv[1])

    print(F(L))


if __name__ == "__main__":
    main()
