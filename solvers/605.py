#!/usr/bin/env python3
"""
Project Euler 605: Pairwise Coin-Tossing Game

We model the game as an infinite sequence of independent fair coin flips X_1, X_2, ...
For round i (players i vs i+1, cyclic), let:
    X_i = 1  if the *second* player (i+1) wins round i,
         0  otherwise (the first player i wins).

A player wins the whole game exactly when they win two consecutive rounds; this happens
precisely when the pattern (X_i, X_{i+1}) = (1, 0) occurs, because only the shared
player (i+1) can win both rounds i and i+1. The winner is then player i+1.

Let T be the index of the second flip of the first occurrence of pattern "10"
(i.e. the smallest t >= 2 with X_{t-1}=1 and X_t=0). Then the winner is player T mod n.

The probability that T = m is:
    P(T=m) = (m-1) / 2^m  for m >= 2
because the sequence must be some zeros, then a 1, then (m-2-a) ones, then the final 0.

For k in {1..n}:
    P_n(k) = sum_{j>=0} P(T = k + jn)
           = sum_{j>=0} (k+jn-1) / 2^{k+jn}

This is a geometric-series sum leading to the closed form:

Let A = 2^n - 1.
Let N0 = (k-1)*A + n.

Then:
    P_n(k) = (2^{n-k} * N0) / A^2  (as a rational number, before reduction).

For the specific asked n = 10^8+7 (a prime), gcd(n, 2^n-1)=1 so this fraction is already reduced,
and M_n(k) = numerator * denominator can be computed directly modulo 10^8.
"""

from math import gcd


MOD = 10**8


def reduced_fraction_P(n: int, k: int) -> tuple[int, int]:
    """
    Return the reduced fraction numerator/denominator for P_n(k).

    This routine uses big integers and is intended for small n (used for the problem's examples).
    """
    if not (1 <= k <= n):
        raise ValueError("Require 1 <= k <= n")

    A = (1 << n) - 1  # 2^n - 1
    N0 = (k - 1) * A + n

    num = (1 << (n - k)) * N0
    den = A * A

    # g = gcd(N0, A^2) but computed cheaply as gcd(N0, A) twice (handles square factors).
    g1 = gcd(N0, A)
    g2 = gcd(N0 // g1, A)
    g = g1 * g2

    num //= g
    den //= g
    gnd = gcd(num, den)
    # Defensive: ensure fully reduced
    num //= gnd
    den //= gnd
    return num, den


def last8digits_M(n: int, k: int) -> int:
    """
    Compute the last 8 digits of M_n(k) for the specific Project Euler 605 target values.

    For n = 10^8+7 (prime), the fraction is reduced and:
        M = (2^{n-k} * ((k-1)(2^n-1) + n)) * (2^n-1)^2
    So we compute everything modulo 10^8.
    """
    if not (1 <= k <= n):
        raise ValueError("Require 1 <= k <= n")

    two_n = pow(2, n, MOD)
    A_mod = (two_n - 1) % MOD

    N0_mod = ((k - 1) * A_mod + (n % MOD)) % MOD
    part1 = pow(2, n - k, MOD)
    part2 = (A_mod * A_mod) % MOD

    return (part1 * N0_mod % MOD) * part2 % MOD


def main() -> None:
    # Examples from the problem statement:
    num, den = reduced_fraction_P(3, 1)
    assert (num, den) == (12, 49)
    assert num * den == 588

    num, den = reduced_fraction_P(6, 2)
    assert (num, den) == (368, 1323)
    assert num * den == 486864

    n = 10**8 + 7
    k = 10**4 + 7
    ans = last8digits_M(n, k)
    # Print as exactly 8 digits (leading zeros if any).
    print(f"{ans:08d}")


if __name__ == "__main__":
    main()
