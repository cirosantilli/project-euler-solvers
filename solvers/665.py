#!/usr/bin/env python3
"""
Project Euler 665 - Proportionate Nim

Compute f(M) for M = 10^7.

Rules (from the problem statement):
Moves from (n,m) allow subtracting:
- (k,0) or (0,k)  (remove k from one pile)
- (k,k)          (remove k from both piles)
- (k,2k) or (2k,k) (remove k from one pile and 2k from the other)

A losing (P) position set can be generated greedily with mex, enforcing that no two
P-positions share any move-invariant:
- coordinate values (due to single-pile moves)
- difference (b-a) (due to diagonal moves)
- linear forms (b-2a) and (a-2b) (due to (k,2k)/(2k,k) moves)

We generate P-positions in increasing mex of the smaller coordinate a, and for each a
choose the smallest b >= a+1 satisfying all constraints. Then we sum a+b over those
P-positions with a+b <= M.
"""

from array import array


def f(M: int) -> int:
    if M < 0:
        return 0

    # We must generate true P-positions of the infinite game, then count those with a+b <= M.
    # It's enough to generate all pairs with a <= M//2 (since b >= a implies a+b > M when a > M//2).
    half = M // 2

    # Empirically (and supported by the structure of this game), b stays below about 1.13*M
    # for all needed a <= M//2. Use a conservative headroom factor.
    L = (M * 12) // 10 + 100  # 1.2*M + 100

    # Disjoint-set "next free" structure:
    # parent[x] = smallest y >= x that is not yet used (after path compression).
    #
    # We use DSU for:
    # - used coordinate values (a and b)
    # - used differences d = b-a
    #
    # This avoids repeated scanning in dense arrays.
    par_num = array("I", range(L + 2))   # sentinel at L+1
    par_diff = array("I", range(L + 2))  # sentinel at L+1

    def find(par: array, x: int) -> int:
        while par[x] != x:
            par[x] = par[par[x]]
            x = par[x]
        return x

    def occupy(par: array, x: int) -> None:
        # Mark x as used: redirect to next free.
        par[x] = find(par, x + 1)

    # For linear constraints we keep a compact boolean table for t in [-2L, L]
    # mapped by idx = t + shift.
    shift = 2 * L
    used_lin = bytearray(3 * L + 1)

    # To test the constraint "a-2b not used", it is convenient to use u = 2b-a = -(a-2b).
    # For fixed a, u increases by 2 as b increases. We store used u's split by parity:
    #   even u : used_u2_even[u//2] == 1
    #   odd u  : used_u2_odd[u//2]  == 1
    used_u2_even = bytearray(L + 1)  # u in [0, 2L] -> u//2 in [0, L]
    used_u2_odd = bytearray(L + 1)

    twoL = 2 * L

    # Initialize with (0,0) as a losing position.
    occupy(par_num, 0)
    occupy(par_diff, 0)
    used_lin[shift] = 1  # t=0
    used_u2_even[0] = 1  # u=0

    total = 0
    a = 0  # search cursor for mex; with DSU we can just call find(par_num, a)

    # Local bindings for speed
    par_num_local = par_num
    par_diff_local = par_diff
    used_lin_local = used_lin
    used_u2e = used_u2_even
    used_u2o = used_u2_odd
    find_num = find
    find_diff = find

    lin_find = used_lin_local.find
    u2e_find = used_u2e.find
    u2o_find = used_u2o.find
    sh = shift
    L_local = L
    twoL_local = twoL

    while True:
        a = find_num(par_num_local, a)
        if a > half:
            break

        # b=a is impossible because d=0 is already used. Start at a+1.
        b = find_num(par_num_local, a + 1)

        while True:
            # difference constraint
            d = b - a
            nd = find_diff(par_diff_local, d)
            if nd != d:
                b = a + nd
                b = find_num(par_num_local, b)
                continue

            # linear constraint 1: t1 = b-2a
            idx1 = (b - 2 * a) + sh
            if used_lin_local[idx1]:
                idx = lin_find(0, idx1 + 1)
                b = (idx - sh) + 2 * a
                b = find_num(par_num_local, b)
                continue

            # linear constraint 2: t2 = a-2b <=> u = 2b-a must be unused (with parity step 2)
            u = 2 * b - a
            if u & 1:
                ui = u >> 1
                if used_u2o[ui]:
                    ni = u2o_find(0, ui + 1)
                    b = (a + (2 * ni + 1)) >> 1
                    b = find_num(par_num_local, b)
                    continue
            else:
                ui = u >> 1
                if used_u2e[ui]:
                    ni = u2e_find(0, ui + 1)
                    b = (a + (2 * ni)) >> 1
                    b = find_num(par_num_local, b)
                    continue

            # All constraints satisfied
            break

        # Mark a, b, and d as used
        occupy(par_num_local, a)
        occupy(par_num_local, b)
        occupy(par_diff_local, d)

        # Mark linear values and their negations in the u-table
        t = b - 2 * a
        used_lin_local[t + sh] = 1
        u = -t
        if 0 <= u <= twoL_local:
            (used_u2o if (u & 1) else used_u2e)[u >> 1] = 1

        t = a - 2 * b
        used_lin_local[t + sh] = 1
        u = -t
        if 0 <= u <= twoL_local:
            (used_u2o if (u & 1) else used_u2e)[u >> 1] = 1

        s = a + b
        if s <= M:
            total += s

        # Next mex search can start at a+1
        a += 1

    return total


def _self_test() -> None:
    # Test values given in the problem statement
    assert f(10) == 21
    assert f(100) == 1164
    assert f(1000) == 117002


if __name__ == "__main__":
    _self_test()
    print(f(10**7))
