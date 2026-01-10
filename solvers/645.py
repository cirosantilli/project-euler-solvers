#!/usr/bin/env python3
"""
Project Euler 645: Every Day Is a Holiday

Compute E(10000) rounded to 4 digits after the decimal point.

No external libraries are used.
"""

from __future__ import annotations
import math


# ----------------------------
#  Probability building block
# ----------------------------


def _q_no_adjacent_cycle(D: int, p: float) -> float:
    """
    Probability that a length-D cyclic Bernoulli(p) binary string has no adjacent 1s.

    Using the 2x2 transfer matrix
        A = [[1-p, p],
             [1-p, 0]]
    we have q = trace(A^D) = λ1^D + λ2^D.
    """
    if p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0

    a = 1.0 - p
    disc = math.sqrt(a * (1.0 + 3.0 * p))
    lam1 = (a + disc) * 0.5
    lam2 = (a - disc) * 0.5

    def pow_int(x: float) -> float:
        if x == 0.0:
            return 0.0
        ax = abs(x)
        ln = math.log1p(ax - 1.0) if ax > 0.9 else math.log(ax)
        val = math.exp(D * ln)
        if x < 0.0 and (D & 1):
            val = -val
        return val

    return pow_int(lam1) + pow_int(lam2)


def _integrand(D: int, t: float) -> float:
    """
    Integrand for E[T] in continuous time:
        E[T] = ∫_0^∞ (1 - q(e^{-t})) dt
    """
    p = math.exp(-t)
    return 1.0 - _q_no_adjacent_cycle(D, p)


# ---------------------------------
#  Fast Gauss–Legendre quadrature
# ---------------------------------


def _gauss_legendre_nodes_weights(n: int) -> tuple[list[float], list[float]]:
    """
    Compute Gauss–Legendre nodes and weights for integrating on [-1, 1].

    Standard Newton iteration on roots of P_n.
    For n=64 this is extremely fast and done once.
    """
    nodes = [0.0] * n
    weights = [0.0] * n
    m = (n + 1) // 2

    for i in range(m):
        # Good initial guess
        z = math.cos(math.pi * (i + 0.75) / (n + 0.5))

        # Newton's method
        for _ in range(30):
            p1 = 1.0
            p2 = 0.0
            for j in range(1, n + 1):
                p3 = p2
                p2 = p1
                p1 = ((2 * j - 1) * z * p2 - (j - 1) * p3) / j
            # p1 = P_n(z), p2 = P_{n-1}(z)
            pp = n * (z * p1 - p2) / (z * z - 1.0)  # P'_n(z)
            z1 = z
            z = z1 - p1 / pp
            if abs(z - z1) < 1e-15:
                break

        nodes[i] = -z
        nodes[n - 1 - i] = z
        w = 2.0 / ((1.0 - z * z) * (pp * pp))
        weights[i] = w
        weights[n - 1 - i] = w

    return nodes, weights


# Precompute a high-quality rule once.
_GL_N = 64
_GL_X, _GL_W = _gauss_legendre_nodes_weights(_GL_N)


def _integrate_on_interval(D: int, a: float, b: float) -> float:
    """
    Integrate _integrand(D, t) over [a, b] using 64-point Gauss–Legendre.
    """
    mid = (a + b) * 0.5
    half = (b - a) * 0.5
    s = 0.0
    for x, w in zip(_GL_X, _GL_W):
        s += w * _integrand(D, mid + half * x)
    return half * s


def expected_emperors(D: int) -> float:
    """
    Return E(D): expected number of emperors until every day is a holiday.

    Reduction sketch:
      - Give each day an independent Exp(1) time X_i for the first emperor with that birthday.
      - A day is "not yet picked" by time t with probability p(t)=e^{-t}.
      - After applying the "fill isolated gaps" rule, all days are holidays iff
        there are no adjacent "not yet picked" days (on the D-cycle).
      - Thus P(T <= t) = q_D(e^{-t}), where q_D(p) is 'no adjacent 1s' probability.
      - E[T] = ∫_0^∞ (1 - q_D(e^{-t})) dt and E[#emperors] = D * E[T].

    Numerics:
      - The integrand decays roughly like ~ D*e^{-2t}, so truncating at 25 makes the tail negligible.
      - We use 64-point Gauss–Legendre on a few coarse sub-intervals for high precision and speed.
    """
    if D < 2:
        raise ValueError("D must be >= 2")

    T_MAX = 25.0
    SEGMENTS = 5  # split [0, T_MAX] into 5 equal parts
    step = T_MAX / SEGMENTS

    total = 0.0
    a = 0.0
    for i in range(SEGMENTS):
        b = T_MAX if i == SEGMENTS - 1 else (a + step)
        total += _integrate_on_interval(D, a, b)
        a = b

    return D * total


def solve() -> str:
    ans = expected_emperors(10000)
    return f"{ans:.4f}"


def _self_test() -> None:
    # Test values from the problem statement
    assert abs(expected_emperors(2) - 1.0) < 1e-10
    assert abs(expected_emperors(5) - (31.0 / 6.0)) < 1e-9
    assert (
        abs(expected_emperors(365) - 1174.3501) < 5e-4
    )  # statement gives an approximation


if __name__ == "__main__":
    _self_test()
    print(solve())
