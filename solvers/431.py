#!/usr/bin/env python3
"""
Project Euler 431: Square Space Silo

We model the empty ("wasted") volume above the granular surface inside a
cylindrical silo. The grain surface has constant angle of repose α relative
to the horizontal, so the surface height drop equals tan(α) times the
horizontal distance from the delivery point (apex).

If the silo top is the disk of radius R and the delivery point is offset by
x from the center, then the wasted volume is:

    V(x) = tan(α) * ∬_disk dist((u,v), (x,0)) dudv

Using polar coordinates centered at the delivery point, the disk boundary
gives a radial limit r_max(θ), and the integral reduces to 1D:

    I(x) = ∬ r dudv = (1/3) ∫_0^{2π} r_max(θ)^3 dθ
         = (2/3) ∫_0^{π}  r_max(θ)^3 dθ

where (for 0 ≤ x ≤ R):
    r_max(θ) = -x cos θ + sqrt(R^2 - x^2 sin^2 θ)

We compute the θ-integral with Gauss–Legendre quadrature (no external libs),
then for each integer square n^2 within [V(0), V(R)] we bisection-solve
V(x)=n^2 for x and sum the solutions.
"""

from __future__ import annotations

import math
from typing import Callable, List, Tuple


def gauss_legendre_nodes_weights(n: int) -> Tuple[List[float], List[float]]:
    """
    Returns nodes and weights for n-point Gauss–Legendre quadrature on [-1, 1].
    Computed via Newton's method on Legendre polynomial roots.

    This is a standard implementation:
      - Initial guesses from a cosine formula
      - Recurrence to evaluate P_n(z) and P_{n-1}(z)
      - Closed-form derivative for Newton step
    """
    if n <= 0:
        raise ValueError("n must be positive")

    eps = 1e-15
    m = (n + 1) // 2  # number of positive roots (including 0 if odd)
    xs = [0.0] * n
    ws = [0.0] * n

    for i in range(m):
        # Good initial approximation
        z = math.cos(math.pi * (i + 0.75) / (n + 0.5))

        # Newton iterations
        while True:
            p1 = 1.0  # P_0
            p2 = 0.0  # P_-1
            for k in range(1, n + 1):
                p3 = p2
                p2 = p1
                p1 = ((2 * k - 1) * z * p2 - (k - 1) * p3) / k  # P_k

            # p1 = P_n(z), p2 = P_{n-1}(z)
            # P'_n(z) = n*(z*P_n(z) - P_{n-1}(z)) / (z^2 - 1)
            pp = n * (z * p1 - p2) / (z * z - 1.0)

            z1 = z
            z = z1 - p1 / pp
            if abs(z - z1) < eps:
                break

        # Symmetry
        xs[i] = -z
        xs[n - 1 - i] = z

        w = 2.0 / ((1.0 - z * z) * (pp * pp))
        ws[i] = w
        ws[n - 1 - i] = w

    return xs, ws


class GaussLegendre:
    """Convenience wrapper for fixed-order Gauss–Legendre integration."""

    def __init__(self, n: int, a: float, b: float):
        xs, ws = gauss_legendre_nodes_weights(n)
        mid = (a + b) * 0.5
        half = (b - a) * 0.5
        # Pre-transform nodes to [a,b] to avoid doing it per evaluation
        self.nodes = [mid + half * x for x in xs]
        self.weights = [half * w for w in ws]

    def integrate(self, f: Callable[[float], float]) -> float:
        return sum(w * f(x) for x, w in zip(self.nodes, self.weights))


def wasted_volume(x: float, R: float, alpha_rad: float, quad: GaussLegendre) -> float:
    """
    Computes V(x) for 0 <= x <= R.

    V(x) = tan(alpha) * (2/3) * ∫_0^π r_max(θ)^3 dθ
    """
    t = math.tan(alpha_rad)

    def integrand(theta: float) -> float:
        s = math.sin(theta)
        c = math.cos(theta)
        rad = R * R - (x * s) * (x * s)
        if rad < 0.0:  # guard against tiny negative from floating-point
            rad = 0.0
        rmax = -x * c + math.sqrt(rad)
        return rmax * rmax * rmax

    return t * (2.0 / 3.0) * quad.integrate(integrand)


def solve() -> str:
    # Problem parameters (radius is 6m, angle is 40 degrees)
    R = 6.0
    alpha = math.radians(40.0)

    # Quadrature setup
    quad = GaussLegendre(n=64, a=0.0, b=math.pi)

    # Tests from the problem statement (example silo: diameter 6m => radius 3m, alpha=30°)
    R_ex = 3.0
    alpha_ex = math.radians(30.0)
    quad_ex = quad  # same quadrature interval/order is fine
    assert abs(wasted_volume(0.0, R_ex, alpha_ex, quad_ex) - 32.648388556) < 1e-6
    assert abs(wasted_volume(1.114785284, R_ex, alpha_ex, quad_ex) - 36.0) < 1e-6
    assert abs(wasted_volume(2.511167869, R_ex, alpha_ex, quad_ex) - 49.0) < 1e-6

    v0 = wasted_volume(0.0, R, alpha, quad)
    vR = wasted_volume(R, R, alpha, quad)

    n_min = math.isqrt(int(math.floor(v0)))  # sqrt floor, then adjust upward below
    while (n_min * n_min) < v0 - 1e-12:
        n_min += 1
    n_max = math.isqrt(int(math.floor(vR + 1e-12)))
    while (n_max + 1) * (n_max + 1) <= vR + 1e-12:
        n_max += 1

    total = 0.0

    # Monotone bisection for each square volume
    for n in range(n_min, n_max + 1):
        target = float(n * n)

        lo, hi = 0.0, R
        flo = wasted_volume(lo, R, alpha, quad) - target
        fhi = wasted_volume(hi, R, alpha, quad) - target
        if flo > 0.0 or fhi < 0.0:
            continue  # out of range (shouldn't happen given how n_min/n_max are computed)

        for _ in range(70):  # enough for far beyond 1e-12 on x
            mid = (lo + hi) * 0.5
            fmid = wasted_volume(mid, R, alpha, quad) - target
            if fmid >= 0.0:
                hi = mid
            else:
                lo = mid

        total += (lo + hi) * 0.5

    return f"{total:.9f}"


if __name__ == "__main__":
    print(solve())
