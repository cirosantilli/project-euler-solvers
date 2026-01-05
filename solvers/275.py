#!/usr/bin/env python3
"""
Project Euler 275 - Balanced Sculptures

We count balanced sculptures of order n:
- n blocks + 1 plinth
- plinth at (0,0)
- all blocks have y > 0 (so plinth is unique lowest tile)
- the x-coordinate of the center of mass of the blocks is 0
- reflections across y-axis are NOT distinct

Key transformation:
Because the only tile adjacent to the plinth with y>0 is (0,1),
every valid sculpture MUST include the block at (0,1).

So we shift coordinates down by 1:
- Treat the mandatory block at (0,1) as root at (0,0)
- All blocks now satisfy y >= 0
- Balance is simply sum(x) == 0 over all blocks

We count:
Total balanced polyominoes T (reflection-distinct)
Symmetric balanced polyominoes S (fixed under reflection)

Answer = (T + S) // 2
"""

from __future__ import annotations


def _count_total_balanced(n: int) -> int:
    """
    Count all balanced sculptures of order n with reflections counted separately.
    Uses Redelmeier's algorithm (queue-based), with pruning on possible moment.
    """
    # Bounding box limits: any cell is within manhattan distance <= n-1 from root
    XMAX = n - 1
    YMAX = n - 1
    W = 2 * XMAX + 1
    SHIFT = XMAX
    GRID = W * (YMAX + 1)

    # x-coordinate lookup by linear index
    x_of = [0] * GRID
    for y in range(YMAX + 1):
        base = y * W
        for xi in range(W):
            x_of[base + xi] = xi - SHIFT

    # neighbor list (within y>=0, box bounds)
    neigh = [None] * GRID
    for y in range(YMAX + 1):
        row = y * W
        for xi in range(W):
            idx = row + xi
            ns = []
            if xi > 0:
                ns.append(idx - 1)
            if xi < W - 1:
                ns.append(idx + 1)
            if y > 0:
                ns.append(idx - W)
            if y < YMAX:
                ns.append(idx + W)
            neigh[idx] = ns

    root = SHIFT  # (0,0)
    seen = bytearray(GRID)

    # queue of untried sites
    Q = [0] * (8 * n + 50)

    # initialize
    seen[root] = 1
    q_end = 0
    for nb in neigh[root]:
        if seen[nb] == 0:
            seen[nb] = 1
            Q[q_end] = nb
            q_end += 1

    x_arr = x_of
    nb_arr = neigh
    seen_arr = seen
    Q_arr = Q

    ans = 0

    def rec(
        q_begin: int, q_end_: int, size: int, moment: int, minx: int, maxx: int
    ) -> None:
        nonlocal ans
        if size == n:
            if moment == 0:
                ans += 1
            return

        r = n - size

        # prune using crude but safe bounds
        min_possible_x = minx - r
        max_possible_x = maxx + r

        if moment + r * min_possible_x > 0:
            return
        if moment + r * max_possible_x < 0:
            return

        for i in range(q_begin, q_end_):
            cell = Q_arr[i]
            x = x_arr[cell]

            # add new neighbors
            added = 0
            for nb in nb_arr[cell]:
                if seen_arr[nb] == 0:
                    seen_arr[nb] = 1
                    Q_arr[q_end_ + added] = nb
                    added += 1

            # update bounds
            nmin = x if x < minx else minx
            nmax = x if x > maxx else maxx

            rec(i + 1, q_end_ + added, size + 1, moment + x, nmin, nmax)

            # undo only freshly-added neighbors
            for j in range(q_end_, q_end_ + added):
                seen_arr[Q_arr[j]] = 0

    rec(0, q_end, 1, 0, 0, 0)
    return ans


def _count_symmetric(n: int) -> int:
    """
    Count mirror-symmetric sculptures of order n.
    In a symmetric sculpture, cells with x>0 appear in mirrored pairs.
    So we enumerate only x>=0, but count each x>0 cell as contributing 2 blocks.
    """
    XMAX = n - 1
    YMAX = n - 1
    W = 2 * XMAX + 1
    SHIFT = XMAX
    GRID = W * (YMAX + 1)

    # x lookup
    x_of = [0] * GRID
    for y in range(YMAX + 1):
        base = y * W
        for xi in range(W):
            x_of[base + xi] = xi - SHIFT

    # neighbors restricted to x>=0
    neigh = [None] * GRID
    for y in range(YMAX + 1):
        row = y * W
        for xi in range(W):
            idx = row + xi
            x = xi - SHIFT
            if x < 0:
                neigh[idx] = []
                continue
            ns = []
            if xi > SHIFT:
                ns.append(idx - 1)
            if xi < W - 1:
                ns.append(idx + 1)
            if y > 0:
                ns.append(idx - W)
            if y < YMAX:
                ns.append(idx + W)
            neigh[idx] = ns

    root = SHIFT
    seen = bytearray(GRID)
    Q = [0] * (8 * n + 50)

    seen[root] = 1
    q_end = 0
    for nb in neigh[root]:
        if seen[nb] == 0:
            seen[nb] = 1
            Q[q_end] = nb
            q_end += 1

    ans = 0
    x_arr = x_of
    nb_arr = neigh
    seen_arr = seen
    Q_arr = Q

    def rec(q_begin: int, q_end_: int, full_size: int) -> None:
        nonlocal ans
        if full_size == n:
            ans += 1
            return

        for i in range(q_begin, q_end_):
            cell = Q_arr[i]
            x = x_arr[cell]
            add = 1 if x == 0 else 2
            new_full = full_size + add
            if new_full > n:
                continue

            added = 0
            for nb in nb_arr[cell]:
                if seen_arr[nb] == 0:
                    seen_arr[nb] = 1
                    Q_arr[q_end_ + added] = nb
                    added += 1

            rec(i + 1, q_end_ + added, new_full)

            for j in range(q_end_, q_end_ + added):
                seen_arr[Q_arr[j]] = 0

    rec(0, q_end, 1)
    return ans


def balanced_sculptures(n: int) -> int:
    """
    Distinct sculptures of order n, where mirror reflections are identical.
    Answer = (total + symmetric) // 2.
    """
    total = _count_total_balanced(n)
    sym = _count_symmetric(n)
    return (total + sym) // 2


def main() -> None:
    # Asserts required by the problem statement
    assert balanced_sculptures(6) == 18
    assert balanced_sculptures(10) == 964
    assert balanced_sculptures(15) == 360505

    print(balanced_sculptures(18))


if __name__ == "__main__":
    main()
