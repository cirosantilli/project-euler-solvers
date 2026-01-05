#!/usr/bin/env python3
"""
Project Euler 342 - The Totient of a Square Is a Cube

Find the sum of all integers n, 1 < n < 10^10, such that phi(n^2) is a perfect cube.

No external libraries are used.
"""

from __future__ import annotations

import math


LIMIT_N = 10**10


def iroot3_floor(n: int) -> int:
    """Return floor(cuberoot(n)) for n >= 0 using integer arithmetic."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n < 8:
        return 1 if n >= 1 else 0

    hi = 1
    while hi * hi * hi <= n:
        hi <<= 1
    lo = hi >> 1

    while lo + 1 < hi:
        mid = (lo + hi) >> 1
        m3 = mid * mid * mid
        if m3 <= n:
            lo = mid
        else:
            hi = mid
    return lo


def build_spf(limit: int) -> list[int]:
    """
    Build an array 'spf' where spf[x] is the smallest prime factor of x (spf[0]=spf[1]=0).
    Linear sieve, O(limit).
    """
    spf = [0] * (limit + 1)
    primes: list[int] = []
    for i in range(2, limit + 1):
        if spf[i] == 0:
            spf[i] = i
            primes.append(i)
        si = spf[i]
        for p in primes:
            ip = i * p
            if ip > limit:
                break
            spf[ip] = p
            if p == si:
                break
    return spf


def phi(n: int) -> int:
    """Euler's totient function via trial division (used only for the statement assert)."""
    if n <= 0:
        raise ValueError("n must be positive")
    result = n
    x = n
    p = 2
    while p * p <= x:
        if x % p == 0:
            while x % p == 0:
                x //= p
            result -= result // p
        p = 3 if p == 2 else p + 2
    if x > 1:
        result -= result // x
    return result


def is_perfect_cube(x: int) -> bool:
    """Return True iff x is a perfect cube (x >= 0)."""
    if x < 0:
        return False
    r = int(round(x ** (1.0 / 3.0)))
    while (r + 1) ** 3 <= x:
        r += 1
    while r**3 > x:
        r -= 1
    return r**3 == x


def solve(limit_n: int = LIMIT_N) -> int:
    """
    Main solver.

    Write phi(n^2) = i^3. Then every prime dividing phi(n^2) divides i, hence <= i.
    Since n^2 < limit_n^2, we have i^3 < limit_n^2, so i <= floor(cuberoot(limit_n^2 - 1)).

    For fixed i, let P be the set of distinct primes dividing n. Using:
        phi(n^2) = n^2 * Π_{p in P} (p-1)/p
    we get:
        n^2 = i^3 * Π_{p in P} p/(p-1)

    Also p|n => p|phi(n^2) => p|i, so P is a subset of the distinct prime factors of i.
    We enumerate all such subsets and test whether the resulting n^2 is a perfect square with
    prime set exactly P.
    """
    limit_n2 = limit_n * limit_n
    max_i = iroot3_floor(limit_n2 - 1)

    spf = build_spf(max_i)

    gcd = math.gcd
    isqrt = math.isqrt

    total = 0

    for i in range(2, max_i + 1):
        # Distinct prime factors of i via SPF
        x = i
        primes: list[int] = []
        while x > 1:
            p = spf[x]
            primes.append(p)
            while x % p == 0:
                x //= p

        k = len(primes)
        if k == 0:
            continue

        base = i * i * i  # i^3

        # Precompute subset products
        size = 1 << k
        prodp = [1] * size  # Π p
        prodd = [1] * size  # Π (p-1)
        for mask in range(1, size):
            lsb = mask & -mask
            j = lsb.bit_length() - 1
            prev = mask ^ lsb
            p = primes[j]
            prodp[mask] = prodp[prev] * p
            prodd[mask] = prodd[prev] * (p - 1)

        for mask in range(1, size):
            numer = base
            denom = prodd[mask]

            g = gcd(numer, denom)
            numer //= g
            denom //= g

            mult = prodp[mask]
            g = gcd(mult, denom)
            mult //= g
            denom //= g

            if denom != 1:
                continue

            n2 = numer * mult
            if n2 >= limit_n2:
                continue

            n = isqrt(n2)
            if n <= 1 or n * n != n2:
                continue

            # Verify the prime set is exactly the subset
            tmp = n
            ok = True
            for j, p in enumerate(primes):
                if (mask >> j) & 1:
                    if tmp % p != 0:
                        ok = False
                        break
                    while tmp % p == 0:
                        tmp //= p
            if ok and tmp == 1:
                total += n

    return total


def main() -> None:
    # Test value from the problem statement:
    # n = 50 => phi(50^2) = phi(2500) = 2^3 * 5^3 = 1000, which is a cube.
    assert is_perfect_cube(phi(50 * 50))

    print(solve())


if __name__ == "__main__":
    main()
