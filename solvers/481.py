#!/usr/bin/env python3
"""
Project Euler 481: Chef Showdown

We model the game as a finite stochastic game with perfect information.
Each state is (mask, turn) where:
- mask is a bitmask of remaining chefs
- turn is the index (0-based) of the chef whose turn it is (always present in mask)

On a chef's turn, exactly one dish is cooked:
- with probability (1 - S[i]) nothing happens and the turn advances
- with probability S[i] the chef eliminates one other chef, chosen to maximize
  their own winning probability (ties broken by "next-closest turn")

We compute, for every state, both:
- W[mask][turn][k] = probability chef k eventually wins
- E[mask][turn]    = expected number of remaining dishes cooked

The key trick: for a fixed mask, the "miss" transitions only rotate the turn
around the cyclic order of remaining chefs, yielding a small cyclic linear
system that can be solved in O(m*n) per subset (m = number of chefs in mask).
"""

from __future__ import annotations


def next_chef(i: int, mask: int) -> int:
    """Return the next chef after i in cyclic increasing order within mask."""
    higher = mask & ~((1 << (i + 1)) - 1)  # bits strictly greater than i
    if higher:
        return (higher & -higher).bit_length() - 1
    return (mask & -mask).bit_length() - 1  # wrap to smallest set bit


def solve_game(
    skills: list[float],
) -> tuple[list[list[list[float]]], list[list[float]], int]:
    """
    Solve the game for the given skill probabilities.

    Returns:
        W: list indexed by mask then turn then chef -> win probability
        E: list indexed by mask then turn -> expected remaining dishes
        full_mask: (1<<n)-1
    """
    n = len(skills)
    full_mask = (1 << n) - 1

    # Allocate tables:
    # W[mask][turn] is a length-n vector, E[mask][turn] is a float.
    W = [[[0.0 for _ in range(n)] for _ in range(n)] for _ in range(1 << n)]
    E = [[0.0 for _ in range(n)] for _ in range(1 << n)]

    # Base cases: one chef left -> already winner, no more dishes.
    for i in range(n):
        mask = 1 << i
        W[mask][i][i] = 1.0
        E[mask][i] = 0.0

    # Iterate masks by increasing popcount so smaller masks are known first.
    masks_by_size: list[list[int]] = [[] for _ in range(n + 1)]
    for mask in range(1, 1 << n):
        masks_by_size[mask.bit_count()].append(mask)

    for size in range(2, n + 1):
        for mask in masks_by_size[size]:
            chefs = [i for i in range(n) if (mask >> i) & 1]
            m = len(chefs)
            pos = {
                chef: idx for idx, chef in enumerate(chefs)
            }  # for tie-break distances

            # For each current chef i, decide which chef to eliminate on a favourable rating,
            # based on maximizing i's own future winning probability.
            a = [0.0] * m  # a[t] = 1 - S[chef_t]
            b = [[0.0] * n for _ in range(m)]  # b[t] = S[i] * W_small_vector
            c = [0.0] * m  # c[t] = S[i] * E_small_scalar

            for t, i in enumerate(chefs):
                p = skills[i]
                a[t] = 1.0 - p

                best = -1.0
                tied: list[int] = []

                for j in chefs:
                    if j == i:
                        continue
                    mask2 = mask & ~(1 << j)
                    turn2 = next_chef(i, mask2)
                    val = W[mask2][turn2][i]  # i's chance to win after eliminating j
                    if val > best + 1e-15:
                        best = val
                        tied = [j]
                    elif abs(val - best) <= 1e-15:
                        tied.append(j)

                if len(tied) == 1:
                    jstar = tied[0]
                else:
                    # Tie-break: eliminate the chef whose turn comes next-closest after i
                    # in the CURRENT mask's cyclic order.
                    pi = pos[i]

                    def dist(j: int) -> int:
                        pj = pos[j]
                        d = pj - pi
                        if d <= 0:
                            d += m
                        return d  # in 1..m-1

                    jstar = min(tied, key=dist)

                mask2 = mask & ~(1 << jstar)
                turn2 = next_chef(i, mask2)

                smallW = W[mask2][turn2]
                b[t] = [p * x for x in smallW]
                c[t] = p * E[mask2][turn2]

            # Solve the cyclic linear system for this mask:
            # For each position t in chefs list (sorted), the state where it's chef_t's turn satisfies:
            #   W_t = a_t * W_{t+1} + b_t
            #   E_t = 1 + a_t * E_{t+1} + c_t
            #
            # where t+1 wraps mod m.
            #
            # We compute expressions W_t = A_t * W_0 + B_t, and similarly for E_t, then solve W_0.

            # --- Win probability vectors ---
            A = [0.0] * m  # scalar coefficient for W0
            B = [[0.0] * n for _ in range(m)]  # vector constant

            A_next = 1.0
            B_next = [0.0] * n  # W_0 = 1*W_0 + 0
            for t in range(m - 1, -1, -1):
                A[t] = a[t] * A_next
                Bt = B[t]
                for k in range(n):
                    Bt[k] = a[t] * B_next[k] + b[t][k]
                A_next = A[t]
                B_next = Bt

            denom = 1.0 - A[0]
            W0 = [B[0][k] / denom for k in range(n)]

            # Fill all turns from the expressions.
            for t, chef in enumerate(chefs):
                vec = [A[t] * W0[k] + B[t][k] for k in range(n)]
                W[mask][chef] = vec

            # --- Expected number of dishes ---
            Ae = [0.0] * m
            Be = [0.0] * m
            Ae_next = 1.0
            Be_next = 0.0  # E_0 = 1*E_0 + 0
            for t in range(m - 1, -1, -1):
                Ae[t] = a[t] * Ae_next
                Be[t] = 1.0 + a[t] * Be_next + c[t]
                Ae_next = Ae[t]
                Be_next = Be[t]

            denom_e = 1.0 - Ae[0]
            E0 = Be[0] / denom_e

            for t, chef in enumerate(chefs):
                E[mask][chef] = Ae[t] * E0 + Be[t]

    return W, E, full_mask


def fib_skills(n: int) -> list[float]:
    """Return skills S(k)=F_k/F_{n+1} for chefs k=1..n (0-based list)."""
    fib = [0] * (n + 2)
    fib[1] = fib[2] = 1
    for i in range(3, n + 2):
        fib[i] = fib[i - 1] + fib[i - 2]
    denom = fib[n + 1]
    return [fib[i + 1] / denom for i in range(n)]


def main() -> None:
    # --- Asserts from the problem statement ---

    # Example 1 (custom skills):
    # S(1)=0.25, S(2)=0.5, S(3)=1 => W_3(1)=0.29375
    W3, E3, full3 = solve_game([0.25, 0.5, 1.0])
    assert abs(W3[full3][0][0] - 0.29375) < 1e-12

    # Example 2 (Fibonacci skills, n=7) win probabilities and expected dishes:
    W7, E7, full7 = solve_game(fib_skills(7))
    expected_W7 = [
        "0.08965042",
        "0.20775702",
        "0.15291406",
        "0.14554098",
        "0.15905291",
        "0.10261412",
        "0.14247050",
    ]
    for k, s in enumerate(expected_W7):
        assert f"{W7[full7][0][k]:.8f}" == s
    assert f"{E7[full7][0]:.8f}" == "42.28176050"

    # --- Problem target: E(14) with Fibonacci skills ---
    W14, E14, full14 = solve_game(fib_skills(14))
    ans = E14[full14][0]
    print(f"{ans:.8f}")


if __name__ == "__main__":
    main()
