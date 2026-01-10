#!/usr/bin/env python3
"""
Project Euler 683 — The Chase II

We model one round via the relative position (difference modulo k) of the two dice.
Each die moves left/stay/right with probability 1/3 each, independently per turn.
Therefore the relative step Δ has distribution:
    P(Δ=0)=1/3, P(Δ=±1)=2/9, P(Δ=±2)=1/9.

Let T be the number of completed turns until the dice first coincide (difference 0),
starting from a given nonzero difference. The eliminated player pays T^2.
Since the initial difference is uniform on {0,1,...,k-1}, the expected payment in a
round with k players is E[T^2]/k (with T=0 when starting at difference 0).

For k>=3 we compute the first and second moments of T by solving a linear system
on the transient states 1..k-1. The system matrix is (almost) pentadiagonal with
two corner terms due to wrap-around (Δ=±2). We solve it efficiently using:
  * an O(n) pentadiagonal elimination for the non-cyclic part, and
  * a rank-2 Sherman–Morrison–Woodbury update to incorporate the two corners.

Finally, G(n) is the expected pot size, i.e. the sum of expected payments over
rounds with k = 2..n players.
"""

from __future__ import annotations


def _build_pentadiagonal_B(n: int):
    """
    Build the non-cyclic pentadiagonal matrix B for states 1..n (where n=k-1):
        6*x_i -2*(x_{i-1}+x_{i+1}) -(x_{i-2}+x_{i+2}) = rhs_i
    with out-of-range terms omitted (those correspond to the absorbing state 0).
    Returned as five diagonals (sub2, sub1, diag, sup1, sup2).
    """
    sub2 = [0.0] * n  # i-2
    sub1 = [0.0] * n  # i-1
    diag = [6.0] * n
    sup1 = [0.0] * n  # i+1
    sup2 = [0.0] * n  # i+2
    for i in range(n):
        if i - 1 >= 0:
            sub1[i] = -2.0
        if i + 1 < n:
            sup1[i] = -2.0
        if i - 2 >= 0:
            sub2[i] = -1.0
        if i + 2 < n:
            sup2[i] = -1.0
    return sub2, sub1, diag, sup1, sup2


def _factor_pentadiagonal(sub2, sub1, diag, sup1, sup2):
    """
    In-place-like factorization for a pentadiagonal matrix (no corner entries).
    Produces transformed diagonals plus elimination multipliers alpha/beta such
    that multiple RHS can be solved cheaply.
    """
    n = len(diag)
    # copies we will mutate
    sub1 = sub1[:]
    diag = diag[:]
    sup1 = sup1[:]
    sup2 = sup2[:]

    alpha = [0.0] * n  # multiplier for eliminating sub1 on row i using pivot i-1
    beta = [0.0] * n  # multiplier for eliminating sub2 on row i using pivot i-2

    for i in range(n):
        piv = diag[i]
        # eliminate sub1 in row i+1
        if i + 1 < n:
            alpha[i + 1] = sub1[i + 1] / piv
            diag[i + 1] -= alpha[i + 1] * sup1[i]
            if i + 2 < n:
                sup1[i + 1] -= alpha[i + 1] * sup2[i]
        # eliminate sub2 in row i+2
        if i + 2 < n:
            beta[i + 2] = sub2[i + 2] / piv
            sub1[i + 2] -= beta[i + 2] * sup1[i]
            diag[i + 2] -= beta[i + 2] * sup2[i]

    return diag, sup1, sup2, alpha, beta


def _solve_factored(diag, sup1, sup2, alpha, beta, rhs):
    """
    Solve using a factorization returned by _factor_pentadiagonal.
    """
    n = len(diag)
    rhs = rhs[:]  # mutable copy

    # forward elimination on RHS
    for i in range(n):
        if i + 1 < n:
            rhs[i + 1] -= alpha[i + 1] * rhs[i]
        if i + 2 < n:
            rhs[i + 2] -= beta[i + 2] * rhs[i]

    # backward substitution (upper band width 2)
    x = [0.0] * n
    x[n - 1] = rhs[n - 1] / diag[n - 1]
    if n >= 2:
        x[n - 2] = (rhs[n - 2] - sup1[n - 2] * x[n - 1]) / diag[n - 2]
    for i in range(n - 3, -1, -1):
        x[i] = (rhs[i] - sup1[i] * x[i + 1] - sup2[i] * x[i + 2]) / diag[i]
    return x


class _CyclicPentadiagonalSolver:
    """
    Solve A x = rhs where A is like B (pentadiagonal) plus two wrap-around terms:
        A[0, n-1] += -1
        A[n-1, 0] += -1
    This corresponds to the Δ=±2 wrap-around in the modulo-k relative walk.
    """

    def __init__(self, n: int):
        self.n = n

        sub2, sub1, diag, sup1, sup2 = _build_pentadiagonal_B(n)
        self.diag, self.sup1, self.sup2, self.alpha, self.beta = _factor_pentadiagonal(
            sub2, sub1, diag, sup1, sup2
        )

        # Sherman–Morrison–Woodbury with a rank-2 update for the two corners.
        # U = [-e0, -e_{n-1}], V = [e_{n-1}, e0], so A = B + U V^T.
        u1 = [0.0] * n
        u2 = [0.0] * n
        u1[0] = -1.0
        u2[n - 1] = -1.0
        self.z1 = _solve_factored(
            self.diag, self.sup1, self.sup2, self.alpha, self.beta, u1
        )
        self.z2 = _solve_factored(
            self.diag, self.sup1, self.sup2, self.alpha, self.beta, u2
        )

        # M = I + V^T Z is 2x2. Store its inverse explicitly.
        m11 = 1.0 + self.z1[n - 1]
        m12 = self.z2[n - 1]
        m21 = self.z1[0]
        m22 = 1.0 + self.z2[0]
        det = m11 * m22 - m12 * m21
        self.inv00 = m22 / det
        self.inv01 = -m12 / det
        self.inv10 = -m21 / det
        self.inv11 = m11 / det

    def solve(self, rhs):
        y = _solve_factored(self.diag, self.sup1, self.sup2, self.alpha, self.beta, rhs)

        # V^T y = [y[n-1], y[0]]
        b0 = y[self.n - 1]
        b1 = y[0]
        w0 = self.inv00 * b0 + self.inv01 * b1
        w1 = self.inv10 * b0 + self.inv11 * b1

        # x = y - Z w
        x = [0.0] * self.n
        z1 = self.z1
        z2 = self.z2
        for i in range(self.n):
            x[i] = y[i] - z1[i] * w0 - z2[i] * w1
        return x


def expected_payment_one_round(k: int) -> float:
    """
    Expected payment (i.e. E[s^2]) for a single round with k players,
    averaged over the random initial assignment of the two dice.
    """
    if k == 2:
        # k=2 is special because Δ=±2 maps to the same (only) transient state.
        # Equation becomes: 4*E[T] = 9 and 4*E[T^2] = 9 + 18*E[E[T_next]].
        e1 = 9.0 / 4.0
        weighted_e = (5.0 / 9.0) * e1  # stay prob 5/9, absorb prob 4/9
        v1 = (9.0 + 18.0 * weighted_e) / 4.0
        return v1 / k

    n = k - 1
    solver = _CyclicPentadiagonalSolver(n)

    # First moment: A * e = 9
    e = solver.solve([9.0] * n)
    e_full = [0.0] + e  # index 0..k-1 (0 is absorbing)

    # Second moment: A * v = 9 + 18 * E[e_next]
    rhs_v = [0.0] * n
    for i in range(1, k):
        weighted = (
            (1.0 / 3.0) * e_full[i]
            + (2.0 / 9.0) * (e_full[(i - 1) % k] + e_full[(i + 1) % k])
            + (1.0 / 9.0) * (e_full[(i - 2) % k] + e_full[(i + 2) % k])
        )
        rhs_v[i - 1] = 9.0 + 18.0 * weighted

    v = solver.solve(rhs_v)

    # Initial difference is uniform on {0..k-1}; v_0 = 0.
    return sum(v) / k


def G(n: int) -> float:
    """Expected amount the final winner receives (the expected pot size)."""
    total = 0.0
    for k in range(2, n + 1):
        total += expected_payment_one_round(k)
    return total


def sci_9sig(x: float) -> str:
    """
    Scientific notation with 9 significant digits.
    Example: 2.82491788e6 (no leading + or exponent zero padding).
    """
    s = f"{x:.8e}"  # 1 digit before decimal + 8 after => 9 sig digits
    mant, exp = s.split("e")
    return f"{mant}e{int(exp)}"


def _self_test():
    # Test values from the problem statement:
    assert round(G(5), 3) == 96.544
    assert sci_9sig(G(50)) == "2.82491788e6"


def main():
    _self_test()
    print(sci_9sig(G(500)))


if __name__ == "__main__":
    main()
