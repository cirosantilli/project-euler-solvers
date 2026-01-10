#!/usr/bin/env python3
"""
Project Euler 695: Random Rectangles

Three random points P1,P2,P3 are chosen uniformly in the unit square.
For each pair (i,j) form the axis-aligned rectangle having Pi and Pj as opposite corners.
Its area is |Xi-Xj| * |Yi-Yj|.

We need the expected value of the *second largest* of the three areas, to 10 decimals.

No external libraries are used.
"""

from __future__ import annotations

import math
from typing import List, Tuple


# --- Gauss–Legendre quadrature on [0,1] (no external libs) ---


def gauss_legendre_01(n: int) -> Tuple[List[float], List[float]]:
    """
    Nodes and weights for n-point Gauss–Legendre quadrature on [0,1].

    Computed by Newton iteration on roots of P_n(x) on [-1,1],
    then mapped to [0,1].
    """
    if n <= 0:
        raise ValueError("n must be positive")

    nodes = [0.0] * n
    weights = [0.0] * n
    m = (n + 1) // 2  # number of positive roots (incl. 0 if n odd)

    for i in range(m):
        # Good initial guess for i-th root (from Abramowitz–Stegun)
        x = math.cos(math.pi * (i + 0.75) / (n + 0.5))

        # Newton iterations
        for _ in range(100):
            # Evaluate P_n(x) and P_{n-1}(x) via recurrence
            p0, p1 = 1.0, x  # P_0, P_1
            for k in range(2, n + 1):
                p0, p1 = p1, ((2 * k - 1) * x * p1 - (k - 1) * p0) / k
            pn = p1
            pnm1 = p0

            # Derivative: P'_n(x) = n/(x^2-1) * (x P_n(x) - P_{n-1}(x))
            dpn = n * (x * pn - pnm1) / (x * x - 1.0)

            dx = pn / dpn
            x -= dx
            if abs(dx) < 1e-16:
                break

        w = 2.0 / ((1.0 - x * x) * (dpn * dpn))

        # Symmetry on [-1,1], then map to [0,1]
        xl = (-x + 1.0) * 0.5
        xr = (x + 1.0) * 0.5
        wl = w * 0.5
        wr = w * 0.5

        nodes[i] = xl
        nodes[n - 1 - i] = xr
        weights[i] = wl
        weights[n - 1 - i] = wr

    return nodes, weights


# --- Core math ---


def _median_index(a: float, b: float, c: float) -> int:
    """Return 0 if a is median, 1 if b is median, 2 if c is median."""
    if (a <= b <= c) or (c <= b <= a):
        return 1
    if (b <= a <= c) or (c <= a <= b):
        return 0
    return 2


def integral_median_linear(p: float, q: float, c: float) -> float:
    """
    Exact integral over t in [0,1] of median( p*t, q*(1-t), c ).

    For fixed nonnegative (p,q,c), the three functions are linear in t,
    so the median is piecewise linear with breakpoints where two are equal.
    We integrate exactly on each interval.
    """
    # Collect candidate breakpoints within (0,1)
    bps = [0.0, 1.0]

    # p*t = c  => t = c/p
    if p > 0.0:
        t = c / p
        if 0.0 < t < 1.0:
            bps.append(t)

    # q*(1-t) = c => t = 1 - c/q
    if q > 0.0:
        t = 1.0 - c / q
        if 0.0 < t < 1.0:
            bps.append(t)

    # p*t = q*(1-t) => t = q/(p+q)
    if p + q > 0.0:
        t = q / (p + q)
        if 0.0 < t < 1.0:
            bps.append(t)

    # Sort + dedupe
    bps = sorted(set(bps))

    total = 0.0
    for t0, t1 in zip(bps, bps[1:]):
        tm = 0.5 * (t0 + t1)
        a = p * tm
        b = q * (1.0 - tm)

        which = _median_index(a, b, c)
        if which == 0:
            # ∫ p t dt = p/2 (t1^2 - t0^2)
            total += p * (t1 * t1 - t0 * t0) * 0.5
        elif which == 1:
            # ∫ (q - q t) dt = q (t1-t0) - q/2 (t1^2 - t0^2)
            total += q * (t1 - t0) - q * (t1 * t1 - t0 * t0) * 0.5
        else:
            # ∫ c dt
            total += c * (t1 - t0)

    return total


# Relative y-order permutations (with x-order fixed as 1<2<3).
# For each permutation of labels in increasing y-order, encode dy for each pair:
# code 0 => lower gap (proportional to u), 1 => upper gap (proportional to 1-u), 2 => span (proportional to 1).
_PERM_CODES = [
    (0, 1, 2),
    (2, 1, 0),
    (0, 2, 1),
    (2, 0, 1),
    (1, 2, 0),
    (1, 0, 2),
]


def expected_value(n_u: int = 3000) -> float:
    """
    Compute the expected second-largest area.

    Key reduction:
      - Sort x-coordinates and write gaps a,b with span s=a+b and ratio t=a/s.
        Then (dx12,dx23,dx13) = (s t, s(1-t), s).
      - Sort y-coordinates similarly with span r and ratio u.
        Each dy is r times one of {u,1-u,1} depending on relative y-permutation.
      - Each rectangle area is (s*r) times a function of (t,u, permutation).
        The median scales linearly, so E[median area] = E[s]*E[r]*E[median of scaled part].
      - For 3 iid uniform points on [0,1], E[span] = 1/2 in one dimension, so E[s]*E[r] = 1/4.
      - For fixed u and permutation, median(t*f12, (1-t)*f23, f13) is piecewise linear in t,
        so integrate it *exactly* over t. This leaves a single integral over u in [0,1].

    We evaluate the remaining 1D integral using Gauss–Legendre quadrature on [0,1].
    """
    # 1D Gauss–Legendre nodes/weights for u in [0,1]
    us, ws = gauss_legendre_01(n_u)

    acc = 0.0
    for u, w in zip(us, ws):
        ou = 1.0 - u

        # Average over the 6 possible relative y-order permutations
        perm_sum = 0.0
        for code12, code23, code13 in _PERM_CODES:
            f12 = u if code12 == 0 else (ou if code12 == 1 else 1.0)
            f23 = u if code23 == 0 else (ou if code23 == 1 else 1.0)
            f13 = u if code13 == 0 else (ou if code13 == 1 else 1.0)

            perm_sum += integral_median_linear(f12, f23, f13)

        avg_over_t_and_perm = perm_sum / 6.0  # t already integrated out, u not yet
        acc += w * avg_over_t_and_perm

    # Multiply by E[s]*E[r] = (1/2)*(1/2) = 1/4
    return 0.25 * acc


def _self_test() -> None:
    # Basic sanity checks for the exact t-integration helper.
    # These are not from the Euler statement (it provides no numeric test cases).
    assert abs(integral_median_linear(1.0, 1.0, 1.0) - 0.75) < 1e-15
    assert abs(integral_median_linear(1.0, 1.0, 0.0) - 0.25) < 1e-15

    # Quadrature weights should sum to 1
    _, w8 = gauss_legendre_01(8)
    assert abs(sum(w8) - 1.0) < 1e-15


def solve() -> None:
    _self_test()
    ans = expected_value(3000)
    print(f"{ans:.10f}")


if __name__ == "__main__":
    solve()
