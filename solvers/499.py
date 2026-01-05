#!/usr/bin/env python3
"""
Project Euler 499: St. Petersburg Lottery

We compute p_m(s): the probability that the gambler never runs out of money.

Key result used (see README.md for derivation outline):
Let t<0 be the non-zero solution of

    exp(m*t) = sum_{k>=0} exp(2^k * t) / 2^(k+1)

Then for s >= m,

    p_m(s) = 1 - exp( t * (s - m + 1) )

and p_m(s)=0 for s<m.

This file finds t by bracketing + bisection and evaluates the infinite series
with a safe truncation. No external libraries are used.
"""

from __future__ import annotations

import math
from typing import Dict


# Cache roots per m to avoid recomputation in tests.
_T_CACHE: Dict[int, float] = {}


def _f_expm1(t: float, m: int) -> float:
    """
    Stable evaluation of:
        f(t) = exp(m*t) - sum_{k>=0} exp(2^k*t)/2^(k+1)

    We rewrite using expm1 to remove the constant 1:
        f(t) = expm1(m*t) - sum_{k>=0} expm1(2^k*t)/2^(k+1)

    because sum_{k>=0} 1/2^(k+1) = 1.
    """
    # Kahan summation for a bit of extra robustness.
    s = 0.0
    c = 0.0

    pow2 = 1.0
    weight = 0.5  # 1/2^(k+1) for k=0

    # Enough terms: weights decay exponentially; exp(2^k*t) decays super fast for t<0.
    # 200 is a safe upper bound; loop breaks much earlier.
    for _ in range(200):
        term = weight * math.expm1(pow2 * t)
        y = term - c
        tmp = s + y
        c = (tmp - s) - y
        s = tmp

        # Once the weight is far below double precision noise, further terms can't matter.
        if weight < 2.0**-90:
            break

        pow2 *= 2.0
        weight *= 0.5

    return math.expm1(m * t) - s


def _solve_t(m: int) -> float:
    """
    Find the negative non-zero root t<0 of f(t)=0 by bracketing + bisection.
    (t=0 is always a root; we want the other one.)
    """
    if m in _T_CACHE:
        return _T_CACHE[m]

    # Start very close to 0 from below; for all m>=2 this is on the positive side of f(t).
    hi = -1e-12
    f_hi = _f_expm1(hi, m)

    # If this ever fails (shouldn't for this problem), move closer to 0.
    while f_hi <= 0.0:
        hi *= 0.5
        f_hi = _f_expm1(hi, m)

    # Expand left until the sign flips.
    lo = hi
    f_lo = f_hi
    while f_lo > 0.0:
        lo *= 2.0
        f_lo = _f_expm1(lo, m)
        if lo < -100.0:
            raise RuntimeError("Failed to bracket the non-zero negative root.")

    # Bisection. 120 steps gives sub-1e-36 interval width (overkill for our needs).
    for _ in range(120):
        mid = (lo + hi) * 0.5
        f_mid = _f_expm1(mid, m)
        if f_mid > 0.0:
            hi = mid
        else:
            lo = mid

    t = (lo + hi) * 0.5
    _T_CACHE[m] = t
    return t


def p_m_s(m: int, s: int) -> float:
    """Compute p_m(s)."""
    if s < m:
        return 0.0
    t = _solve_t(m)
    # p = 1 - exp(t*(s-m+1)) = -expm1(t*(s-m+1)) (more stable)
    return -math.expm1(t * (s - m + 1))


def main() -> None:
    # Problem statement checks (rounded values given).
    assert p_m_s(2, 1) == 0.0  # given note: p_m(s)=0 for s<m
    assert round(p_m_s(2, 2), 4) == 0.2522
    assert round(p_m_s(2, 5), 4) == 0.6873
    assert round(p_m_s(6, 10_000), 4) == 0.9952

    ans = p_m_s(15, 1_000_000_000)
    print(f"{ans:.7f}")


if __name__ == "__main__":
    main()
