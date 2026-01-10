#!/usr/bin/env python3
"""
Project Euler 525 - Rolling Ellipse

Compute C(a,b): the length of the curve traced by the center of an ellipse E(a,b)
rolling without slipping along the x-axis for one complete turn.

We use a parameter t that identifies the point on the ellipse boundary that is in
contact with the x-axis (in the ellipse's own, unrotated coordinate system).
"""

import math


def adaptive_simpson(f, a, b, eps=1e-12):
    """Iterative adaptive Simpson integration of f on [a,b]."""

    def simpson(a0, b0, fa, fm, fb):
        return (b0 - a0) * (fa + 4.0 * fm + fb) / 6.0

    fa = f(a)
    fb = f(b)
    m = (a + b) / 2.0
    fm = f(m)
    whole = simpson(a, b, fa, fm, fb)

    total = 0.0
    stack = [(a, b, fa, fm, fb, whole, eps)]

    while stack:
        a1, b1, fa1, fm1, fb1, s1, eps1 = stack.pop()
        m1 = (a1 + b1) / 2.0
        lm = (a1 + m1) / 2.0
        rm = (m1 + b1) / 2.0

        flm = f(lm)
        frm = f(rm)

        left = simpson(a1, m1, fa1, flm, fm1)
        right = simpson(m1, b1, fm1, frm, fb1)

        if abs((left + right) - s1) <= 15.0 * eps1:
            total += left + right + ((left + right) - s1) / 15.0
        else:
            # Split tolerance between sub-intervals
            stack.append((m1, b1, fm1, frm, fb1, right, eps1 / 2.0))
            stack.append((a1, m1, fa1, flm, fm1, left, eps1 / 2.0))

    return total


def center_curve_length(a, b, eps=1e-12):
    """
    Return C(a,b): arc length traced by the ellipse center over one full roll.

    Ellipse in its own coordinates: p(t) = (a cos t, b sin t).

    At contact, the tangent must be horizontal after rotation by angle θ(t).
    This yields:
        θ(t) = atan2(b cos t, a sin t) - π
    and a clean derivative (branch-independent):
        θ'(t) = -ab / (a^2 sin^2 t + b^2 cos^2 t)

    No-slip condition: x-axis translation derivative equals boundary speed:
        s'(t) = |p'(t)| = sqrt(a^2 sin^2 t + b^2 cos^2 t)

    Center position:
        C(t) = (s(t), 0) - R(θ(t)) p(t)
    so:
        C'(t) = (s'(t), 0) - R(θ(t)) (θ'(t) J p(t) + p'(t))
    and C(a,b) = ∫ |C'(t)| dt over t ∈ [t0, t0 + 2π], t0 = -π/2.
    """

    a = float(a)
    b = float(b)
    t0 = -math.pi / 2.0
    t1 = t0 + 2.0 * math.pi

    def speed(t):
        s = math.sin(t)
        c = math.cos(t)

        denom = a * a * s * s + b * b * c * c  # = |p'(t)|^2
        d = math.sqrt(denom)  # s'(t)

        theta = math.atan2(b * c, a * s) - math.pi
        thetap = -a * b / denom

        # p(t)
        px = a * c
        py = b * s

        # J p(t) = (-py, px)
        jx = -py
        jy = px

        # p'(t)
        ppx = -a * s
        ppy = b * c

        # w = θ' J p + p'
        wx = thetap * jx + ppx
        wy = thetap * jy + ppy

        # Rotate w by θ: R(θ) w
        ct = math.cos(theta)
        st = math.sin(theta)
        rwx = wx * ct - wy * st
        rwy = wx * st + wy * ct

        dx = d - rwx
        dy = -rwy
        return math.hypot(dx, dy)

    return adaptive_simpson(speed, t0, t1, eps=eps)


def solve():
    # Test value from the problem statement
    c24 = center_curve_length(2, 4)
    assert abs(c24 - 21.38816906) < 1e-8, c24

    ans = center_curve_length(1, 4) + center_curve_length(3, 4)
    print(f"{ans:.8f}")


if __name__ == "__main__":
    solve()
