#!/usr/bin/env python3
"""
Project Euler 376: Nontransitive Sets of Dice

We count (cyclic) nontransitive triples of 6-sided dice with face values in [1..N].

A triple (A,B,C) is "nontransitive" here when:
    B beats A, C beats B, and A beats C,
where "X beats Y" means P(X roll > Y roll) > 1/2.
(If equal, nobody wins.)

The problem asks for the number of such sets for N = 30, where the sets
{A,B,C}, {B,C,A}, {C,A,B} are considered the same (cyclic rotation),
so we count ordered cycles and divide by 3.

No external libraries are used.
"""

from __future__ import annotations


def nCk(n: int, k: int) -> int:
    """Compute binomial coefficient C(n,k) with integer arithmetic."""
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    res = 1
    # res = n*(n-1)*...*(n-k+1)/k!
    for i in range(1, k + 1):
        res = (res * (n - k + i)) // i
    return res


def _precompute_counts_by_distinct_values(max_k: int = 18) -> list[int]:
    """
    Let count_k be the number of ORDERED triples (A,B,C) satisfying:
        B beats A, C beats B, A beats C
    using exactly k distinct pip values overall (k <= 18 because 18 faces total).

    Then for general N:
        ordered(N) = sum_{k=1..18} count_k * C(N,k)
        answer(N)  = ordered(N) / 3
    """
    # Wins are integers in [0..36], but we only care whether > 18.
    # Cap at 19 (meaning ">= 19") to shrink state space.
    W = 20  # 0..19
    WSIZE = W * W * W  # 8000
    ABC = 7 * 7 * 7  # (a_used,b_used,c_used), each in 0..6
    TOTAL = ABC * WSIZE

    # Decode win-index (0..7999) to (wBA,wCB,wAC)
    wBA_of = [0] * WSIZE
    wCB_of = [0] * WSIZE
    wAC_of = [0] * WSIZE
    for widx in range(WSIZE):
        wAC = widx % W
        tmp = widx // W
        wCB = tmp % W
        wBA = tmp // W
        wBA_of[widx] = wBA
        wCB_of[widx] = wCB
        wAC_of[widx] = wAC

    # cap_add[w][d] = min(19, w + d) where d <= 36
    cap_add = [[0] * 37 for _ in range(20)]
    for w in range(20):
        row = cap_add[w]
        for d in range(37):
            v = w + d
            row[d] = 19 if v > 19 else v

    # Packing helper: (wBA,wCB,wAC) -> widx
    # We'll use base(wBA,wCB) = wBA*400 + wCB*20 (since 20*20 = 400)
    pack_base = [[0] * 20 for _ in range(20)]
    for wBA in range(20):
        base = wBA * 400
        row = pack_base[wBA]
        for wCB in range(20):
            row[wCB] = base + wCB * 20

    # Precompute transitions for each (a_used,b_used,c_used) code.
    # State index is:  z = abc*WSIZE + widx
    # where abc encodes (a_used,b_used,c_used) as abc = (a*7 + b)*7 + c.
    #
    # When we move to the next distinct value, we pick counts (da,db,dc) not all zero.
    # Incremental win contributions (using prefix counts):
    #   wins(B>A) increases by db * a_used
    #   wins(C>B) increases by dc * b_used
    #   wins(A>C) increases by da * c_used
    trans = [
        None
    ] * ABC  # list of lists: for each abc, entries (base_offset, dBA, dCB, dAC)
    for abc in range(ABC):
        c_used = abc % 7
        tmp = abc // 7
        b_used = tmp % 7
        a_used = tmp // 7

        ra = 6 - a_used
        rb = 6 - b_used
        rc = 6 - c_used

        lst: list[tuple[int, int, int, int]] = []
        if ra == 0 and rb == 0 and rc == 0:
            trans[abc] = lst
            continue

        for da in range(ra + 1):
            for db in range(rb + 1):
                for dc in range(rc + 1):
                    if da + db + dc == 0:
                        continue
                    na = a_used + da
                    nb = b_used + db
                    nc = c_used + dc
                    abc2 = (na * 7 + nb) * 7 + nc
                    base_offset = abc2 * WSIZE
                    # deltas in [0..36]
                    dBA = db * a_used
                    dCB = dc * b_used
                    dAC = da * c_used
                    lst.append((base_offset, dBA, dCB, dAC))
        trans[abc] = lst

    # Goal state: all dice filled and each required win-count is >=19.
    goal_abc = (6 * 7 + 6) * 7 + 6  # 342
    goal_widx = (19 * W + 19) * W + 19  # 7999
    goal = goal_abc * WSIZE + goal_widx

    # DP arrays (sparse via active index list). Counts fit easily in 64-bit for this problem.
    cur = [0] * TOTAL
    nxt = [0] * TOTAL
    active = [0]  # start at (0,0,0,0,0,0)
    cur[0] = 1

    count_k = [0] * (max_k + 1)

    for k in range(1, max_k + 1):
        nxt_active: list[int] = []
        nxt_append = nxt_active.append

        # local bindings for speed
        cur_local = cur
        nxt_local = nxt
        trans_local = trans
        wBA_local = wBA_of
        wCB_local = wCB_of
        wAC_local = wAC_of
        cap = cap_add
        pbase = pack_base

        for z in active:
            ways = cur_local[z]
            abc, widx = divmod(z, WSIZE)

            wBA = wBA_local[widx]
            wCB = wCB_local[widx]
            wAC = wAC_local[widx]

            for base_offset, dBA, dCB, dAC in trans_local[abc]:
                nwBA = cap[wBA][dBA]
                nwCB = cap[wCB][dCB]
                nwAC = cap[wAC][dAC]
                y = base_offset + pbase[nwBA][nwCB] + nwAC

                val = nxt_local[y]
                if val == 0:
                    nxt_append(y)
                    nxt_local[y] = ways
                else:
                    nxt_local[y] = val + ways

        # capture count for exactly k distinct values used
        count_k[k] = nxt_local[goal]

        # clear current layer and swap
        for z in active:
            cur_local[z] = 0
        cur, nxt = nxt, cur
        active = nxt_active

    return count_k


def count_nontransitive_sets(N: int) -> int:
    """
    Return the number of nontransitive dice sets for given N
    under the problem's equivalence {A,B,C} ~ {B,C,A} ~ {C,A,B}.
    """
    count_k = _precompute_counts_by_distinct_values(18)

    ordered = 0
    for k in range(1, 19):
        ck = count_k[k]
        if ck:
            ordered += ck * nCk(N, k)

    # Each cycle is counted 3 times by choosing the "start" of (A,B,C).
    return ordered // 3


def solve() -> int:
    # Test value from the problem statement.
    assert count_nontransitive_sets(7) == 9780

    return count_nontransitive_sets(30)


if __name__ == "__main__":
    print(solve())
