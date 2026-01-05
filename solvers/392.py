#!/usr/bin/env python3
"""
Project Euler 392 - Enmeshed Unit Circle

We choose N inner vertical and N inner horizontal grid lines (outer lines fixed at -1 and 1)
to minimize the total area of the grid cells that overlap the unit circle.

This implementation derives the optimum analytically and computes the minimal area for N=400.
No external libraries are used.
"""

from __future__ import annotations

import math


def _f(x: float) -> float:
    """f(x) = sqrt(1 - x^2) for x in [0, 1]."""
    return math.sqrt(max(0.0, 1.0 - x * x))


def _end_x(m: int, x1: float) -> float:
    """
    Given m intervals in [0,1] for the first quadrant grid, and a starting x1 (the first interior
    vertical line), generate x_m by the optimality recurrence (shooting method).

    Returns x_m (should be 1.0 at the correct x1). If x1 is invalid or diverges, returns +inf.
    """
    if not (0.0 < x1 < 1.0):
        return float("inf")

    x_prev = 0.0
    x_cur = x1
    g_prev = 1.0  # f(0)

    # Build up to x_m (there are m intervals, so m+1 points x_0..x_m)
    for k in range(1, m):
        if x_cur <= 0.0:
            return float("inf")
        if x_cur >= 1.0:
            # Overshot before reaching k=m; still fine for bracketing (>1)
            return x_cur

        g_cur = _f(x_cur)
        x_next = x_cur + (g_prev - g_cur) * g_cur / x_cur

        # Basic sanity: must be increasing.
        if not (x_cur < x_next):
            return float("inf")

        x_prev, x_cur = x_cur, x_next
        g_prev = g_cur

    return x_cur


def _solve_quadrant(m: int) -> float:
    """
    Solve the minimized red area in the first quadrant [0,1]^2 and return that area.

    m = number of intervals per axis in the quadrant grid.
    """
    # Bisection on x1 so that the recurrence lands exactly at x_m = 1.
    lo = 1e-6
    while _end_x(m, lo) >= 1.0:
        lo *= 0.5
        if lo < 1e-20:
            raise RuntimeError("Failed to bracket the solution (lo).")

    hi = 0.9
    while _end_x(m, hi) <= 1.0:
        hi = (hi + 1.0) / 2.0
        if hi >= 1.0 - 1e-15:
            raise RuntimeError("Failed to bracket the solution (hi).")

    for _ in range(200):
        mid = (lo + hi) / 2.0
        if _end_x(m, mid) > 1.0:
            hi = mid
        else:
            lo = mid

    x1 = (lo + hi) / 2.0

    # Generate the optimal x-grid in [0,1]: x_0=0 < ... < x_m=1.
    xs = [0.0, x1]
    g_prev = 1.0
    for k in range(1, m):
        xk = xs[k]
        gk = _f(xk)
        xs.append(xk + (g_prev - gk) * gk / xk)
        g_prev = gk

    # The optimal staircase outer-cover area in the quadrant is:
    # S = sum_{i=0}^{m-1} (x_{i+1}-x_i) * f(x_i)
    area_q = 0.0
    for i in range(m):
        xi = xs[i]
        area_q += (xs[i + 1] - xi) * _f(xi)

    return area_q


def minimal_red_area(N: int) -> float:
    """
    Return the minimal total red area in the full square [-1,1]^2.

    Using symmetry, we can split all rectangles by the axes (x=0 and y=0). This doesn't change
    the total red area, but reduces the geometry to the first quadrant with x,y >= 0 where a cell
    is red iff its lower-left corner is inside the quarter circle.

    In the first quadrant, the optimal solution uses a staircase boundary that drops exactly one
    y-level per x-interval, and each staircase corner lies on the circle. This reduces the 2D
    optimization to a 1D optimal partition problem for f(x)=sqrt(1-x^2).
    """
    if N < 1:
        raise ValueError("N must be >= 1.")
    m = (
        N // 2 + 1
    )  # number of intervals per axis in the first quadrant after splitting by axes
    area_q = _solve_quadrant(m)
    return 4.0 * area_q


def _round10(x: float) -> float:
    """Round to 10 digits after the decimal point."""
    return float(f"{x:.10f}")


def main() -> None:
    # Test value from the problem statement:
    assert _round10(minimal_red_area(10)) == 3.3469640797

    ans = minimal_red_area(400)
    print(f"{ans:.10f}")


if __name__ == "__main__":
    main()
