#!/usr/bin/env python3
"""
Project Euler 430: Range Flips

N disks in a row, all initially white. Each turn chooses A,B uniformly from {1..N}
(independently, with replacement) and flips the whole interval [min(A,B), max(A,B)].

Let E(N,M) be the expected number of white disks after M turns.
We need E(10^10, 4000), rounded to 2 decimals.

No external libraries are used.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, getcontext


def expected_small(N: int, M: int) -> float:
    """
    Exact (up to floating rounding) computation by summing all disks.
    Suitable for small N (used for the problem statement's check values).
    """
    n2 = float(N * N)
    total = 0.0
    for i in range(1, N + 1):
        # Probability disk i is flipped in one move:
        # p = 1 - P(A<i,B<i) - P(A>i,B>i)
        p = 1.0 - ((i - 1) * (i - 1) + (N - i) * (N - i)) / n2
        r = 1.0 - 2.0 * p  # E[(-1)^{flip}] per turn for this disk
        total += 0.5 * (1.0 + (r**M))
    return total


def expected_large(N: int, M: int) -> Decimal:
    """
    Fast high-accuracy computation for very large N.

    Derivation sketch (details in README.md):
      E(N,M) = N/2 + 1/2 * sum_{i=1..N} r_i^M
      where r_i = 1 - 2*p_i and p_i is the one-turn flip probability for disk i.

    For large N the r_i values are sampled at the midpoints of N equal subintervals of [-1,1]
    of the smooth function f(x) = (x^2 - c)^M with c=(2N-1)/N^2.
    Thus the sum is a composite midpoint rule for an integral; its error is O(M^2/N).

    Expanding the integral in the tiny parameter c=O(1/N) and keeping the first two terms yields:
        sum r_i^M = N/(2M+1) - N*M*c/(2M-1) + O(M^2/N)
    which is far within 0.01 when N=10^10 and M=4000.

    We compute the closed form with Decimal to avoid any rounding surprises.
    """
    getcontext().prec = 60
    Nd = Decimal(N)
    Md = Decimal(M)

    # c = (2N - 1) / N^2
    # E = N/2 + 1/2 * [ N/(2M+1) - N*M*c/(2M-1) ]
    # Simplify the c-term: N*M*c = M*(2N-1)/N
    E = Nd / 2 + Nd / (2 * (2 * Md + 1)) - (Md * (2 * Nd - 1)) / (2 * Nd * (2 * Md - 1))
    return E


def solve() -> str:
    # Asserts from the problem statement
    assert abs(expected_small(3, 1) - (10.0 / 9.0)) < 1e-12
    assert abs(expected_small(3, 2) - (5.0 / 3.0)) < 1e-12
    assert abs(expected_small(10, 4) - 5.157) < 1e-3
    assert abs(expected_small(100, 10) - 51.893) < 1e-3

    ans = expected_large(10**10, 4000)
    ans2 = ans.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return format(ans2, "f")


if __name__ == "__main__":
    print(solve())
