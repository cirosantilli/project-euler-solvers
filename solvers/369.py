#!/usr/bin/env python3
"""
Project Euler 369 - Badugi
https://projecteuler.net/problem=369

We model the deck as a 4x13 grid:
- 4 suits (left side of a bipartite graph)
- 13 ranks (right side)
Selecting cards corresponds to selecting edges (suit, rank).

A 4-card Badugi subset exists iff the bipartite graph contains a matching
covering all 4 suits (each suit matched to a distinct rank).

We count, for each n (4 <= n <= 13), the number of n-card selections that
contain such a matching, then sum them.
"""


def nCk(n: int, k: int) -> int:
    """Compute binomial coefficient C(n,k) with exact integer arithmetic."""
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    num = 1
    den = 1
    # multiplicative formula
    for i in range(1, k + 1):
        num *= n - (k - i)
        den *= i
    return num // den


def popcount4(x: int) -> int:
    # x is 0..15, tiny popcount
    return (x & 1) + ((x >> 1) & 1) + ((x >> 2) & 1) + ((x >> 3) & 1)


# Precompute popcounts for suit-subsets (0..15).
POPCOUNT = [popcount4(s) for s in range(16)]


def update_reachable(reach: int, suits_present: int) -> int:
    """
    reach is a 16-bit bitset over suit-masks (0..15):
      bit m == 1 means there exists a matching using processed ranks
      that covers exactly the suits in mask m.
    suits_present is a 4-bit mask of suits available in the new rank.

    Adding one rank can extend any existing matching by matching ONE new suit
    from suits_present not already covered.
    """
    new_reach = reach  # option: don't use this rank
    for m in range(16):
        if (reach >> m) & 1:
            avail = suits_present & (~m)  # suits not already covered
            b = avail & 0xF
            while b:
                lsb = b & -b
                new_reach |= 1 << (m | lsb)
                b -= lsb
    return new_reach & 0xFFFF


def build_state_space():
    """
    Only a small subset of the 2^16 possible reach-bitsets are actually
    reachable by repeatedly applying update_reachable with suits_present in 0..15.
    We enumerate the reachable ones (68 states) with a BFS.
    """
    start = 1 << 0  # only empty set of suits is matchable initially
    seen = {start}
    queue = [start]
    for reach in queue:
        for suits_present in range(16):
            nxt = update_reachable(reach, suits_present)
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    states = queue  # BFS order
    index = {s: i for i, s in enumerate(states)}
    trans = [[0] * 16 for _ in states]
    for i, reach in enumerate(states):
        for suits_present in range(16):
            trans[i][suits_present] = index[update_reachable(reach, suits_present)]
    return start, states, index, trans


def solve(max_n: int = 13) -> int:
    start, states, index, trans = build_state_space()
    start_idx = index[start]

    # dp[state_index][k] = number of selections among processed ranks
    # resulting in reach-state, selecting exactly k cards (k <= max_n)
    dp = [[0] * (max_n + 1) for _ in states]
    dp[start_idx][0] = 1

    # Process 13 ranks; each rank independently chooses a subset of its 4 suit-cards.
    for _ in range(13):
        ndp = [[0] * (max_n + 1) for _ in states]
        for i, arr in enumerate(dp):
            # skip all-zero rows quickly
            if not any(arr):
                continue
            for suits_present in range(16):
                j = trans[i][suits_present]
                add = POPCOUNT[suits_present]
                if add > max_n:
                    continue
                targ = ndp[j]
                for k, v in enumerate(arr):
                    nk = k + add
                    if v and nk <= max_n:
                        targ[nk] += v
        dp = ndp

    # f(n) is the count of n-card selections whose reach-state includes mask 15 (all suits matchable)
    full_mask_bit = 1 << 15
    f = [0] * (max_n + 1)
    for i, reach in enumerate(states):
        if reach & full_mask_bit:
            for n in range(max_n + 1):
                f[n] += dp[i][n]

    # Asserts from the problem statement:
    assert nCk(52, 5) == 2598960
    assert f[5] == 514800

    return sum(f[n] for n in range(4, max_n + 1))


def main():
    print(solve(13))


if __name__ == "__main__":
    main()
