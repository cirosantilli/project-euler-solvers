#!/usr/bin/env python3
"""
Project Euler 567 - Reciprocal Games I

This program computes S(123456789) rounded to 8 decimal places.

No external libraries are used (only Python standard library).
"""

from __future__ import annotations

import math


# High-precision Euler–Mascheroni constant (more than enough for double precision)
_EULER_GAMMA = 0.57721566490153286060651209008240243104215933593992


def harmonic(n: int) -> float:
    """
    Return H_n = sum_{k=1..n} 1/k.

    For large n we use the Euler–Maclaurin asymptotic expansion:
      H_n = ln(n) + γ + 1/(2n) - 1/(12n^2) + 1/(120n^4) - 1/(252n^6) + 1/(240n^8) + ...
    """
    if n <= 0:
        return 0.0
    if n < 1_000_000:
        # Exact summation is fine for small n (used by sample asserts).
        return sum(1.0 / k for k in range(1, n + 1))

    x = float(n)
    inv = 1.0 / x
    inv2 = inv * inv
    # Terms quickly become negligible for n ~ 1e8, but keep a few for safety.
    return (
        math.log(x)
        + _EULER_GAMMA
        + 0.5 * inv
        - inv2 / 12.0
        + (inv2 * inv2) / 120.0
        - (inv2 * inv2 * inv2) / 252.0
        + (inv2 * inv2 * inv2 * inv2) / 240.0
    )


def pow2_over_i_sum(m: int) -> float:
    """
    Return sum_{i=1..m} 2^{-i} / i.

    For m >= ~60, the remainder past m is < 2^{-m}/m and is astronomically small,
    so we can safely use the closed form sum_{i>=1} 2^{-i}/i = ln(2).
    """
    if m <= 0:
        return 0.0
    if m <= 60:
        s = 0.0
        for i in range(1, m + 1):
            s += math.ldexp(1.0, -i) / i
        return s
    return math.log(2.0)


def j_a(n: int) -> float:
    """
    Jerry's expected win for Game A, J_A(n).

    Definition:
      J_A(n) = sum_{k=1..n} (1/k) * C(n,k) / 2^n

    For large n we use the identity:
      J_A(n) = sum_{j=0..n-1} 2^{-j} / (n-j) - H_n / 2^n
    and truncate the geometric tail because 2^{-j} decays rapidly.
    """
    if n <= 0:
        return 0.0

    # For small n, compute directly from the definition (safe and simple).
    if n <= 200:
        p = math.ldexp(1.0, -n)  # 2^{-n}
        s = 0.0
        for k in range(1, n + 1):
            s += (math.comb(n, k) * p) / k
        return s

    h = harmonic(n)

    # Fast series: sum_{j=0..∞} 2^{-j}/(n-j), truncated.
    s = 0.0
    J = 80  # 2^{-80} is ~8e-25; plenty for double precision
    for j in range(0, J + 1):
        s += math.ldexp(1.0, -j) / (n - j)

    # Subtract H_n / 2^n (underflows to 0 for huge n, which is fine).
    s -= math.ldexp(h, -n)
    return s


def j_b(n: int) -> float:
    """
    Jerry's expected win for Game B, J_B(n).

    Using C(n,k) = n/k * C(n-1,k-1):
      1/(k*C(n,k)) = 1/(n*C(n-1,k-1))

    So:
      J_B(n) = (1/n) * sum_{j=0..n-1} 1/C(n-1,j)

    For large n, the sum of reciprocal binomials is dominated by edge terms
    (j small and j near n-1). We compute a small number of edge terms and use
    symmetry.
    """
    if n <= 0:
        return 0.0

    # Exact for small n
    if n <= 200:
        s = 0.0
        for k in range(1, n + 1):
            s += 1.0 / (k * math.comb(n, k))
        return s

    N = n - 1
    K = 25  # far more than enough for n ~ 1e8

    inv = 1.0  # 1/C(N,0)
    edge_sum = inv
    for j in range(1, K + 1):
        # Update reciprocal binomial:
        # 1/C(N,j) = 1/C(N,j-1) * j/(N-j+1)
        inv *= j / (N - j + 1)
        edge_sum += inv

    # Symmetry: sum_{j=0..N} 1/C(N,j) ≈ 2*sum_{j=0..K} 1/C(N,j)
    t = 2.0 * edge_sum
    return t / n


def S(m: int) -> float:
    """
    S(m) = sum_{n=1..m} (J_A(n) + J_B(n))

    A key simplification (derived in README):
      S(m) = 4*H_m - 2*sum_{i=1..m} 2^{-i}/i - (J_A(m) + J_B(m))
    """
    if m <= 0:
        return 0.0
    h = harmonic(m)
    p = pow2_over_i_sum(m)
    return 4.0 * h - 2.0 * p - (j_a(m) + j_b(m))


def _run_asserts() -> None:
    # Samples from the problem statement (rounded to 8 decimals there).
    assert f"{j_a(6):.8f}" == "0.39505208"
    assert f"{j_b(6):.8f}" == "0.43333333"
    assert f"{S(6):.8f}" == "7.58932292"


def main() -> None:
    _run_asserts()
    m = 123_456_789
    ans = S(m)
    print(f"{ans:.8f}")


if __name__ == "__main__":
    main()
