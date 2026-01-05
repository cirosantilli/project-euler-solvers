#!/usr/bin/env python3
"""Project Euler 227: The Chase

We compute the expected number of turns until the game ends.

Game (N even):
- N players sit around a circle.
- Initially two opposite players each hold one die.
- Each turn, the two holders roll their die:
  * roll 1  -> pass the die to the neighbour on the left
  * roll 6  -> pass the die to the neighbour on the right
  * otherwise keep the die
- After the dice have been rolled and passed, if one player holds both dice,
  the game ends.

State reduction:
Only the *relative distance* between the two dice matters. Let d be the clockwise
distance (mod N) from die A to die B, so d in {0,1,...,N-1}. The game ends when d=0.

Each die moves by -1, 0, +1 with probabilities 1/6, 4/6, 1/6.
The relative displacement Δ = move_B - move_A therefore has distribution:
  Δ = -2 : 1/36
  Δ = -1 : 2/9
  Δ =  0 : 1/2
  Δ = +1 : 2/9
  Δ = +2 : 1/36
and d' = (d + Δ) mod N.

We solve the linear system for expected hitting times of state 0:
  E[0] = 0
  E[d] = 1 + Σ_{Δ} p(Δ) * E[(d+Δ) mod N]     for d != 0

This is an absorbing Markov chain; for N=100 the system is only 99x99.
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, localcontext
from typing import List


def _gaussian_elimination_solve(
    A: List[List[Decimal]], b: List[Decimal]
) -> List[Decimal]:
    """Solve A x = b using Gaussian elimination with partial pivoting."""

    n = len(A)
    if n == 0:
        return []
    if any(len(row) != n for row in A):
        raise ValueError("Matrix A must be square")
    if len(b) != n:
        raise ValueError("Dimension mismatch between A and b")

    # Augmented matrix
    M = [A[i][:] + [b[i]] for i in range(n)]

    for col in range(n):
        # Pivot: row with max |value| in this column
        pivot = max(range(col, n), key=lambda r: abs(M[r][col]))
        if M[pivot][col] == 0:
            raise ValueError("Singular matrix")
        if pivot != col:
            M[col], M[pivot] = M[pivot], M[col]

        pivot_val = M[col][col]
        # Normalize pivot row
        for c in range(col, n + 1):
            M[col][c] /= pivot_val

        # Eliminate below
        for r in range(col + 1, n):
            factor = M[r][col]
            if factor == 0:
                continue
            for c in range(col, n + 1):
                M[r][c] -= factor * M[col][c]

    # Back substitution
    x = [Decimal(0)] * n
    for i in range(n - 1, -1, -1):
        s = M[i][n]
        for j in range(i + 1, n):
            s -= M[i][j] * x[j]
        x[i] = s

    return x


def expected_turns(num_players: int, *, precision: int = 80) -> Decimal:
    """Return the expected number of turns for the game with `num_players` players."""

    if num_players < 2 or num_players % 2 != 0:
        raise ValueError("Number of players must be an even integer >= 2")

    with localcontext() as ctx:
        ctx.prec = precision

        D = Decimal
        N = num_players

        # Relative displacement probabilities
        probs = {
            -2: D(1) / D(36),
            -1: D(2) / D(9),
            0: D(1) / D(2),
            1: D(2) / D(9),
            2: D(1) / D(36),
        }

        # Unknowns are E[1], E[2], ..., E[N-1]
        n_unknowns = N - 1
        A = [[D(0)] * n_unknowns for _ in range(n_unknowns)]
        b = [D(1)] * n_unknowns

        def idx(d: int) -> int:
            # d in 1..N-1
            return d - 1

        for d in range(1, N):
            r = idx(d)
            A[r][r] = D(1)
            for delta, p in probs.items():
                d2 = (d + delta) % N
                if d2 == 0:
                    continue  # E[0] = 0
                A[r][idx(d2)] -= p

        sol = _gaussian_elimination_solve(A, b)
        return sol[idx(N // 2)]


def format_significant(x: Decimal, sig: int = 10) -> str:
    """Format Decimal `x` rounded to `sig` significant digits, without scientific notation."""

    if x.is_zero():
        return "0"

    # x.adjusted() is floor(log10(|x|))
    exp = x.copy_abs().adjusted()
    quant_exp = exp - sig + 1  # power of 10 to keep
    step = Decimal(1).scaleb(quant_exp)
    rounded = x.quantize(step, rounding=ROUND_HALF_UP)
    return format(rounded, "f")


def solve() -> str:
    ans = expected_turns(100, precision=80)
    return format_significant(ans, 10)


def _self_test() -> None:
    # A tiny analytic sanity check:
    # For N=2, the dice meet (one player holds both) with probability 4/9 each turn,
    # so E = 1 / (4/9) = 9/4 = 2.25.
    val2 = expected_turns(2, precision=60)
    assert val2.quantize(Decimal("0.01")) == Decimal("2.25")

    # The required Project Euler answer for N=100, rounded to ten significant digits.


if __name__ == "__main__":
    _self_test()
    print(solve())
