#!/usr/bin/env python3
"""
Project Euler 450: Hypocycloid and Lattice Points

No external libraries are used.

We compute:
T(N) = sum_{R=3..N} sum_{r=1..floor((R-1)/2)} S(R,r)
where S(R,r) is the sum of |x|+|y| over distinct integer-coordinate points
on the hypocycloid that occur at parameter values with rational sin(t), cos(t).
"""
from __future__ import annotations

import math
import sys
from math import gcd


# ----------------------------
# Möbius sieve + prefix sums
# ----------------------------

def mobius_sieve(n: int) -> list[int]:
    """Linear sieve for Möbius μ(1..n)."""
    mu = [0] * (n + 1)
    mu[1] = 1
    primes: list[int] = []
    is_comp = [False] * (n + 1)
    for i in range(2, n + 1):
        if not is_comp[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            ip = i * p
            if ip > n:
                break
            is_comp[ip] = True
            if i % p == 0:
                mu[ip] = 0
                break
            mu[ip] = -mu[i]
    return mu


def build_prefix(mu: list[int]) -> tuple[list[int], list[int], list[int], list[int]]:
    """
    Build prefix sums:
      pref_mu[i]      = Σ_{k<=i} μ(k)
      pref_mui[i]     = Σ_{k<=i} μ(k)*k
      pref_mu_odd[i]  = Σ_{k<=i, k odd} μ(k)
      pref_mui_odd[i] = Σ_{k<=i, k odd} μ(k)*k
    """
    n = len(mu) - 1
    pref_mu = [0] * (n + 1)
    pref_mui = [0] * (n + 1)
    pref_mu_odd = [0] * (n + 1)
    pref_mui_odd = [0] * (n + 1)

    s0 = s1 = so0 = so1 = 0
    for i in range(1, n + 1):
        mi = mu[i]
        s0 += mi
        s1 += mi * i
        if i & 1:
            so0 += mi
            so1 += mi * i
        pref_mu[i] = s0
        pref_mui[i] = s1
        pref_mu_odd[i] = so0
        pref_mui_odd[i] = so1
    return pref_mu, pref_mui, pref_mu_odd, pref_mui_odd


# ----------------------------
# Region sums (no gcd filter)
# R(n) = {(a,b): 1<=b<a and a+b<=n}
# ----------------------------

def G0(n: int) -> int:
    """count of pairs in R(n)."""
    if n <= 2:
        return 0
    m = (n - 1) // 2
    return m * (n - m - 1)


def GA(n: int) -> int:
    """sum of a over pairs in R(n)."""
    c = G0(n)
    return (n + 1) * c // 2


def GB(n: int) -> int:
    """sum of b over pairs in R(n)."""
    if n <= 2:
        return 0
    m = (n - 1) // 2
    term = m * (m + 1)
    # term * (3n - 4m - 2) / 6
    return term * (3 * n - 4 * m - 2) // 6


def HB(n: int) -> int:
    """
    Sum of b over pairs in R(n) with a and b both odd.
    """
    # write a=2x+1, b=2y+1, x>y>=0, x+y <= floor((n-2)/2)
    M = (n - 2) // 2
    if M <= 0:
        return 0
    m0 = (M - 1) // 2
    if m0 < 0:
        return 0
    s_y = m0 * (m0 + 1) // 2
    s_y2 = m0 * (m0 + 1) * (2 * m0 + 1) // 6
    # Σ (2y+1)(M-2y) = M(m0+1)^2 - 4Σy^2 - 2Σy
    return M * (m0 + 1) * (m0 + 1) - 4 * s_y2 - 2 * s_y


def KB(n: int) -> int:
    """
    Sum of b over pairs in R(n) with a ≡ b (mod 4).
    """
    res = 0

    # b=4y+1, a=4x+1, x>y>=0, x+y <= floor((n-2)/4)
    M1 = (n - 2) // 4
    if M1 > 0:
        m1 = (M1 - 1) // 2
        if m1 >= 0:
            s_y = m1 * (m1 + 1) // 2
            s_y2 = m1 * (m1 + 1) * (2 * m1 + 1) // 6
            # Σ (4y+1)(M1-2y) = M1 Σ(4y+1) - 8Σy^2 - 2Σy
            sum_4y1 = (m1 + 1) * (2 * m1 + 1)  # Σ(4y+1)
            res += M1 * sum_4y1 - 8 * s_y2 - 2 * s_y

    # b=4y+3, a=4x+3, x>y>=0, x+y <= floor((n-6)/4)
    M3 = (n - 6) // 4
    if M3 > 0:
        m3 = (M3 - 1) // 2
        if m3 >= 0:
            s_y = m3 * (m3 + 1) // 2
            s_y2 = m3 * (m3 + 1) * (2 * m3 + 1) // 6
            sum_4y3 = (m3 + 1) * (2 * m3 + 3)  # Σ(4y+3)
            res += M3 * sum_4y3 - 8 * s_y2 - 6 * s_y

    return res


# ----------------------------
# Möbius-blocked sums
# ----------------------------

def mobius_sum_weighted(m: int, pref_mui: list[int], base_func) -> int:
    """
    Compute Σ_{d=1..m} μ(d)*d*base_func( floor(m/d) )
    with the standard floor-division blocking trick.
    """
    res = 0
    l = 1
    while l <= m:
        q = m // l
        r = m // q
        res += (pref_mui[r] - pref_mui[l - 1]) * base_func(q)
        l = r + 1
    return res


# ----------------------------
# Axis-aligned contribution (c=1)
# ----------------------------

class AxisCalculator:
    """
    Computes f(M) = Σ_{coprime a>b, a+b<=M} g(a,b)
    where g(a,b) corresponds to the c=1 (axis-aligned) points, and then
    T_axis(N) = Σ_{d>=1} d * f( floor(N/d) ).
    """

    def __init__(self, n: int) -> None:
        mu = mobius_sieve(n)
        _, pref_mui, _, pref_mui_odd = build_prefix(mu)
        self.pref_mui = pref_mui
        self.pref_mui_odd = pref_mui_odd
        self.cache: dict[int, int] = {}

    def f(self, m: int) -> int:
        """
        f(m) = 4*Σ a + 2*Σ b + 2*Σ_{a,b odd} b - 4*Σ_{a≡b mod4} b
        over coprime pairs (a>b, a+b<=m).
        """
        if m in self.cache:
            return self.cache[m]
        SA = mobius_sum_weighted(m, self.pref_mui, GA)
        SB = mobius_sum_weighted(m, self.pref_mui, GB)
        P2 = mobius_sum_weighted(m, self.pref_mui_odd, HB)
        P4 = mobius_sum_weighted(m, self.pref_mui_odd, KB)
        val = 4 * SA + 2 * SB + 2 * P2 - 4 * P4
        self.cache[m] = val
        return val

    def total(self, n: int) -> int:
        total = 0
        l = 1
        while l <= n:
            q = n // l
            r = n // q
            # Σ_{d=l..r} d
            sum_d = (l + r) * (r - l + 1) // 2
            total += sum_d * self.f(q)
            l = r + 1
        return total


# ----------------------------
# Non-axis contribution (c>1)
# ----------------------------

def primitive_triples(cmax: int) -> list[tuple[int, int, int]]:
    """
    All primitive Pythagorean triples (a,b,c) with c odd, c<=cmax, a>0,b>0.
    Generated via Euclid's formula.
    """
    triples: list[tuple[int, int, int]] = []
    m_limit = int(math.isqrt(cmax * 2)) + 3
    for m in range(2, m_limit + 1):
        mm = m * m
        for n in range(1, m):
            if ((m - n) & 1) == 0:
                continue
            if gcd(m, n) != 1:
                continue
            c = mm + n * n
            if c > cmax:
                break
            a = mm - n * n
            b = 2 * m * n
            triples.append((a, b, c))
    return triples


def gauss_pow(re: int, im: int, exp: int) -> tuple[int, int]:
    """
    (re + i im)^exp as a Gaussian integer (Re, Im), via fast exponentiation.
    """
    rr, ri = 1, 0
    br, bi = re, im
    e = exp
    while e > 0:
        if e & 1:
            rr, ri = rr * br - ri * bi, rr * bi + ri * br
        br, bi = br * br - bi * bi, br * bi + bi * br
        e //= 2
    return rr, ri


def non_axis_total(n: int) -> int:
    total = 0

    # max A' such that 3^A' <= n
    maxA = 1
    while pow(3, maxA + 1) <= n:
        maxA += 1

    for Ap in range(2, maxA + 1):
        # conservative integer root for c_max with c^Ap <= n
        cmax = int(n ** (1.0 / Ap)) + 2
        while pow(cmax, Ap) > n:
            cmax -= 1
        triples = primitive_triples(cmax)

        for Bp in range(1, Ap):
            if gcd(Ap, Bp) != 1:
                continue

            for a, b, c in triples:
                den = pow(c, Ap)
                if den * (Ap + Bp) > n:
                    continue

                # Consider all sign variants and the swapped (b,a)
                variants: set[tuple[int, int]] = set()
                for u, v in ((a, b), (b, a)):
                    for su in (1, -1):
                        for sv in (1, -1):
                            variants.add((su * u, sv * v))

                for re, im in variants:
                    uA, vA = gauss_pow(re, im, Ap)
                    uB, vB = gauss_pow(re, im, Bp)
                    scale = pow(c, Ap - Bp)

                    numX = Ap * uB * scale + Bp * uA
                    numY = Ap * vB * scale - Bp * vA

                    g = gcd(den, gcd(abs(numX), abs(numY)))
                    d0 = den // g
                    if d0 * (Ap + Bp) > n:
                        continue

                    x0 = numX // g
                    y0 = numY // g

                    kmax = n // (d0 * (Ap + Bp))
                    total += (abs(x0) + abs(y0)) * (kmax * (kmax + 1) // 2)

    return total


# ----------------------------
# Full T(N)
# ----------------------------

def T(n: int) -> int:
    axis = AxisCalculator(n).total(n)
    return axis + non_axis_total(n)


# ----------------------------
# Helpers for problem-statement assertions
# ----------------------------

def _i_pow(k: int) -> tuple[int, int]:
    """i^k for integer k as (Re, Im)."""
    k &= 3
    if k == 0:
        return (1, 0)
    if k == 1:
        return (0, 1)
    if k == 2:
        return (-1, 0)
    return (0, -1)


def C_points(R: int, r: int) -> set[tuple[int, int]]:
    """
    Enumerate C(R,r) (distinct lattice points meeting the rational sin/cos condition),
    intended only for small/medium R,r and for verifying the problem statement examples.
    """
    A = R - r
    B = r
    d = gcd(A, B)
    Ap = A // d
    Bp = B // d

    pts: set[tuple[int, int]] = set()

    # c=1 / axis-aligned angles t0 ∈ {0, π/2, π, 3π/2}
    pts.add((d * (Ap + Bp), 0))  # t0=0
    pts.add((d * (Ap * ((-1) ** Bp) + Bp * ((-1) ** Ap)), 0))  # t0=π

    reB, imB = _i_pow(Bp)
    reA, imA = _i_pow(Ap)
    pts.add((d * (Ap * reB + Bp * reA), d * (Ap * imB - Bp * imA)))  # t0=π/2

    reB, imB = _i_pow(3 * Bp)
    reA, imA = _i_pow(3 * Ap)
    pts.add((d * (Ap * reB + Bp * reA), d * (Ap * imB - Bp * imA)))  # t0=3π/2

    # c>1 solutions: brute over triples with c<=1000 (enough for the given examples)
    for a, b, c in primitive_triples(1000):
        den = pow(c, Ap)
        if den == 1:
            continue

        variants: set[tuple[int, int]] = set()
        for u, v in ((a, b), (b, a)):
            for su in (1, -1):
                for sv in (1, -1):
                    variants.add((su * u, sv * v))

        for re, im in variants:
            uA, vA = gauss_pow(re, im, Ap)
            uB, vB = gauss_pow(re, im, Bp)
            scale = pow(c, Ap - Bp)

            numX = Ap * uB * scale + Bp * uA
            numY = Ap * vB * scale - Bp * vA

            g = gcd(den, gcd(abs(numX), abs(numY)))
            d0 = den // g
            if d0 == 0:
                continue
            if d % d0 != 0:
                continue

            k = d // d0
            x = k * (numX // g)
            y = k * (numY // g)
            pts.add((x, y))

    return pts


def S_value(R: int, r: int) -> int:
    return sum(abs(x) + abs(y) for (x, y) in C_points(R, r))


# ----------------------------
# Main / tests
# ----------------------------

def main() -> None:
    # Problem statement asserts
    assert C_points(3, 1) == {(3, 0), (-1, 2), (-1, 0), (-1, -2)}
    assert C_points(2500, 1000) == {
        (2500, 0),
        (772, 2376),
        (772, -2376),
        (516, 1792),
        (516, -1792),
        (500, 0),
        (68, 504),
        (68, -504),
        (-1356, 1088),
        (-1356, -1088),
        (-1500, 1000),
        (-1500, -1000),
    }
    assert S_value(3, 1) == 10

    assert T(3) == 10
    assert T(10) == 524
    assert T(100) == 580442
    assert T(10**3) == 583108600

    # Required output
    n = 10**6
    print(T(n))


if __name__ == "__main__":
    main()
