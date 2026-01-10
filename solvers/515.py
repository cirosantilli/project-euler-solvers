#!/usr/bin/env python3
"""
Project Euler 515 - Dissonant Numbers

Let d(p,n,0) be the multiplicative inverse of n modulo prime p.
Let d(p,n,k) = sum_{i=1..n} d(p,i,k-1) for k >= 1.
Let D(a,b,k) = sum( d(p,p-1,k) mod p ) for primes a <= p < a+b.

Key fact (proved in README):
For any prime p and any integer k with 2 <= k < p,
    d(p, p-1, k) ≡ (k-1)^(-1) (mod p).

Therefore the whole problem reduces to:
    D(a,b,k) = sum_{primes p in [a,a+b)} inv_mod(k-1, p).

No external libraries are used.
"""

import math


def sieve_primes(limit: int) -> list[int]:
    """Return all primes <= limit using a simple sieve."""
    if limit < 2:
        return []
    is_prime = bytearray(b"\x01") * (limit + 1)
    is_prime[0:2] = b"\x00\x00"
    r = int(math.isqrt(limit))
    for i in range(2, r + 1):
        if is_prime[i]:
            start = i * i
            step = i
            is_prime[start : limit + 1 : step] = b"\x00" * (
                ((limit - start) // step) + 1
            )
    return [i for i in range(2, limit + 1) if is_prime[i]]


def primes_in_range(start: int, length: int) -> list[int]:
    """
    Segmented sieve: return primes p in [start, start+length).
    Works well when 'length' is modest (<= a few million).
    """
    if length <= 0:
        return []
    low = start
    high = start + length

    seg = bytearray(b"\x01") * length

    # Handle small numbers explicitly if the segment overlaps them.
    if low <= 1:
        for x in range(low, min(high, 2)):
            seg[x - low] = 0

    limit = int(math.isqrt(high - 1))
    small_primes = sieve_primes(limit)

    for p in small_primes:
        # First multiple of p in [low, high)
        m = ((low + p - 1) // p) * p
        # But don't mark p itself if it's inside the segment, and avoid starting before p*p
        if m < p * p:
            m = p * p
        for x in range(m, high, p):
            seg[x - low] = 0

    res = []
    for i, flag in enumerate(seg):
        if flag:
            n = low + i
            if n >= 2:
                res.append(n)
    return res


def D(a: int, b: int, k: int) -> int:
    """
    Compute D(a,b,k) as defined in the problem statement.
    Uses the closed-form d(p,p-1,k) ≡ (k-1)^(-1) mod p for k>=2 and k<p.
    """
    primes = primes_in_range(a, b)

    if k == 0:
        # d(p, p-1, 0) is inverse of p-1 which is -1 mod p => p-1.
        return sum(p - 1 for p in primes)

    if k == 1:
        # sum_{i=1..p-1} i^{-1} ≡ sum_{i=1..p-1} i ≡ 0 (mod p)
        return 0

    x = k - 1
    total = 0
    for p in primes:
        # Fermat's little theorem: a^(p-2) mod p is inverse of a mod p, for a not divisible by p.
        total += pow(x, p - 2, p)
    return total


def solve() -> None:
    # Test values given in the problem statement
    assert D(101, 1, 10) == 45
    assert D(10**3, 10**2, 10**2) == 8334
    assert D(10**6, 10**3, 10**3) == 38162302

    ans = D(10**9, 10**5, 10**5)
    print(ans)


if __name__ == "__main__":
    solve()
