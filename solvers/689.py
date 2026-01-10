#!/usr/bin/env python3
"""
Project Euler 689: Binary Series

We model x ~ Uniform[0, 1). Its binary digits after the point are i.i.d. Bernoulli(1/2)
(except for dyadic rationals, which form a set of measure zero).
So f(x) has the same distribution as S = sum_{i>=1} B_i / i^2.

We compute p(0.5) = P(S > 0.5) using characteristic-function inversion.
No external libraries are used.
"""
from __future__ import annotations

import math
from fractions import Fraction


def binary_digit_after_point(x: Fraction, i: int) -> int:
    """
    Return d_i(x): the i-th digit after the binary point of x in [0,1),
    computed exactly for rational x using integer/rational arithmetic.

    For example, x=1/4 => binary 0.01, so d_2(x)=1 and all other d_i=0.
    """
    if not (0 <= x < 1):
        raise ValueError("x must satisfy 0 <= x < 1")
    if i <= 0:
        raise ValueError("i must be a positive integer")

    y = x
    bit = 0
    for _ in range(i):
        y *= 2
        bit = int(y)  # 0 or 1
        y -= bit
    return bit


def _assert_problem_statement_examples() -> None:
    # From the problem statement:
    # d_2(0.25) = 1, and d_i(0.25) = 0 for i != 2.
    x = Fraction(1, 4)
    assert binary_digit_after_point(x, 2) == 1
    for i in range(1, 40):
        if i != 2:
            assert binary_digit_after_point(x, i) == 0


def _adaptive_simpson(f, a: float, b: float, eps: float) -> float:
    """
    Adaptive Simpson integration (iterative, stack-based) on [a,b].

    Returns an approximation to integral_a^b f(t) dt with absolute error ~ eps.
    """
    fa = f(a)
    fb = f(b)
    m = (a + b) * 0.5
    fm = f(m)
    S = (b - a) * (fa + 4.0 * fm + fb) / 6.0

    # Stack holds (a, b, fa, fm, fb, S, eps_for_interval)
    stack = [(a, b, fa, fm, fb, S, eps)]
    total = 0.0

    # Safety cap: extremely unlikely to hit for this problem if parameters are sane.
    max_iters = 2_000_000
    iters = 0

    while stack:
        a, b, fa, fm, fb, S, eps = stack.pop()
        m = (a + b) * 0.5
        lm = (a + m) * 0.5
        rm = (m + b) * 0.5

        flm = f(lm)
        frm = f(rm)

        S_left = (m - a) * (fa + 4.0 * flm + fm) / 6.0
        S_right = (b - m) * (fm + 4.0 * frm + fb) / 6.0
        S2 = S_left + S_right

        iters += 1
        if iters > max_iters:
            raise RuntimeError("Integration did not converge (too many refinements).")

        if abs(S2 - S) <= 15.0 * eps:
            # Richardson extrapolation
            total += S2 + (S2 - S) / 15.0
        else:
            half = eps * 0.5
            stack.append((m, b, fm, frm, fb, S_right, half))
            stack.append((a, m, fa, flm, fm, S_left, half))

    return total


def solve() -> float:
    """
    Compute p(0.5) = P(S > 0.5), where S = sum_{i>=1} B_i / i^2 and B_i ~ Bernoulli(1/2).

    Using Gil-Pelaez inversion:
      P(S > a) = 1/2 + (1/pi) * ∫_0^∞ Im( e^{-ita} φ(t) / t ) dt

    For this particular S:
      φ(t) = Π_{i>=1} (1 + e^{it/i^2}) / 2
           = exp(it * μ) * Π_{i>=1} cos( t / (2 i^2) )
      where μ = E[S] = (1/2) * Σ_{i>=1} 1/i^2 = π^2/12.

    Since Π cos(·) is real, the integral simplifies to:
      ∫_0^∞ (sin((μ-a)t)/t) * Π_{i>=1} cos(t/(2 i^2)) dt.

    We truncate the infinite product at N and approximate the tail using
    log(cos x) ≈ -x^2/2 for small x.
    """
    a = 0.5
    mu = (math.pi * math.pi) / 12.0
    beta = mu - a  # > 0

    # Truncation for the product Π cos(t/(2 i^2))
    N = 200
    inv2_i2 = [1.0 / (2.0 * i * i) for i in range(1, N + 1)]

    # Tail correction using Σ_{i>N} 1/i^4 = ζ(4) - Σ_{i<=N} 1/i^4
    zeta4 = (math.pi**4) / 90.0
    partial4 = 0.0
    for i in range(1, N + 1):
        ii = float(i)
        partial4 += 1.0 / (ii * ii * ii * ii)
    tail4 = zeta4 - partial4

    cos = math.cos
    sin = math.sin
    exp = math.exp

    def prod_cos(t: float) -> float:
        p = 1.0
        # Multiply the first N terms exactly.
        for c in inv2_i2:
            p *= cos(t * c)
        # Multiply by tail approximation:
        # Π_{i>N} cos(t/(2 i^2)) ≈ exp( -t^2/8 * Σ_{i>N} 1/i^4 )
        return p * exp(-(t * t) * tail4 / 8.0)

    def integrand(t: float) -> float:
        if t == 0.0:
            # lim_{t->0} sin(beta t)/t = beta and prod_cos(0)=1
            return beta
        return (sin(beta * t) / t) * prod_cos(t)

    # Numerically integrate over a finite interval [0, T]; the integrand decays rapidly.
    T = 1200.0
    eps = 1e-12
    I = _adaptive_simpson(integrand, 0.0, T, eps)
    p = 0.5 + I / math.pi
    return p


def main() -> None:
    _assert_problem_statement_examples()
    ans = solve()
    print(f"{ans:.8f}")


if __name__ == "__main__":
    main()
