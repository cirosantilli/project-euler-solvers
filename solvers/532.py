#!/usr/bin/env python3
"""
Project Euler 532 - Nanobots on Geodesics

We have n bots on the unit sphere, initially on the small circle of Euclidean radius r=0.999
(centered on the z-axis). Each bot chases the next one counterclockwise along the shortest
geodesic, continuously adjusting its heading.

By rotational symmetry, all bots always share the same colatitude θ(t) and are equally spaced
in longitude by Δ = 2π/n. The chase dynamics reduce to a 1D ODE for θ(t), and since all bots
move at equal constant speed, the arc-length drawn by each bot equals the time to reach the
meeting point (the north pole).

The resulting length per bot is:

  L(n) = I(u) / sin(π/n),
  I(u) = ∫_0^r  sqrt(1 - u t^2) / (1 - t^2) dt,
  u = sin^2(π/n), r=0.999.

With substitution t = tanh(y), dt/(1-t^2)=dy and r = tanh(Ymax), so:

  I(u) = ∫_0^{Ymax} sqrt(1 - u tanh^2(y)) dy,  Ymax = atanh(r).

We compute I(u) numerically via adaptive Simpson integration (no external libraries),
and find the minimal n with L(n) > 1000 via monotone binary search.
"""

from __future__ import annotations

import math
from typing import Callable, Dict

RADIUS_SMALL_CIRCLE = 0.999
Y_MAX = 0.5 * math.log(
    (1.0 + RADIUS_SMALL_CIRCLE) / (1.0 - RADIUS_SMALL_CIRCLE)
)  # atanh(r)


def _adaptive_simpson(
    f: Callable[[float], float],
    a: float,
    b: float,
    eps: float,
    fa: float | None = None,
    fb: float | None = None,
    fm: float | None = None,
    depth: int = 0,
    max_depth: int = 30,
) -> float:
    """
    Classic recursive adaptive Simpson integrator.
    Assumes f is smooth on [a,b]. Returns integral with ~absolute error <= eps.
    """
    m = (a + b) * 0.5
    if fa is None:
        fa = f(a)
    if fb is None:
        fb = f(b)
    if fm is None:
        fm = f(m)

    S = (b - a) * (fa + 4.0 * fm + fb) / 6.0

    lm = (a + m) * 0.5
    rm = (m + b) * 0.5
    flm = f(lm)
    frm = f(rm)

    S_left = (m - a) * (fa + 4.0 * flm + fm) / 6.0
    S_right = (b - m) * (fm + 4.0 * frm + fb) / 6.0
    S2 = S_left + S_right

    if depth >= max_depth or abs(S2 - S) <= 15.0 * eps:
        # Richardson extrapolation improves accuracy.
        return S2 + (S2 - S) / 15.0

    return _adaptive_simpson(
        f, a, m, eps * 0.5, fa, fm, flm, depth + 1, max_depth
    ) + _adaptive_simpson(f, m, b, eps * 0.5, fm, fb, frm, depth + 1, max_depth)


_L_CACHE: Dict[int, float] = {}


def length_per_bot(n: int) -> float:
    """Arc-length drawn by each bot for a given n."""
    if n in _L_CACHE:
        return _L_CACHE[n]
    if n < 3:
        raise ValueError("n must be >= 3")

    alpha = math.pi / n
    s = math.sin(alpha)
    u = s * s  # sin^2(pi/n)

    def integrand(y: float) -> float:
        t = math.tanh(y)
        return math.sqrt(1.0 - u * t * t)

    I = _adaptive_simpson(integrand, 0.0, Y_MAX, 1e-12)
    L = I / s
    _L_CACHE[n] = L
    return L


def minimal_n_for_length_over(target: float) -> int:
    """Find the smallest integer n >= 3 such that length_per_bot(n) > target."""
    hi = 3
    while length_per_bot(hi) <= target:
        hi *= 2
    lo = hi // 2

    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if length_per_bot(mid) > target:
            hi = mid
        else:
            lo = mid
    return hi


def solve() -> str:
    n = minimal_n_for_length_over(1000.0)
    total = n * length_per_bot(n)
    return f"{total:.2f}"


def _self_test() -> None:
    # From the problem statement: for n=3 each line is 2.84 (rounded), total is 8.52 (rounded).
    L3 = length_per_bot(3)
    assert round(L3, 2) == 2.84, L3
    assert round(3.0 * L3, 2) == 8.52, 3.0 * L3


if __name__ == "__main__":
    _self_test()
    print(solve())
