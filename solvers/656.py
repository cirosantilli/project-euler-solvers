#!/usr/bin/env python3
"""Project Euler 656 - Palindromic Sequences

We use a continued-fraction characterization of palindromic prefixes of the
Sturmian (Beatty-difference) word induced by alpha = sqrt(beta).

No external libraries are used.
"""

import math

MOD = 10**15
LIMIT_BETA = 1000
G = 100


def sqrt_continued_fraction_period(n: int):
    """Return (a0, period) for sqrt(n) where n is a positive non-square integer.

    sqrt(n) = [a0; period repeating]. The standard algorithm for quadratic surds
    yields the period; it ends when a == 2*a0.
    """
    a0 = math.isqrt(n)
    if a0 * a0 == n:
        raise ValueError("n must be non-square")

    m = 0
    d = 1
    a = a0
    period = []
    while True:
        m = d * a - m
        d = (n - m * m) // d
        a = (a0 + m) // d
        period.append(a)
        if a == 2 * a0:
            break
    return a0, period


def pal_prefix_lengths_from_period(period, g: int):
    """Generate the first g palindromic prefix lengths for alpha=sqrt(beta).

    Let theta = frac(alpha) = [0; a1,a2,...] and define convergent denominators
    q_-1=0, q_0=1, q_k = a_k*q_{k-1} + q_{k-2}.
    Then palindromic prefix lengths are:
        n = q_{k-2} + t*q_{k-1}  for odd k, 1 <= t <= a_k,
    in increasing order.
    """
    out = []
    q_m1, q0 = 0, 1
    k = 1  # coefficient index (a1 has k=1)
    i = 0  # index into period
    while len(out) < g:
        a = period[i]
        i += 1
        if i == len(period):
            i = 0

        if k % 2 == 1:
            for t in range(1, a + 1):
                out.append(q_m1 + t * q0)
                if len(out) >= g:
                    return out

        q1 = a * q0 + q_m1
        q_m1, q0 = q0, q1
        k += 1
    return out


def H_mod_from_period(period, g: int, mod: int = MOD) -> int:
    """Compute H_g modulo mod using arithmetic-progression summation."""
    q_m1, q0 = 0, 1
    k = 1
    i = 0
    count = 0
    s = 0
    while count < g:
        a = period[i]
        i += 1
        if i == len(period):
            i = 0

        if k % 2 == 1:
            remaining = g - count
            tmax = a if a <= remaining else remaining
            # sum_{t=1..tmax} (q_m1 + t*q0) = tmax*q_m1 + q0*tmax*(tmax+1)/2
            s += tmax * q_m1 + q0 * (tmax * (tmax + 1) // 2)
            s %= mod
            count += tmax

        q1 = a * q0 + q_m1
        q_m1, q0 = q0, q1
        k += 1
    return s % mod


def solve() -> str:
    # Problem-statement checks for alpha = sqrt(31)
    _, period31 = sqrt_continued_fraction_period(31)
    expected_n20 = [
        1,
        3,
        5,
        7,
        44,
        81,
        118,
        273,
        3158,
        9201,
        15244,
        21287,
        133765,
        246243,
        358721,
        829920,
        9600319,
        27971037,
        46341755,
        64712473,
    ]
    got_n20 = pal_prefix_lengths_from_period(period31, 20)
    assert got_n20 == expected_n20, (got_n20, expected_n20)
    assert sum(got_n20) == 150243655

    squares = {i * i for i in range(1, math.isqrt(LIMIT_BETA) + 1)}
    total = 0
    for beta in range(2, LIMIT_BETA + 1):
        if beta in squares:
            continue
        _, period = sqrt_continued_fraction_period(beta)
        total = (total + H_mod_from_period(period, G, MOD)) % MOD

    return f"{total:015d}"


if __name__ == "__main__":
    print(solve())
