#!/usr/bin/env python3
"""
Project Euler 682: 5-Smooth Pairs

Compute f(10^7) mod 1_000_000_007.

No external libraries are used.
"""

MOD = 1_000_000_007


def poly_trim(p):
    """Remove trailing zeros (keep at least one coefficient)."""
    while len(p) > 1 and p[-1] == 0:
        p.pop()
    return p


def poly_mul(a, b):
    """Naive polynomial multiplication modulo MOD."""
    if a == [0] or b == [0]:
        return [0]
    res = [0] * (len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    res[i + j] = (res[i + j] + ai * bj) % MOD
    return res


def poly_from_1_minus_xk(k):
    """Return polynomial (1 - x^k)."""
    p = [0] * (k + 1)
    p[0] = 1
    p[k] = MOD - 1
    return p


def negate_odd_coeffs(p):
    """Return p(-x): negate odd-degree coefficients."""
    q = p[:]
    for i in range(1, len(q), 2):
        q[i] = (-q[i]) % MOD
    return q


def even_part(p):
    """Return polynomial consisting of even-degree terms: sum p[2i] x^i."""
    return p[::2] if len(p) > 1 else p[:]


def odd_part(p):
    """Return polynomial consisting of odd-degree terms: sum p[2i+1] x^i."""
    out = p[1::2]
    return out if out else [0]


def bostan_mori(P, Q, n):
    """
    Coefficient extraction: [x^n] P(x)/Q(x) mod MOD, with Q(0) != 0.

    Runs in O(d^2 log n) for degree d polynomials (naive multiply).
    """
    P = P[:]
    Q = Q[:]
    while n > 0:
        Qneg = negate_odd_coeffs(Q)

        P = poly_mul(P, Qneg)
        Q = poly_mul(Q, Qneg)

        if n & 1:
            P = odd_part(P)
        else:
            P = even_part(P)
        Q = even_part(Q)

        poly_trim(P)
        poly_trim(Q)
        n >>= 1

    return P[0] * pow(Q[0], MOD - 2, MOD) % MOD


def build_generating_function_PQ():
    """
    The generating function for f(n) is rational:

        S(x) = sum_k A_k(x)^2

    where A_k(x) is the coefficient of y^k in
        1/((1 - y x^2)(1 - y x^3)(1 - y x^5)).

    By taking a y-constant-term (via residues at y=x^2,x^3,x^5),
    S(x) becomes a sum of 3 simple rational functions, which we
    combine into a single P(x)/Q(x).

    This function constructs P and Q from small factors, avoiding
    hard-coded long coefficient arrays.
    """

    def mul_factors(factors):
        out = [1]
        for f in factors:
            out = poly_mul(out, f)
        return out

    # Denominators from the residue expressions:
    #   D1 = (1-x)(1-x^3)(1-x^4)(1-x^5)(1-x^7)
    #   D2 = (1-x)^2(1+x)(1-x^5)(1-x^6)(1-x^8)
    #   D3 = (1-x)^2(1+x)(x^2+x+1)(1-x^7)(1-x^8)(1-x^10)
    D1 = mul_factors([poly_from_1_minus_xk(k) for k in (1, 3, 4, 5, 7)])
    D2 = mul_factors(
        [[1, MOD - 1], [1, MOD - 1], [1, 1]]  # (1-x)^2(1+x)
        + [poly_from_1_minus_xk(k) for k in (5, 6, 8)]
    )
    D3 = mul_factors(
        [[1, MOD - 1], [1, MOD - 1], [1, 1], [1, 1, 1]]  # (1-x)^2(1+x)(x^2+x+1)
        + [poly_from_1_minus_xk(k) for k in (7, 8, 10)]
    )

    Q = poly_mul(poly_mul(D1, D2), D3)

    # S(x) = 1/D1 - x/D2 + x^5/D3
    Q_over_D1 = poly_mul(D2, D3)
    Q_over_D2 = poly_mul(D1, D3)
    Q_over_D3 = poly_mul(D1, D2)

    P1 = Q_over_D1  #  1 * Q/D1
    P2 = [0] + Q_over_D2  #  x * Q/D2
    P2 = [(-c) % MOD for c in P2]  # -x * Q/D2
    P3 = [0] * 5 + Q_over_D3  #  x^5 * Q/D3

    # P = P1 + P2 + P3
    n = max(len(P1), len(P2), len(P3))
    P = [0] * n
    for i in range(n):
        P[i] = (
            (P1[i] if i < len(P1) else 0)
            + (P2[i] if i < len(P2) else 0)
            + (P3[i] if i < len(P3) else 0)
        ) % MOD

    poly_trim(P)
    poly_trim(Q)
    return P, Q


def f(n):
    """Compute f(n) modulo MOD."""
    P, Q = build_generating_function_PQ()
    return bostan_mori(P, Q, n)


def main():
    # Test values from the problem statement:
    assert f(10) == 4
    assert f(10**2) == 3629

    print(f(10**7))


if __name__ == "__main__":
    main()
