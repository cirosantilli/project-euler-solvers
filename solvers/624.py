#!/usr/bin/env python3
"""
Project Euler 624: Two Heads Are Better Than One

We toss an unbiased coin until the first occurrence of two consecutive heads (HH).
Let M be the index of the second H in that first HH. P(n) is the probability that n | M.

We compute Q(P(10^18), 1_000_000_009), where for a reduced fraction a/b and prime p,
Q(a/b, p) is the smallest positive q such that a ≡ b*q (mod p).
Equivalently, q ≡ (a * b^{-1}) (mod p), mapped into {1,2,...,p} (with 0 -> p).

No external libraries are used (only Python standard library).
"""

from __future__ import annotations

from fractions import Fraction
from typing import List, Optional, Tuple


Matrix2 = List[List[int]]


def mat_mul(a: Matrix2, b: Matrix2, mod: Optional[int] = None) -> Matrix2:
    """Multiply 2x2 matrices."""
    if mod is None:
        return [
            [
                a[0][0] * b[0][0] + a[0][1] * b[1][0],
                a[0][0] * b[0][1] + a[0][1] * b[1][1],
            ],
            [
                a[1][0] * b[0][0] + a[1][1] * b[1][0],
                a[1][0] * b[0][1] + a[1][1] * b[1][1],
            ],
        ]
    return [
        [
            (a[0][0] * b[0][0] + a[0][1] * b[1][0]) % mod,
            (a[0][0] * b[0][1] + a[0][1] * b[1][1]) % mod,
        ],
        [
            (a[1][0] * b[0][0] + a[1][1] * b[1][0]) % mod,
            (a[1][0] * b[0][1] + a[1][1] * b[1][1]) % mod,
        ],
    ]


def mat_pow(mat: Matrix2, exp: int, mod: Optional[int] = None) -> Matrix2:
    """Fast exponentiation for 2x2 matrices."""
    res: Matrix2 = [[1, 0], [0, 1]]
    base: Matrix2 = [mat[0][:], mat[1][:]]
    e = exp
    while e > 0:
        if e & 1:
            res = mat_mul(res, base, mod)
        base = mat_mul(base, base, mod)
        e >>= 1
    return res


def mat_scalar_mul(mat: Matrix2, s: int, mod: int) -> Matrix2:
    """Multiply a 2x2 matrix by a scalar modulo mod."""
    return [
        [(mat[0][0] * s) % mod, (mat[0][1] * s) % mod],
        [(mat[1][0] * s) % mod, (mat[1][1] * s) % mod],
    ]


def mat_vec_mul(mat: Matrix2, v: Tuple[int, int], mod: int) -> Tuple[int, int]:
    """Multiply 2x2 matrix by a length-2 vector modulo mod."""
    return (
        (mat[0][0] * v[0] + mat[0][1] * v[1]) % mod,
        (mat[1][0] * v[0] + mat[1][1] * v[1]) % mod,
    )


def inv_2x2(mat: Matrix2, mod: int) -> Matrix2:
    """Inverse of a 2x2 matrix modulo a prime mod."""
    a, b = mat[0]
    c, d = mat[1]
    det = (a * d - b * c) % mod
    inv_det = pow(det, mod - 2, mod)  # mod is prime in this problem
    return [
        [(d * inv_det) % mod, ((-b) % mod * inv_det) % mod],
        [((-c) % mod * inv_det) % mod, (a * inv_det) % mod],
    ]


# Fibonacci Q-matrix
A: Matrix2 = [[1, 1], [1, 0]]


def P_fraction(n: int) -> Fraction:
    """
    Exact rational P(n) for small n using Fraction arithmetic.

    Derivation yields:
      P(n) = e2^T * (B/2^n) * (I - B/2^n)^(-1) * v
    where B = A^n, e2=[0,1], v=[0,1].
    """
    if n < 1 or n > 60:
        # Safety guard: exact Fractions would explode for huge n.
        raise ValueError("P_fraction is intended only for small n (e.g., test values).")

    B = mat_pow(A, n, mod=None)  # integer matrix
    s = Fraction(1, 2**n)  # 2^{-n}
    # M = s * B in rationals
    M = [
        [Fraction(B[0][0]) * s, Fraction(B[0][1]) * s],
        [Fraction(B[1][0]) * s, Fraction(B[1][1]) * s],
    ]
    # Compute (I - M)^{-1} via 2x2 inverse in Fractions
    I_minus_M = [
        [Fraction(1) - M[0][0], -M[0][1]],
        [-M[1][0], Fraction(1) - M[1][1]],
    ]
    a, b = I_minus_M[0]
    c, d = I_minus_M[1]
    det = a * d - b * c
    inv = [
        [d / det, -b / det],
        [-c / det, a / det],
    ]
    # v = [0,1]
    w0 = inv[0][1]
    w1 = inv[1][1]
    # x = M * w
    x1 = M[1][0] * w0 + M[1][1] * w1
    return x1


def Q_of_P(n: int, p: int) -> int:
    """
    Compute Q(P(n), p) for prime p, i.e. P(n) reduced fraction a/b mapped to q:
        a ≡ b*q (mod p), smallest positive q.

    We compute P(n) directly in F_p using a matrix geometric-series trick.
    """
    if p <= 2:
        raise ValueError("p must be an odd prime")

    # B = A^n (mod p)
    B = mat_pow(A, n, mod=p)

    # s = 2^{-n} (mod p)
    inv2 = (p + 1) // 2  # inverse of 2 mod an odd prime
    s = pow(inv2, n, p)

    # M = s * B
    M = mat_scalar_mul(B, s, mod=p)

    # Sum_{k>=1} M^k = M * (I - M)^{-1}
    I_minus_M = [
        [(1 - M[0][0]) % p, (-M[0][1]) % p],
        [(-M[1][0]) % p, (1 - M[1][1]) % p],
    ]
    inv_I = inv_2x2(I_minus_M, p)

    # Multiply by v = [0,1]
    w = mat_vec_mul(inv_I, (0, 1), p)

    # x = M * w
    x = mat_vec_mul(M, w, p)

    q = x[1] % p  # e2^T * x, where e2 = [0,1]
    return p if q == 0 else q


def main() -> None:
    # Asserts from the problem statement
    assert P_fraction(2) == Fraction(3, 5)
    assert P_fraction(3) == Fraction(9, 31)
    assert Q_of_P(2, 109) == 66
    assert Q_of_P(3, 109) == 46

    # Required output
    n = 10**18
    p = 1_000_000_009
    print(Q_of_P(n, p))


if __name__ == "__main__":
    main()
