#!/usr/bin/env python3
"""
Project Euler 449 — Chocolate Covered Candy

We have an ellipsoid of revolution given by:
    b^2 x^2 + b^2 y^2 + a^2 z^2 = a^2 b^2

Divide by a^2 b^2:
    x^2/a^2 + y^2/a^2 + z^2/b^2 = 1

So the semi-axes are:
    equatorial radius (x,y): A = a
    polar radius (z):        C = b

A uniform chocolate coat of thickness t = 1mm means the *outer parallel body*
(K ⊕ tB), i.e. Minkowski sum with a radius-t ball.

For any smooth convex body in 3D, the volume of the outer parallel body is:
    V(t) = V0 + S*t + M*t^2 + (4/3)π*t^3
where
    S = surface area of the body
    M = ∫ H dA  (H is the (average) mean curvature, (κ1+κ2)/2)

Therefore the chocolate volume (shell) is:
    V_choc(t) = V(t) - V0 = S*t + M*t^2 + (4/3)π*t^3

This problem uses t = 1.
"""

from __future__ import annotations
import math


def _safe_atanh_over_x(x: float) -> float:
    """Return atanh(x)/x with a stable series for tiny x."""
    ax = abs(x)
    if ax < 1e-8:
        # atanh(x) = x + x^3/3 + x^5/5 + ...
        x2 = x * x
        return 1.0 + x2 / 3.0 + (x2 * x2) / 5.0
    return math.atanh(x) / x


def _safe_asin_over_x(x: float) -> float:
    """Return asin(x)/x with a stable series for tiny x."""
    ax = abs(x)
    if ax < 1e-8:
        # asin(x) = x + x^3/6 + 3x^5/40 + ...
        x2 = x * x
        return 1.0 + x2 / 6.0 + 3.0 * (x2 * x2) / 40.0
    return math.asin(x) / x


def chocolate_volume(a: float, b: float, t: float = 1.0) -> float:
    """
    Chocolate volume needed to coat the ellipsoid (a,a,b) with thickness t (mm).

    The input parameters (a,b) match the problem statement equation.
    """
    if a <= 0 or b <= 0 or t < 0:
        raise ValueError("a and b must be positive; t must be non-negative")

    pi = math.pi

    # Sphere
    if abs(a - b) < 1e-14:
        S = 4.0 * pi * a * a
        M = 4.0 * pi * a
        return S * t + M * t * t + (4.0 * pi / 3.0) * t**3

    # Use A=equatorial radius, C=polar radius (z-axis)
    A, C = a, b

    if A > C:
        # Oblate spheroid (flattened): equatorial > polar
        e = math.sqrt(1.0 - (C * C) / (A * A))  # eccentricity in [0,1)
        # Surface area (elementary form):
        # S = 2π A^2 * (1 + (1-e^2)/e * atanh(e))
        S = 2.0 * pi * A * A * (1.0 + (C * C / (A * A)) * _safe_atanh_over_x(e))

        # Integrated mean curvature:
        # M = 2π C + (2π A/e) * atan(A e / C)
        # (derived by integrating over the generating curve)
        M = 2.0 * pi * C + (2.0 * pi * A / e) * math.atan((A * e) / C)

    else:
        # Prolate spheroid (elongated): polar > equatorial
        e = math.sqrt(1.0 - (A * A) / (C * C))  # eccentricity in [0,1)
        # Surface area:
        # S = 2π A^2 * (1 + C/(A e) * asin(e))
        S = 2.0 * pi * A * A * (1.0 + (C / A) * _safe_asin_over_x(e))

        # Integrated mean curvature:
        # M = 2π C + (2π A^2/(C e)) * atanh(e)
        M = 2.0 * pi * C + (2.0 * pi * A * A / (C * e)) * math.atanh(e)

    return S * t + M * t * t + (4.0 * pi / 3.0) * t**3


def solve() -> str:
    # Tests from the problem statement
    v11 = chocolate_volume(1.0, 1.0, 1.0)
    assert abs(v11 - (28.0 * math.pi / 3.0)) < 1e-12

    v21 = chocolate_volume(2.0, 1.0, 1.0)
    assert abs(v21 - 60.35475635) < 1e-8

    # Required answer
    ans = chocolate_volume(3.0, 1.0, 1.0)
    return f"{ans:.8f}"


if __name__ == "__main__":
    print(solve())
