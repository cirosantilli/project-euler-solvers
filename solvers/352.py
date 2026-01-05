#!/usr/bin/env python3
"""
Project Euler 352: Blood Tests

We model the optimal expected number of tests under the restriction that
whenever we start with a mixed (pooled) sample, we must fully resolve all
animals contributing to that sample before testing any other animals.

Key idea: dynamic programming with two states:
  U[n] = expected tests to fully classify n animals (unconditional).
  P[n] = expected additional tests to fully classify n animals given that
         at least one of them is infected (i.e. the whole group is known positive).

Answer required:
  sum_{p=0.01..0.50 step 0.01} T(10000, p), rounded to 6 decimals.
"""

from __future__ import annotations


def round6(x: float) -> float:
    # Formatting-based rounding avoids surprises from binary floating point.
    return float(f"{x:.6f}")


def T(s: int, p: float, kmax: int = 100) -> float:
    """
    Compute T(s,p) = optimal expected number of tests to screen s animals
    when each animal is infected independently with probability p.

    We restrict pool sizes to at most kmax. For this problem's parameter range
    (p in [0.01, 0.50]) kmax=100 is sufficient; increasing it further does not
    change the optimal values (and kmax=100 matches the official examples).
    """
    if s < 0:
        raise ValueError("s must be non-negative")
    if not (0.0 < p <= 1.0):
        raise ValueError("p must be in (0, 1]")

    kmax = min(kmax, s)
    a = 1.0 - p  # probability an animal is NOT infected

    # Precompute a^k for k=0..kmax
    powa = [1.0] * (kmax + 1)
    for k in range(1, kmax + 1):
        powa[k] = powa[k - 1] * a

    # U up to s, P up to kmax
    U = [0.0] * (s + 1)
    P = [0.0] * (kmax + 1)

    U[0] = 0.0
    if s >= 1:
        U[1] = 1.0  # need one test to classify one animal

    if kmax >= 1:
        P[1] = (
            0.0  # with one animal and "at least one infected", it's infected for sure
        )

    # Compute coupled DP for sizes up to kmax (or s if smaller).
    nlimit = min(s, kmax)
    for n in range(2, nlimit + 1):
        # Compute P[n]:
        # choose a subset of size k (1<=k<n) to test next
        denom = 1.0 - powa[n]  # P(group is positive) = 1 - a^n
        bestP = float("inf")
        for k in range(1, n):
            # Conditional probability that the chosen subset is positive,
            # given that the whole group is positive.
            prob_pos = (1.0 - powa[k]) / denom
            cand = 1.0 + prob_pos * (P[k] + U[n - k]) + (1.0 - prob_pos) * P[n - k]
            if cand < bestP:
                bestP = cand
        P[n] = bestP

        # Compute U[n]:
        bestU = float("inf")
        for k in range(1, n + 1):
            # 1 test for the pool + remaining + (if pool positive) resolve the pool
            cand = 1.0 + U[n - k] + (1.0 - powa[k]) * P[k]
            if cand < bestU:
                bestU = cand
        U[n] = bestU

    # For n > kmax, we only consider pool sizes up to kmax.
    for n in range(nlimit + 1, s + 1):
        bestU = float("inf")
        for k in range(1, kmax + 1):
            cand = 1.0 + U[n - k] + (1.0 - powa[k]) * P[k]
            if cand < bestU:
                bestU = cand
        U[n] = bestU

    return U[s]


def solve() -> str:
    # Asserts for the example values stated in the problem statement.
    assert round6(T(25, 0.02)) == 4.155452
    assert round6(T(25, 0.10)) == 12.702124

    total = 0.0
    for i in range(1, 51):
        p = i / 100.0
        total += T(10000, p)

    return f"{total:.6f}"


if __name__ == "__main__":
    print(solve())
