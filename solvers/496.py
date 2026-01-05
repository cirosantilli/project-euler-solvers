#!/usr/bin/env python3
"""
Project Euler 496: Incenter and circumcenter of triangle

We need F(L): sum of BC over all integer-sided triangles ABC such that:
- I is incenter
- D is the second intersection of AI with circumcircle
- AC = DI
- BC <= L

This program computes F(10^9) and prints it.

No external libraries are used.
"""

from __future__ import annotations

import math


def build_spf(n: int) -> list[int]:
    """Smallest prime factor sieve up to n (inclusive)."""
    spf = list(range(n + 1))
    if n >= 0:
        spf[0] = 0
    if n >= 1:
        spf[1] = 1
    lim = int(math.isqrt(n))
    for i in range(2, lim + 1):
        if spf[i] == i:  # prime
            step = i
            start = i * i
            for j in range(start, n + 1, step):
                if spf[j] == j:
                    spf[j] = i
    return spf


def squarefree_divs_mu_times_d(p: int, spf: list[int]) -> list[tuple[int, int]]:
    """
    Return list of (d, mu(d)*d) over all squarefree divisors d of p.
    We store coef = mu(d)*d to speed up later sums.

    For squarefree d:
      mu(d) = (-1)^(number of prime factors)
    """
    # distinct prime factors of p
    primes: list[int] = []
    x = p
    while x > 1:
        pr = spf[x]
        primes.append(pr)
        while x % pr == 0:
            x //= pr

    divs: list[tuple[int, int]] = [(1, 1)]  # (d, mu(d)*d)
    for pr in primes:
        # If coef = mu(d)*d, then for d' = d*pr: coef' = mu(d')*d' = (-mu(d))*(d*pr) = -coef*pr
        current = divs[:]  # small (<=64 entries), copying is cheap
        for d, coef in current:
            divs.append((d * pr, -coef * pr))
    return divs


def coprime_prefix_sum(divs_mu_d: list[tuple[int, int]], x: int) -> int:
    """
    S(x) = sum_{1<=q<=x, gcd(p,q)=1} q
    where divs_mu_d encodes the squarefree divisors of p as (d, mu(d)*d).

    Using Möbius inversion:
      [gcd(p,q)=1] = sum_{d|gcd(p,q)} mu(d)
    so:
      S(x) = sum_{d|p} mu(d) * sum_{q<=x, d|q} q
           = sum_{d|p} mu(d) * d * T(floor(x/d)),
      where T(n)=n(n+1)/2.
    """
    if x <= 0:
        return 0
    total = 0
    for d, coef in divs_mu_d:  # coef = mu(d)*d
        n = x // d
        total += coef * (n * (n + 1) // 2)
    return total


def F(L: int) -> int:
    """
    Compute F(L) as defined in the problem.
    """
    # p*q <= L and q < 2p => p <= sqrt(L) is safe upper bound
    p_max = int(math.isqrt(L)) + 1

    spf = build_spf(p_max)
    div_lists = [None] * (p_max + 1)
    div_lists[1] = [(1, 1)]
    for p in range(2, p_max + 1):
        div_lists[p] = squarefree_divs_mu_times_d(p, spf)

    ans = 0
    for p in range(1, p_max + 1):
        q_low = p + 1
        q_high = min(2 * p - 1, L // p)
        if q_low > q_high:
            continue

        M = L // p  # then floor(L/(p*q)) == (L//p)//q == M//q
        divs_mu_d = div_lists[p]

        q = q_low
        while q <= q_high:
            v = M // q
            q_end = min(q_high, M // v)  # largest q with same quotient v

            # sum of q in [q, q_end] coprime to p
            sum_q = coprime_prefix_sum(divs_mu_d, q_end) - coprime_prefix_sum(
                divs_mu_d, q - 1
            )
            if sum_q:
                tri = v * (v + 1) // 2  # 1+2+...+v
                ans += p * tri * sum_q

            q = q_end + 1

    return ans


def main() -> None:
    # Test value from the problem statement
    assert F(15) == 45

    print(F(10**9))


if __name__ == "__main__":
    main()
