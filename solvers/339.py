#!/usr/bin/env python3
"""
Project Euler 339: Peredur fab Efrawg

We compute E(n): the optimal expected final number of black sheep starting from n black and n white.

No external libraries are used.
"""

from __future__ import annotations


def expected_black(n: int) -> float:
    """
    Return E(n) for Project Euler 339.

    Derivation summary (full details in README.md):
    Let S_m(b) be the optimal value at the *decision stage* (after a bleat+conversion)
    when there are m total sheep and b black sheep. For fixed m this becomes an
    optimal-stopping problem on a 1D birth-death chain. Using the chain's scale
    function, S_m is the least concave majorant of the previous payoff, which
    (by symmetry/monotonicity) implies the stopping region is exactly b <= floor(m/2).
    This collapses the whole DP to a simple O(n) recurrence.

    The final answer needed by the problem is E(10_000).
    """
    if n < 1:
        raise ValueError("n must be >= 1")

    # Boundary values:
    # B[b] := S_{2b}(b) = S_{2b-1}(b)  (the value at the midpoint once it first becomes "stoppable")
    B = [0.0] * (n + 1)
    B[0] = 0.0

    # p is the central binomial probability for even N = 2b-2:
    # p = C(N, N/2) / 2^N, with N starting at 0.
    p = 1.0  # N=0

    for b in range(1, n + 1):
        # Ratio of scale increments in the continuation region for m = 2b-1:
        # r = 2p / (1+p)
        r = (2.0 * p) / (1.0 + p)

        # Compute B[b] from B[b-1] using m = 2b-1.
        m = 2 * b - 1
        B[b] = B[b - 1] + (m - B[b - 1]) * r

        # Update p for next b (N increases by 2):
        # p_{N+2} = p_N * (N+1)/(N+2)  where N = 2b-2, so factor = (2b-1)/(2b)
        p *= (2.0 * b - 1.0) / (2.0 * b)

    # For the final step we need S_{2n}(n+1), which is in the continuation region for m=2n.
    # Let q be the "central" binomial probability for odd N = 2n-1 at k=n:
    # q = C(N, n) / 2^N.
    # Recurrence for odd N: q_{N+2} = q_N * (N+2)/(N+3).
    q = 0.5  # N=1, C(1,1)/2 = 1/2
    for t in range(1, n):
        # N = 2t-1  -> factor = (2t+1)/(2t+2)
        q *= (2.0 * t + 1.0) / (2.0 * t + 2.0)

    # In scale coordinates, S_{2n}(b) is linear between b=n (value B[n]) and b=2n (value 2n).
    # The scale step from b=n to b=n+1 for m=2n corresponds to ratio r2 = C(2n-1, n) / 2^(2n-2) = 2*q.
    r2 = 2.0 * q

    m2 = 2 * n
    S_n_plus_1 = B[n] + (m2 - B[n]) * r2

    # Initial state is before the first bleat: b=n, m=2n.
    # So E(n) = (1/2) * ( S_{2n}(n-1) + S_{2n}(n+1) ).
    # And since n-1 is in the stopping region for m=2n, S_{2n}(n-1) = B[n-1].
    return 0.5 * (B[n - 1] + S_n_plus_1)


def solve() -> str:
    n = 10_000
    ans = expected_black(n)
    return f"{ans:.6f}"


def _self_test() -> None:
    # Test value given in the problem statement:
    assert abs(expected_black(5) - 6.871346) < 5e-7

    # Extra sanity checks (also known values from community discussions).
    assert abs(expected_black(1) - 1.0) < 1e-12
    assert abs(expected_black(2) - (55.0 / 24.0)) < 1e-12
    assert abs(expected_black(3) - (1981.0 / 528.0)) < 1e-12


if __name__ == "__main__":
    _self_test()
    print(solve())
