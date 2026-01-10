#!/usr/bin/env python3
"""
Project Euler 664 - An Infinite Game

We compute F(n): the maximum number of squares a token can be moved to the right of
the dividing line.

Key result used here:
    F(n) = 3 + ceil( log_phi( A_n ) )
where
    phi = (1+sqrt(5))/2
    sigma = 1/phi
    A_n = sum_{d>=1} d^n * sigma^d

Moreover, for n >= 3 we can compute log(A_n) essentially exactly via singularity
analysis of the exponential generating function of A_n:
    sum_{n>=0} A_n * x^n/n! = sigma*e^x / (1 - sigma*e^x)
This has a dominant simple pole at x0 = ln(phi), giving
    A_n = n! / (ln(phi))^(n+1) * (1 + exponentially tiny error).

For the required n = 1234567 that error is so small it has no effect on the final
ceiling.
"""

from __future__ import annotations

import math


SQRT5 = math.sqrt(5.0)
PHI = (1.0 + SQRT5) / 2.0
LN_PHI = math.log(PHI)
LN_LN_PHI = math.log(LN_PHI)  # ln(ln(phi))


def _ceil_with_integer_guard(x: float, eps: float = 1e-10) -> int:
    """
    Ceil that is stable when x is extremely close to an integer (within eps).
    In that case, return that integer.
    """
    k = round(x)
    if abs(x - k) < eps:
        return int(k)
    return int(math.floor(x) + 1)


def F(n: int) -> int:
    """
    Maximum number of squares beyond the dividing line that can be reached.
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    # Small n are edge-cases where log_phi(A_n) is exactly an integer and the
    # strict-inequality boundary matters; keep them exact and simple.
    if n == 0:
        return 4
    if n == 1:
        return 6
    if n == 2:
        return 9

    # For n>=3, use the dominant-pole asymptotic (effectively exact here):
    # ln(A_n) = ln(n!) - (n+1)*ln(ln(phi))
    lnA = math.lgamma(n + 1) - (n + 1) * LN_LN_PHI
    log_phi_A = lnA / LN_PHI
    return 3 + _ceil_with_integer_guard(log_phi_A)


def solve() -> int:
    # Test values from the problem statement.
    assert F(0) == 4
    assert F(1) == 6
    assert F(2) == 9
    assert F(3) == 13
    assert F(11) == 58
    assert F(123) == 1173

    return F(1234567)


if __name__ == "__main__":
    print(solve())
