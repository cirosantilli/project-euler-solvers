#!/usr/bin/env python3
"""
Project Euler 641 - A Long Row of Dice

We have n dice in a row, all showing 1.
For k = 2..n we "turn" every k-th die, increasing its face by 1 (wrapping 6->1).
Let f(n) be the number of dice showing 1 at the end. Compute f(10^36).

This solution is self-contained and uses only the Python standard library.
"""

from __future__ import annotations

import math


def icbrt(n: int) -> int:
    """Integer floor cube root: largest x with x^3 <= n."""
    if n < 0:
        raise ValueError("icbrt() argument must be non-negative")
    if n < 2:
        return n
    # Upper bound based on bit-length: (2^k)^3 = 2^(3k)
    hi = 1 << ((n.bit_length() + 2) // 3)
    lo = hi >> 1
    while lo + 1 < hi:
        mid = (lo + hi) >> 1
        m3 = mid * mid * mid
        if m3 <= n:
            lo = mid
        else:
            hi = mid
    return lo


def mobius_sieve(limit: int) -> list[int]:
    """
    Linear sieve for Möbius function μ(1..limit).
    μ(n)=0 if n has a squared prime factor, else (-1)^(number of prime factors).
    """
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


def count_f(n: int) -> int:
    """
    Compute f(n) for the dice process described in the problem.
    """
    # A die at position i is turned once for each divisor k >= 2 of i,
    # hence exactly τ(i) - 1 times where τ is the divisor-count function.
    # The final face is 1 iff τ(i) ≡ 1 (mod 6).
    #
    # τ(i) ≡ 1 (mod 6) implies τ(i) is odd => i is a perfect square: i = x^2.
    # Writing x = ∏ p^b, then τ(x^2) = ∏ (2b+1).
    # Modulo 3: 2b+1 ≡ 1-b (mod 3), so b ≡ 1 (mod 3) is forbidden (would give 0 mod 3),
    # and b ≡ 2 (mod 3) contributes -1; we need an even number of such primes.
    #
    # Unique factorization: x = y^3 * z^2 where z is squarefree and primes in z are exactly
    # those with exponent b ≡ 2 (mod 3). Parity condition: z has an even number of primes.
    #
    # Therefore f(n) = #{ x <= floor(sqrt(n)) : x = y^3 z^2, z squarefree, ω(z) even }.
    M = math.isqrt(n)  # x <= M

    # We will sum over z using Möbius:
    # For squarefree z, μ(z) = (-1)^ω(z). Indicator[ω(z) even AND squarefree] = (μ(z)^2 + μ(z)) / 2.
    # Let t(z) = floor( (M / z^2)^(1/3) ). Then:
    #   f(n) = (S0 + S1) / 2
    # where
    #   S0 = sum_z μ(z)^2 * t(z)    (counts squarefree z)
    #   S1 = sum_z μ(z)    * t(z)    (alternating by parity of ω(z))
    #
    # Group by y = t(z):
    # y is in [1 .. floor(cuberoot(M))].
    # For fixed y:
    #   y <= (M / z^2)^(1/3) < y+1
    #   => sqrt(M / (y+1)^3) < z <= sqrt(M / y^3)
    # Define:
    #   R(y) = floor_sqrt(M / y^3)
    #   L(y) = floor_sqrt(M / (y+1)^3)
    # Then z in (L(y), R(y)] have t(z)=y.
    #
    # So we need prefix sums:
    #   Q(n) = sum_{k<=n} μ(k)^2  (number of squarefree <= n)
    #   M(n) = sum_{k<=n} μ(k)    (Mertens function)
    # to answer interval queries quickly.

    # Max z queried is R(1) = floor_sqrt(M)
    z_max = math.isqrt(M)

    # For Mertens recursion up to z_max, precompute μ and prefix sums up to about z_max^(2/3).
    c = icbrt(z_max)  # floor(z_max^(1/3))
    limit = max(c * c + 10, math.isqrt(z_max) + 10, 1000)

    mu = mobius_sieve(limit)

    mertens_small = [0] * (limit + 1)
    sqfree_small = [0] * (limit + 1)
    s = 0
    q = 0
    for i in range(1, limit + 1):
        s += mu[i]
        mertens_small[i] = s
        if mu[i] != 0:
            q += 1
        sqfree_small[i] = q

    mertens_cache: dict[int, int] = {}

    def mertens(n_: int) -> int:
        """M(n)=sum_{k<=n} μ(k), using recursion + quotient grouping."""
        if n_ <= limit:
            return mertens_small[n_]
        v = mertens_cache.get(n_)
        if v is not None:
            return v
        res = 1
        i = 2
        while i <= n_:
            q_ = n_ // i
            j = n_ // q_
            res -= (j - i + 1) * mertens(q_)
            i = j + 1
        mertens_cache[n_] = res
        return res

    sqfree_cache: dict[int, int] = {}

    def squarefree_count(n_: int) -> int:
        """
        Q(n)=sum_{k<=n} μ(k)^2, i.e. count of squarefree numbers <= n.
        Uses: Q(n) = sum_{d<=sqrt(n)} μ(d) * floor(n/d^2)
        with grouping by constant floor(n/d^2).
        """
        if n_ <= 0:
            return 0
        if n_ <= limit:
            return sqfree_small[n_]
        v = sqfree_cache.get(n_)
        if v is not None:
            return v

        m = math.isqrt(n_)  # only up to sqrt(1e9)=31623 for this problem
        res = 0
        d = 1
        # d_max <= m <= sqrt(n_) <= sqrt(z_max) <= limit (by construction)
        while d <= m:
            k = n_ // (d * d)
            d_max = math.isqrt(n_ // k)
            res += (mertens_small[d_max] - mertens_small[d - 1]) * k
            d = d_max + 1

        sqfree_cache[n_] = res
        return res

    Y = icbrt(M)

    S0 = 0
    S1 = 0
    for y in range(1, Y + 1):
        y3 = y * y * y
        R = math.isqrt(M // y3)
        yp1 = y + 1
        yp13 = yp1 * yp1 * yp1
        L = math.isqrt(M // yp13) if yp13 <= M else 0
        if R == L:
            continue
        S0 += y * (squarefree_count(R) - squarefree_count(L))
        S1 += y * (mertens(R) - mertens(L))

    return (S0 + S1) // 2


def main() -> None:
    # Problem statement test values
    assert count_f(100) == 2
    assert count_f(10**8) == 69

    print(count_f(10**36))


if __name__ == "__main__":
    main()
