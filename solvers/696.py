#!/usr/bin/env python3
"""
Project Euler 696: Mahjong

Counts distinct winning hands (tile multisets), not the number of decompositions.

No external libraries are used.
"""
from collections import deque

MOD = 1_000_000_007


def _precompute_fact(kmax: int):
    fact = [1] * (kmax + 1)
    invfact = [1] * (kmax + 1)
    for i in range(1, kmax + 1):
        fact[i] = fact[i - 1] * i % MOD
    invfact[kmax] = pow(fact[kmax], MOD - 2, MOD)
    for i in range(kmax, 0, -1):
        invfact[i - 1] = invfact[i] * i % MOD
    return fact, invfact


def _nCk_small(N: int, K: int, invfact):
    """Compute C(N,K) mod MOD for small K (K <= ~100). Works for any integer N."""
    if K < 0:
        return 0
    if K == 0:
        return 1
    if N < K:
        return 0
    num = 1
    # N*(N-1)*...*(N-K+1) / K!
    for i in range(K):
        num = (num * ((N - i) % MOD)) % MOD
    return (num * invfact[K]) % MOD


# -------------------- Automaton construction --------------------

# NFA states are (a, b, p):
#   a = # chows started at previous number (need 1 tile now)
#   b = # chows started two numbers ago (need 1 tile now to finish)
#   p = 0/1 whether the pair has already been used
#
# Input symbol c in {0..4} is the tile count for the current number in this suit.
# Transition chooses:
#   x = chows starting here
#   y = pungs here (0/1)
#   z = pair here (0/1, only if p=0)
# satisfying: a+b + x + 3y + 2z = c
# Next NFA state becomes (x, a, p|z).


def _nfa_next(a: int, b: int, p: int, c: int):
    if a + b > c:
        return ()
    r = c - (a + b)
    out = []
    z_choices = (0, 1) if p == 0 else (0,)
    for z in z_choices:
        if 2 * z > r:
            continue
        r2 = r - 2 * z
        for y in (0, 1):
            if 3 * y > r2:
                continue
            x = r2 - 3 * y
            if 0 <= x <= 4:
                out.append((x, a, p | z))
    # remove duplicates (tiny list)
    if len(out) <= 1:
        return tuple(out)
    out = tuple(sorted(set(out)))
    return out


def _build_dfa():
    # Enumerate NFA states
    nfa_states = [(a, b, p) for a in range(5) for b in range(5) for p in (0, 1)]
    nfa_index = {st: i for i, st in enumerate(nfa_states)}
    # Precompute NFA transitions for speed
    nfa_trans = [[None] * 5 for _ in range(len(nfa_states))]
    for st in nfa_states:
        i = nfa_index[st]
        a, b, p = st
        for c in range(5):
            nxt = _nfa_next(a, b, p, c)
            nfa_trans[i][c] = tuple(nfa_index[s] for s in nxt)

    # Subset-construction determinization (DFA)
    init = frozenset([nfa_index[(0, 0, 0)]])
    q = deque([init])
    dfa_index = {init: 0}
    dfa_states = []
    dfa_trans = []  # [dfa_state][c] = next_dfa_state
    while q:
        S = q.popleft()
        dfa_states.append(S)
        row = []
        for c in range(5):
            nxt = set()
            for si in S:
                nxt.update(nfa_trans[si][c])
            nxt = frozenset(nxt)
            if nxt not in dfa_index:
                dfa_index[nxt] = len(dfa_index)
                q.append(nxt)
            row.append(dfa_index[nxt])
        dfa_trans.append(row)

    # Find boundary states (after reading a 0, only (0,0,p) can survive)
    # These are fixed points of the 0-transition.
    delta0 = [dfa_trans[i][0] for i in range(len(dfa_states))]
    empty_state = dfa_index[frozenset()]  # dead/empty set
    b0 = dfa_index[frozenset([nfa_index[(0, 0, 0)]])]
    b1 = dfa_index[frozenset([nfa_index[(0, 0, 1)]])]
    return dfa_states, dfa_trans, delta0, b0, b1, empty_state


_DFA_STATES, _DFA_TRANS, _DELTA0, _BOUNDARY0, _BOUNDARY1, _DEAD = _build_dfa()


# -------------------- Block tables --------------------


def _build_block_tables(max_len: int, max_tiles: int):
    """
    H[L][T] = number of 'blocks' (positive run, no zeros inside) of length L and tile-sum T
              such that starting from boundary p=0, after the block we can read a 0 and be back
              at boundary p=0 (i.e. no pending chows and no pair used).
    J[L][T] = same, but after reading a 0 we end at boundary p=1 (pair used exactly once).
    """
    d = len(_DFA_STATES)
    # dp[state][tiles] for current length
    dp = [[0] * (max_tiles + 1) for _ in range(d)]
    dp[_BOUNDARY0][0] = 1

    H = [[0] * (max_tiles + 1) for _ in range(max_len + 1)]
    J = [[0] * (max_tiles + 1) for _ in range(max_len + 1)]

    for L in range(1, max_len + 1):
        dp2 = [[0] * (max_tiles + 1) for _ in range(d)]
        for st in range(d):
            row = dp[st]
            # symbols are 1..4 inside a block
            for c in (1, 2, 3, 4):
                nxt = _DFA_TRANS[st][c]
                dst = dp2[nxt]
                limit = max_tiles - c
                for t in range(limit + 1):
                    v = row[t]
                    if v:
                        dst[t + c] = (dst[t + c] + v) % MOD
        dp = dp2

        for st in range(d):
            b = _DELTA0[st]  # state after a separating 0
            if b == _BOUNDARY0:
                out = H[L]
            elif b == _BOUNDARY1:
                out = J[L]
            else:
                continue
            row = dp[st]
            for t, v in enumerate(row):
                if v:
                    out[t] = (out[t] + v) % MOD

    # Precompute sparse term-lists per length to speed convolutions
    H_terms = [[] for _ in range(max_len + 1)]
    J_terms = [[] for _ in range(max_len + 1)]
    for L in range(1, max_len + 1):
        for T in range(max_tiles + 1):
            v = H[L][T]
            if v:
                H_terms[L].append((T, v))
            v = J[L][T]
            if v:
                J_terms[L].append((T, v))
    return H_terms, J_terms


def _convolve_len_tiles(A, B_terms, max_len: int, max_tiles: int):
    """
    Convolution in (length, tiles):
      C[L1+L2][T1+T2] += A[L1][T1] * B[L2][T2]
    where B is given as per-length sparse lists.
    """
    C = [[0] * (max_tiles + 1) for _ in range(max_len + 1)]
    for L1 in range(max_len + 1):
        row1 = A[L1]
        if not any(row1):
            continue
        max_L2 = max_len - L1
        for L2 in range(1, max_L2 + 1):
            terms = B_terms[L2]
            if not terms:
                continue
            out = C[L1 + L2]
            for T1, v1 in enumerate(row1):
                if not v1:
                    continue
                for T2, v2 in terms:
                    TT = T1 + T2
                    if TT <= max_tiles:
                        out[TT] = (out[TT] + v1 * v2) % MOD
    return C


# -------------------- Per-suit generating polynomials --------------------


def _per_suit_A_B(n: int, t: int):
    """
    Returns (A, B) where:
      A[k] = # ways a single suit contributes exactly k Triples and no Pair
      B[k] = # ways a single suit contributes exactly k Triples and exactly one Pair
    for numbers 1..n in that suit.

    Internally counts by total tiles T, then maps:
      A[k] = count(T = 3k, no pair)
      B[k] = count(T = 3k+2, with pair)
    """
    max_tiles = 3 * t + 2
    max_len = min(max_tiles, n)  # no run longer than n

    H_terms, J_terms = _build_block_tables(max_len, max_tiles)
    _, invfact = _precompute_fact(max_len)

    # P = H^b as a dense (length, tiles) polynomial; start at b=0
    P = [[0] * (max_tiles + 1) for _ in range(max_len + 1)]
    P[0][0] = 1

    G0 = [0] * (max_tiles + 1)  # no pair
    G1 = [0] * (max_tiles + 1)  # with pair

    # iterate over number of no-pair blocks b
    for b in range(0, max_len + 1):
        # Add no-pair contributions with exactly b blocks:
        # placements factor = C(n - L + 1, b)
        for L in range(max_len + 1):
            N = n - L + 1
            if N < b:
                continue
            comb = _nCk_small(N, b, invfact)
            if not comb:
                continue
            row = P[L]
            for T, v in enumerate(row):
                if v:
                    G0[T] = (G0[T] + v * comb) % MOD

        # Add pair contributions with total blocks B=b+1:
        # sequences: choose the position of the pair-block (factor B),
        # then pick B-1 no-pair blocks (H^b) and one pair-block (J)
        B = b + 1
        if B <= max_len:
            R = _convolve_len_tiles(P, J_terms, max_len, max_tiles)
            for L in range(max_len + 1):
                N = n - L + 1
                if N < B:
                    continue
                comb = _nCk_small(N, B, invfact)
                if not comb:
                    continue
                factor = (comb * B) % MOD
                row = R[L]
                for T, v in enumerate(row):
                    if v:
                        G1[T] = (G1[T] + v * factor) % MOD

        # Next power: P <- P * H
        if b != max_len:
            P = _convolve_len_tiles(P, H_terms, max_len, max_tiles)

    A = [0] * (t + 1)
    Bc = [0] * (t + 1)
    for k in range(t + 1):
        A[k] = G0[3 * k] if 3 * k <= max_tiles else 0
        idx_t = 3 * k + 2
        Bc[k] = G1[idx_t] if idx_t <= max_tiles else 0
    return A, Bc


# -------------------- Combine suits --------------------


def _poly_mul(a, b, deg: int):
    res = [0] * (deg + 1)
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            if bj == 0:
                continue
            ij = i + j
            if ij > deg:
                break
            res[ij] = (res[ij] + ai * bj) % MOD
    return res


def _poly_pow(base, exp: int, deg: int):
    res = [0] * (deg + 1)
    res[0] = 1
    b = base[:]
    e = exp
    while e > 0:
        if e & 1:
            res = _poly_mul(res, b, deg)
        e >>= 1
        if e:
            b = _poly_mul(b, b, deg)
    return res


def w(n: int, s: int, t: int) -> int:
    """
    Compute w(n,s,t) mod MOD.
    """
    A, B = _per_suit_A_B(n, t)
    # other suits contribute only via A; the suit with the pair is chosen in s ways
    if s <= 1:
        A_pow = [1] + [0] * t
    else:
        A_pow = _poly_pow(A, s - 1, t)

    total = 0
    for k in range(t + 1):
        total = (total + B[k] * A_pow[t - k]) % MOD
    return (total * (s % MOD)) % MOD


def main():
    # Tests from the problem statement
    assert w(4, 1, 1) == 20
    assert w(9, 1, 4) == 13259
    assert w(9, 3, 4) == 5237550
    assert w(1000, 1000, 5) == 107662178

    # Required computation
    print(w(10**8, 10**8, 30))


if __name__ == "__main__":
    main()
