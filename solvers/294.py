#!/usr/bin/env python3
"""
Project Euler 294 — Sum of Digits - Experience #23

S(n) = number of positive integers k < 10^n such that:
  - k ≡ 0 (mod 23)
  - sum of decimal digits of k is 23

We compute S(11^12) mod 10^9.

Key idea:
Digit positions contribute weights 10^pos (mod 23). Since 23 is prime and gcd(10,23)=1,
we have 10^22 ≡ 1 (mod 23), so weights repeat with period 22.
Group digit positions by pos mod 22, then use small truncated generating functions (degree ≤ 23).
"""

from __future__ import annotations

import math
from typing import List, Optional

MOD = 1_000_000_000
BASE = 23
MAX_SUM = 23
DEG = MAX_SUM + 1  # degrees 0..23 inclusive
PERIOD = 22  # since 10^22 ≡ 1 (mod 23)


# A polynomial in x of degree <= 23, whose coefficients are vectors over Z_23 (remainder classes).
# We flatten it as a list of length DEG*BASE, indexed by (deg, rem) -> deg*BASE + rem.
Poly = List[int]


def _poly_one() -> Poly:
    p = [0] * (DEG * BASE)
    p[0 * BASE + 0] = 1
    return p


def _poly_mul(a: Poly, b: Poly, mod: Optional[int]) -> Poly:
    """Multiply two flattened polynomials with cyclic convolution on remainder (mod 23),
    truncating degrees to <= 23.
    """
    res = [0] * (DEG * BASE)

    if mod is None:
        for da in range(DEG):
            ba = da * BASE
            for db in range(DEG - da):
                bb = db * BASE
                br = (da + db) * BASE
                for ra in range(BASE):
                    av = a[ba + ra]
                    if not av:
                        continue
                    for rb in range(BASE):
                        bv = b[bb + rb]
                        if not bv:
                            continue
                        res[br + ((ra + rb) % BASE)] += av * bv
        return res

    m = mod
    for da in range(DEG):
        ba = da * BASE
        for db in range(DEG - da):
            bb = db * BASE
            br = (da + db) * BASE
            for ra in range(BASE):
                av = a[ba + ra]
                if not av:
                    continue
                for rb in range(BASE):
                    bv = b[bb + rb]
                    if not bv:
                        continue
                    idx = br + ((ra + rb) % BASE)
                    res[idx] = (res[idx] + av * bv) % m
    return res


def _make_H(weight: int) -> Poly:
    """H(x) = sum_{d=1..9} x^d * y^{(d*weight mod 23)}  (in the remainder-convolution ring)."""
    h = [0] * (DEG * BASE)
    for d in range(1, 10):
        h[d * BASE + ((d * weight) % BASE)] += 1
    return h


def _pow_1_plus_H_trunc(H: Poly, N: int, mod: Optional[int]) -> Poly:
    """
    Compute (1 + H)^N truncated to degree <= 23.
    Since H has no constant term, we can use the binomial theorem:
      (1 + H)^N = sum_{m=0..23} C(N,m) * H^m
    where higher m terms can't contribute to degrees <= 23.
    """
    one = _poly_one()
    res = [0] * (DEG * BASE)
    res[0] = 1  # m=0 term

    if N == 0:
        return res

    # Precompute H^m for m=1..23 (H^0 = 1).
    Hpows = [one, H]
    for _ in range(2, DEG):
        Hpows.append(_poly_mul(Hpows[-1], H, mod))

    # Accumulate sum_{m=1..23} comb(N,m) * H^m
    if mod is None:
        for m in range(1, DEG):
            c = math.comb(N, m)
            if c == 0:
                continue
            src = Hpows[m]
            for i, v in enumerate(src):
                if v:
                    res[i] += v * c
        return res

    M = mod
    for m in range(1, DEG):
        c = math.comb(N, m) % M
        if c == 0:
            continue
        src = Hpows[m]
        for i, v in enumerate(src):
            if v:
                res[i] = (res[i] + v * c) % M
    return res


def _positions_per_residue(n: int, period: int = PERIOD) -> List[int]:
    """
    For positions 0..n-1, count how many positions have pos ≡ r (mod period).
    """
    q, r = divmod(n, period)
    return [q + (1 if i < r else 0) for i in range(period)]


def S(n: int, mod: Optional[int] = None) -> int:
    """
    Count length-n digit strings (with leading zeros) whose digit sum is 23 and value ≡ 0 (mod 23).
    This equals the problem's S(n) because digit sum 23 implies the number is positive.

    If mod is None, returns the exact integer (safe for the provided test values n=9 and n=42).
    If mod is an integer, returns the result modulo mod.
    """
    if n <= 0:
        return 0

    Ns = _positions_per_residue(n, PERIOD)
    weights = [pow(10, r, BASE) for r in range(PERIOD)]

    # Build per-residue class generating function and raise to Ns[r].
    polys: List[Poly] = []
    for r in range(PERIOD):
        H = _make_H(weights[r])
        polys.append(_pow_1_plus_H_trunc(H, Ns[r], mod))

    # Multiply all residue-class polynomials together.
    acc = _poly_one()
    for p in polys:
        acc = _poly_mul(acc, p, mod)

    return acc[MAX_SUM * BASE + 0] if mod is None else acc[MAX_SUM * BASE + 0] % mod


def solve() -> int:
    # Given checks from the problem statement (exact values).
    assert S(9, None) == 263626
    assert S(42, None) == 6377168878570056

    # Required answer:
    n = 11**12
    return S(n, MOD)


if __name__ == "__main__":
    print(solve())
