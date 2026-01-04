#!/usr/bin/env python3
"""
Project Euler 503 - Compromise or Persist

We compute F(n): Alice's minimum possible expected final score with n cards labeled 1..n.

Key idea:
- After each draw, Alice only learns the rank of the current card among all seen so far.
- The pattern of ranks (relative order) of seen cards is independent of which absolute values were drawn.
  Therefore, if Alice continues (discarding the current card), her expected future outcome depends only on
  how many cards have been seen so far, not on the specific rank she just observed.

This yields a 1D backward dynamic program with an optimal rank-threshold policy.
"""

from __future__ import annotations


def expected_score(n: int) -> float:
    """
    Return F(n) as a float.

    We work with normalized expectations x_t = G_t / (n+1), where:
      - t is the iteration number (1-indexed),
      - G_t is the optimal expected score from iteration t onward,
      - at iteration t, the rank k of the current card among the first t seen cards is uniform in {1..t},
      - the expected value of the k-th smallest element in a random t-subset of {1..n} is (n+1)*k/(t+1).

    In normalized form, the 'stop now' expectation is k/(t+1), and the 'continue' value is x_{t+1}.
    Optimal decision: stop iff k/(t+1) <= x_{t+1}, i.e. k <= floor(x_{t+1}*(t+1)).
    """
    if n <= 0:
        raise ValueError("n must be a positive integer")

    # Base case: at t=n (only one card remains), Alice must stop.
    # The expected last-card value is (n+1)/2, hence normalized x_n = 1/2.
    x_next = 0.5  # this is x_{t+1} while iterating backwards

    # Iterate t = n-1, n-2, ..., 1
    for t in range(n - 1, 0, -1):
        y = x_next
        tp1 = t + 1

        # Candidate threshold K = floor(y * (t+1))
        # Use a tiny bias plus correction loops to avoid float edge issues.
        K = int(y * tp1 + 1e-15)
        if K > t:
            K = t

        # Correct potential off-by-one due to floating rounding.
        # Ensure: K/(t+1) <= y < (K+1)/(t+1) (with a tiny tolerance).
        eps = 1e-15
        while K > 0 and (K / tp1) > y + eps:
            K -= 1
        while K < t and ((K + 1) / tp1) <= y - eps:
            K += 1

        # Expected normalized score at iteration t:
        # With prob K/t we stop at a rank in 1..K, else continue.
        # Sum_{k=1..K} k = K(K+1)/2.
        sumk = (K * (K + 1)) / 2.0
        x_t = (sumk / tp1 + (t - K) * y) / t

        x_next = x_t

    return x_next * (n + 1)


def _self_test() -> None:
    # Test values from the problem statement.
    assert abs(expected_score(3) - (5.0 / 3.0)) < 1e-12
    assert abs(expected_score(4) - (15.0 / 8.0)) < 1e-12
    assert abs(expected_score(10) - 2.5579365079) < 1e-10


def main() -> None:
    _self_test()
    ans = expected_score(10**6)
    print(f"{ans:.10f}")


if __name__ == "__main__":
    main()
