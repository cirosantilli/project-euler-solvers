#!/usr/bin/env python3
"""
Project Euler 372: Pencils of Rays

We need R(M, N): the number of integer pairs (x, y) with
    M < x <= N,  M < y <= N
such that floor((y/x)^2) is odd.

This solution uses exact integer arithmetic only (no external libraries).
"""

from __future__ import annotations

import math


def floor_sum(n: int, m: int, a: int, b: int) -> int:
    """
    AtCoder-style floor_sum:
        sum_{i=0}^{n-1} floor((a*i + b) / m)
    Requires n>=0, m>0, a>=0, b>=0.
    """
    res = 0
    while True:
        if a >= m:
            res += (n - 1) * n * (a // m) // 2
            a %= m
        if b >= m:
            res += n * (b // m)
            b %= m
        y_max = a * n + b
        if y_max < m:
            break
        n = y_max // m
        b = y_max % m
        a, m = m, a
    return res


def _floor_surd(a: int, b: int, c: int, k: int) -> int:
    """
    Return floor((a + b*sqrt(k))/c) exactly, where c>0 and k>=0.
    b may be negative.
    """
    # Fast rational cases
    if b == 0 or k == 0:
        return a // c

    bb = -b if b < 0 else b
    # s = floor(|b|*sqrt(k))
    s = math.isqrt(bb * bb * k)

    if b > 0:
        # numerator in [a+s, a+s+1)
        t = (a + s) // c
        u = (t + 1) * c - a
        if u <= 0:
            return t + 1
        if u * u <= bb * bb * k:
            return t + 1
        return t
    else:
        # numerator in (a - s - 1, a - s)
        t = (a - s - 1) // c
        # check if t+1 <= (a - bb*sqrt(k))/c  <=>  a-(t+1)c >= bb*sqrt(k)
        d = a - (t + 1) * c
        if d >= 0 and d * d >= bb * bb * k:
            return t + 1
        return t


def _normalize(a: int, b: int, c: int) -> tuple[int, int, int]:
    """Make c>0 and reduce gcd(|a|,|b|,c)."""
    if c < 0:
        a, b, c = -a, -b, -c
    g = math.gcd(math.gcd(abs(a), abs(b)), c)
    if g > 1:
        a //= g
        b //= g
        c //= g
    return a, b, c


def _reciprocal(a: int, b: int, c: int, k: int) -> tuple[int, int, int]:
    """
    For alpha = (a + b*sqrt(k))/c, return representation (A + B*sqrt(k))/C = 1/alpha.
    """
    # 1/alpha = c/(a + b*sqrt(k)) = c*(a - b*sqrt(k)) / (a^2 - b^2*k)
    A = c * a
    B = -c * b
    C = a * a - b * b * k
    if C < 0:
        A, B, C = -A, -B, -C
    return _normalize(A, B, C)


def sum_floor_mul_surd(a: int, b: int, c: int, k: int, n: int) -> int:
    """
    S = sum_{i=1}^n floor(i * alpha), where alpha = (a + b*sqrt(k))/c and c>0.

    This is computed exactly via Beatty-sequence reciprocity:
      If alpha = q + r with q=floor(alpha), r in [0,1),
         S(alpha,n) = q*n(n+1)/2 + S(r,n)
      For 0<r<1 (irrational),
         S(r,n) = n*m - S(1/r, m), where m=floor(n*r)

    We implement it iteratively using an alternating-sign accumulator.
    """
    if n <= 0:
        return 0

    # Rational fallback (should be rare in this problem, but kept for completeness)
    if b == 0 or k == 0:
        p, q = a, c
        if p >= 0:
            # sum_{i=1}^n floor(i*p/q) = sum_{i=0}^{n-1} floor((p*i + p)/q)
            return floor_sum(n, q, p, p)
        # Negative slope not expected here
        pp = -p
        return -floor_sum(n, q, pp, pp + q - 1)

    aa, bb, cc = a, b, c
    nn = n
    res = 0
    sign = 1  # +1 for add, -1 for subtract

    while nn > 0:
        q_int = _floor_surd(aa, bb, cc, k)
        if q_int:
            res += sign * q_int * nn * (nn + 1) // 2
            aa -= q_int * cc

        if aa == 0 and bb == 0:
            break

        m = _floor_surd(aa * nn, bb * nn, cc, k)  # floor(nn * alpha)
        if m == 0:
            break
        res += sign * nn * m

        aa, bb, cc = _reciprocal(aa, bb, cc, k)
        nn = m
        sign = -sign

    return res


def solve(M: int, N: int) -> int:
    """
    Compute R(M,N): number of (x,y) with M<x<=N and M<y<=N
    such that floor((y/x)^2) is odd.
    """
    L = M + 1
    U = N
    if L > U:
        return 0

    len_side = U - L + 1
    total_pairs = len_side * len_side

    # Maximum possible value of floor((y/x)^2) on the square is attained at (x=L, y=U).
    k_max = (U * U) // (L * L)
    last_odd = k_max if (k_max & 1) else (k_max - 1)

    U2m1 = U * U - 1
    Lm1 = L - 1
    isqrt = math.isqrt

    # P(k) = #{(x,y) in [L,U]^2 : y^2 < k*x^2}
    def P(k: int) -> int:
        # k=1: y^2 < x^2  <=> y < x (since x,y>0)
        if k == 1:
            return len_side * (len_side - 1) // 2

        r = isqrt(k)
        if r * r == k:
            # k is a square: sqrt(k) = r, and strict inequality gives y <= r*x - 1
            s = r
            b = U // s  # last x where r*x <= U  (still not saturated)
            if b < L:
                return total_pairs
            if b > U:
                b = U
            cnt = b - L + 1
            sum_x = (L + b) * cnt // 2
            partial = s * sum_x - L * cnt
            full_cnt = U - b
            return partial + full_cnt * len_side

        # Non-square: y_max = floor(sqrt(k)*x), saturation when sqrt(k)*x >= U
        b = isqrt(
            U2m1 // k
        )  # largest x with k*x^2 <= U^2-1  => floor(sqrt(k)*x) <= U-1
        if b < L:
            return total_pairs
        if b > U:
            b = U
        cnt = b - L + 1

        sum_floor = sum_floor_mul_surd(0, 1, 1, k, b) - sum_floor_mul_surd(
            0, 1, 1, k, Lm1
        )
        partial = sum_floor - (L - 1) * cnt
        full_cnt = U - b
        return partial + full_cnt * len_side

    ans = 0
    for n in range(1, last_odd + 1, 2):
        ans += P(n + 1) - P(n)
    return ans


def main() -> None:
    # Test values from the problem statement
    assert solve(0, 100) == 3019
    assert solve(100, 10_000) == 29_750_422

    print(solve(2_000_000, 1_000_000_000))


if __name__ == "__main__":
    main()
