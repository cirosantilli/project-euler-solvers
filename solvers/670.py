#!/usr/bin/env python3
"""Project Euler 670: Colouring a Strip

We tile a 2×n rectangle with tiles of size 1×1, 1×2, 1×3 (horizontal), and the
2×1 vertical domino (rotation of the 1×2 tile), in four colours.

Rules:
  1) Full cover, no overlap.
  2) No four tiles may have their corners meeting at a single interior point.
     In a 2×n grid this forbids a boundary between columns where:
       - both rows have a tile boundary there (i.e. neither row has a tile spanning
         across the boundary),
       - and neither of the two columns adjacent to the boundary is a vertical domino.
  3) Adjacent tiles (sharing an edge of positive length) must have different colours.

Let F(n) be the number of valid coloured tilings. We need F(10^16) modulo 1_000_004_321.

Solution outline:
  - Process the strip column-by-column.
  - A boundary state keeps only what can affect the future:
      * for each row, whether the current cell is already occupied by a horizontal tile
        coming from the left, and if so whether it continues further (only possible for
        the middle cell of a length-3 tile), plus that tile's colour;
      * if the cell is not pre-occupied, we store the colour of the tile to its left
        (needed because the next tile must differ);
      * whether the previous column was a vertical domino (needed only for the
        no-4-corners rule).
  - Enumerate all reachable states with BFS, build the transfer matrix T.
  - Compute the required huge n using fast matrix exponentiation and apply it to the
    initial state vector.

No external libraries are used.
"""

from __future__ import annotations

MOD = 1_000_004_321
COLORS = 4
NONE = 4  # sentinel for "no left neighbour colour" at the very left edge


# State encoding (tuple of ints):
#   (v_prev,
#    inT, contT, valT,
#    inB, contB, valB)
#
# For each row (T=top, B=bottom):
#   - in? = 1 if the current cell is occupied by a horizontal tile coming from the left.
#   - cont? = meaningful only if in?=1. 1 means this incoming tile continues to next column
#             as well (only possible for the middle cell of a length-3 tile started one
#             column earlier). Otherwise 0.
#   - val? = if in?=1: the colour (0..3) of the incoming tile.
#            if in?=0: the colour (0..3) of the tile immediately to the left in that row,
#                      or NONE at the very left edge.
#
# v_prev is 1 iff the previous column was a vertical domino. For i=0 we use v_prev=1 as a
# harmless sentinel so the corner-rule doesn't constrain the first column.


def _transitions(state: tuple[int, ...]) -> dict[tuple[int, ...], int]:
    """Return next_state -> number of ways for one column step."""

    v_prev, inT, contT, valT, inB, contB, valB = state

    def add(
        v_cur: int,
        t_state: tuple[int, int, int],
        b_state: tuple[int, int, int],
        ways: int,
        out: dict[tuple[int, ...], int],
    ) -> None:
        # no-four-corners rule at the boundary between previous and current column:
        # forbidden iff both rows have a cut there (i.e. both current cells are free),
        # and neither side column is a vertical domino.
        if v_prev == 0 and v_cur == 0 and inT == 0 and inB == 0:
            return
        nt_in, nt_cont, nt_val = t_state
        nb_in, nb_cont, nb_val = b_state
        ns = (v_cur, nt_in, nt_cont, nt_val, nb_in, nb_cont, nb_val)
        out[ns] = (out.get(ns, 0) + ways) % MOD

    out: dict[tuple[int, ...], int] = {}

    # Determine current colours if occupied by an incoming horizontal tile.
    cT = valT if inT else -1
    cB = valB if inB else -1

    # If a row is incoming, we can already compute its contribution to the next state's row-part.
    def next_from_incoming(
        incoming: int, cont: int, colour: int
    ) -> tuple[int, int, int]:
        if incoming == 0:
            raise ValueError("called next_from_incoming for non-incoming row")
        if cont:
            # It continues into next column, but cannot continue beyond that.
            return (1, 0, colour)
        # It ends here; next column starts with a cut and left-colour = this tile.
        return (0, 0, colour)

    nextT = next_from_incoming(inT, contT, valT) if inT else None
    nextB = next_from_incoming(inB, contB, valB) if inB else None

    leftT = valT  # meaningful only if inT==0
    leftB = valB  # meaningful only if inB==0

    # Case 1: both cells already occupied (two horizontal tiles entering from the left).
    if inT and inB:
        # They are vertically adjacent in this column.
        if cT != cB:
            add(0, nextT, nextB, 1, out)
        return out

    # Case 2: top occupied, bottom free -> must place a horizontal tile in bottom row.
    if inT and not inB:
        for L in (1, 2, 3):
            for col in range(COLORS):
                if leftB != NONE and col == leftB:
                    continue
                if col == cT:
                    continue
                if L == 1:
                    b_state = (0, 0, col)
                elif L == 2:
                    b_state = (1, 0, col)
                else:  # L == 3
                    b_state = (1, 1, col)
                add(0, nextT, b_state, 1, out)
        return out

    # Case 3: bottom occupied, top free -> must place a horizontal tile in top row.
    if not inT and inB:
        for L in (1, 2, 3):
            for col in range(COLORS):
                if leftT != NONE and col == leftT:
                    continue
                if col == cB:
                    continue
                if L == 1:
                    t_state = (0, 0, col)
                elif L == 2:
                    t_state = (1, 0, col)
                else:  # L == 3
                    t_state = (1, 1, col)
                add(0, t_state, nextB, 1, out)
        return out

    # Case 4: both cells free.
    # Option A: place a vertical domino.
    for col in range(COLORS):
        if leftT != NONE and col == leftT:
            continue
        if leftB != NONE and col == leftB:
            continue
        # The domino ends in this column.
        add(1, (0, 0, col), (0, 0, col), 1, out)

    # Option B: place two horizontal tiles (one per row), only possible when it doesn't
    # violate the corner rule; `add()` filters the forbidden boundary automatically.
    for Lt in (1, 2, 3):
        for Lb in (1, 2, 3):
            for ct in range(COLORS):
                if leftT != NONE and ct == leftT:
                    continue
                for cb in range(COLORS):
                    if leftB != NONE and cb == leftB:
                        continue
                    if ct == cb:
                        continue  # vertical adjacency

                    if Lt == 1:
                        t_state = (0, 0, ct)
                    elif Lt == 2:
                        t_state = (1, 0, ct)
                    else:
                        t_state = (1, 1, ct)

                    if Lb == 1:
                        b_state = (0, 0, cb)
                    elif Lb == 2:
                        b_state = (1, 0, cb)
                    else:
                        b_state = (1, 1, cb)

                    add(0, t_state, b_state, 1, out)

    return out


def build_automaton() -> tuple[list[tuple[int, ...]], list[list[tuple[int, int]]]]:
    """Enumerate all reachable states and the sparse transition graph.

    Returns:
      - states: list of state tuples
      - adj: adjacency list, adj[i] = list of (j, weight) transitions
    """

    init = (1, 0, 0, NONE, 0, 0, NONE)

    states: list[tuple[int, ...]] = [init]
    index = {init: 0}
    adj: list[list[tuple[int, int]]] = []

    q = [init]
    qi = 0
    while qi < len(q):
        s = q[qi]
        qi += 1

        trans = _transitions(s)
        row: list[tuple[int, int]] = []
        for ns, w in trans.items():
            if ns not in index:
                index[ns] = len(states)
                states.append(ns)
                q.append(ns)
            row.append((index[ns], w))
        adj.append(row)

    return states, adj


def compute_small(
    n: int, states: list[tuple[int, ...]], adj: list[list[tuple[int, int]]]
) -> int:
    """Compute F(n) by straightforward DP, suitable for small n (e.g. test values)."""

    init = (1, 0, 0, NONE, 0, 0, NONE)
    idx = {s: i for i, s in enumerate(states)}
    S = len(states)

    vec = [0] * S
    vec[idx[init]] = 1

    for _ in range(n):
        nxt = [0] * S
        for i, val in enumerate(vec):
            if val == 0:
                continue
            for j, w in adj[i]:
                nxt[j] = (nxt[j] + val * w) % MOD
        vec = nxt

    ans = 0
    for i, s in enumerate(states):
        _, inT, _, _, inB, _, _ = s
        if inT == 0 and inB == 0:
            ans = (ans + vec[i]) % MOD
    return ans


def dense_matrix_from_adj(S: int, adj: list[list[tuple[int, int]]]) -> list[list[int]]:
    A = [[0] * S for _ in range(S)]
    for i in range(S):
        for j, w in adj[i]:
            A[i][j] = w
    return A


def mat_mul(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
    """Dense matrix multiplication (mod MOD)."""

    n = len(A)
    C = [[0] * n for _ in range(n)]
    rng = range(n)
    mod = MOD

    for i in rng:
        Ai = A[i]
        Ci = C[i]
        for k in rng:
            a = Ai[k]
            if a:
                Bk = B[k]
                for j in rng:
                    Ci[j] += a * Bk[j]
        for j in rng:
            Ci[j] %= mod

    return C


def vec_mul(v: list[int], A: list[list[int]]) -> list[int]:
    """Row-vector times matrix (mod MOD): returns v*A."""

    n = len(A)
    out = [0] * n
    mod = MOD

    for i, vi in enumerate(v):
        if vi == 0:
            continue
        Ai = A[i]
        for j, aij in enumerate(Ai):
            if aij:
                out[j] = (out[j] + vi * aij) % mod

    return out


def apply_power(T: list[list[int]], exp: int, v0: list[int]) -> list[int]:
    """Compute v0 * (T^exp) with binary exponentiation."""

    vec = v0[:]
    power = T
    e = exp

    while e > 0:
        if e & 1:
            vec = vec_mul(vec, power)
        e //= 2
        if e:
            power = mat_mul(power, power)

    return vec


def solve(n: int) -> int:
    states, adj = build_automaton()

    # Problem statement test values
    assert compute_small(2, states, adj) == 120
    assert compute_small(5, states, adj) == 45_876
    assert compute_small(100, states, adj) == 53_275_818

    S = len(states)
    T = dense_matrix_from_adj(S, adj)

    init = (1, 0, 0, NONE, 0, 0, NONE)
    idx = {s: i for i, s in enumerate(states)}

    v0 = [0] * S
    v0[idx[init]] = 1

    vN = apply_power(T, n, v0)

    ans = 0
    for i, s in enumerate(states):
        _, inT, _, _, inB, _, _ = s
        if inT == 0 and inB == 0:
            ans = (ans + vN[i]) % MOD

    return ans


def main() -> None:
    print(solve(10**16))


if __name__ == "__main__":
    main()
