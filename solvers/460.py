#!/usr/bin/env python3
"""
Project Euler 460: An Ant on the Move

We compute F(10000) (rounded to 9 decimal places).

Key idea: the given "constant velocity" on a straight segment is the logarithmic mean,
so the travel time equals the integral of (ds / y) along that straight segment.
That allows a symmetry + dynamic-programming reduction to a 1D DP over heights.

No third-party libraries are used.
"""

from __future__ import annotations

import math
from typing import List


def _min_step_excess(y0: int, y1: int, h: int, logs: List[float]) -> float:
    """
    Minimal excess cost to go from height y0 to y1 (y1>y0) during the "climb",
    where excess is: time(step) - (dx / h).

    We optimize over integer dx >= 0. The continuous optimum is attained at
    dx* = dy * L / sqrt(h^2 - L^2) where L is the logarithmic mean of y0,y1.
    Because the objective is convex in dx, the best integer dx is near dx*,
    so checking floor(dx*) and ceil(dx*) suffices.
    """
    dy = y1 - y0
    # Logarithmic mean (y1-y0)/(ln y1 - ln y0)
    v = dy / (logs[y1] - logs[y0])  # v < h always when y1 <= h and y0 < y1
    denom = math.sqrt(h * h - v * v)
    dx_star = dy * v / denom

    best = float("inf")
    k = int(dx_star)
    for dx in (k, k + 1):
        if dx < 0:
            continue
        # time(step) - saved cruising time
        val = math.hypot(dx, dy) / v - dx / h
        if val < best:
            best = val
    return best


def _best_climb_excess(h: int, window_const: int = 64) -> float:
    """
    Compute dp[h] where dp[y] is minimal excess cost to climb from y=1 to y,
    with cruising speed fixed at v_cruise = h.

    To make it fast, we only consider y0 in [y - M, y), where
    M = O(h/y). This matches the fact that the optimal path is close to the
    hyperbolic geodesic (a semicircle), where typical vertical step sizes
    shrink like ~h/y as y grows.
    """
    logs = [0.0] * (h + 1)
    for y in range(1, h + 1):
        logs[y] = math.log(y)

    dp = [float("inf")] * (h + 1)
    dp[1] = 0.0

    for y in range(2, h + 1):
        # Empirically/provably-safe window around y, shrinking as y increases.
        M = int(window_const * h / y) + 2
        y0_min = 1 if y - M < 1 else y - M

        best = float("inf")
        for y0 in range(y0_min, y):
            cand = dp[y0] + _min_step_excess(y0, y, h, logs)
            if cand < best:
                best = cand
        dp[y] = best

    return dp[h]


def F(d: int) -> float:
    """
    Compute F(d): the minimal travel time from (0,1) to (d,1).

    For even d (the case needed for the problem), the optimal path is symmetric and
    reaches its maximum height at y = d/2. Then
        F(d) = 2*E + d/h,  where h=d/2 and E is the minimal climb excess to reach h.

    For odd d, we try both neighboring heights floor(d/2) and ceil(d/2) and take min.
    """
    if d < 1:
        raise ValueError("d must be a positive integer")

    # Candidate top heights near d/2.
    h0 = d // 2
    candidates = [h0] if d % 2 == 0 else [h0, h0 + 1]
    best = float("inf")
    for h in candidates:
        if h < 1:
            continue
        E = _best_climb_excess(h)
        total = 2.0 * E + d / h
        if total < best:
            best = total
    return best


def solve() -> str:
    # Asserts for the verification values given in the problem statement.
    # Compare on the 9-decimal rounding requested/used by the statement.
    assert f"{F(4):.9f}" == "2.960516287"
    assert f"{F(10):.9f}" == "4.668187834"
    assert f"{F(100):.9f}" == "9.217221972"

    ans = F(10000)
    return f"{ans:.9f}"


if __name__ == "__main__":
    print(solve())
