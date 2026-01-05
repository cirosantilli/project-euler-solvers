#!/usr/bin/env python3
"""Project Euler 497: Drunken Tower of Hanoi

Compute the last nine digits of:
    \sum_{1<=n<=10000} E(n, 10^n, 3^n, 6^n, 9^n)

No external libraries are used.

The program prints the answer as a 9-digit number (with leading zeros if needed).
"""

import sys
from typing import Optional

MOD = 1_000_000_000  # last nine digits

# Rod indices: 0=A, 1=B, 2=C
# Directed edges between distinct rods in a fixed order:
EDGES = [(0, 1), (0, 2), (1, 0), (1, 2), (2, 0), (2, 1)]
EDGE_IDX = {e: i for i, e in enumerate(EDGES)}


def expected_steps_reflecting(i: int, j: int, k: int) -> int:
    """Expected steps for a symmetric random walk on {1..k} with reflecting ends.

    Start at i, stop upon first hitting j.

    Closed form (from a second-order difference equation):
      - if i < j: (j-i) * (j+i-2)
      - if i > j: (i-j) * (2k - i - j)
      - if i = j: 0
    """
    if i == j:
        return 0
    if i < j:
        return (j - i) * (j + i - 2)
    return (i - j) * (2 * k - i - j)


def _init_counts(mod: Optional[int]):
    """Base DP (n=1) for counting directed rod-to-rod walk segments.

    dp[from][to][start] is a length-6 vector counting how many times each directed
    segment in EDGES occurs while executing the optimal (minimum-pickup) Hanoi
    solution to move 1 disk from 'from' to 'to', starting with Bob at 'start'.

    We keep only directed transitions between distinct rods; 'start==from' adds
    no segment for the initial pickup.
    """
    dp = [[[[0] * 6 for _ in range(3)] for _ in range(3)] for _ in range(3)]
    for fr in range(3):
        for to in range(3):
            if fr == to:
                continue
            for st in range(3):
                vec = [0] * 6
                if st != fr:
                    vec[EDGE_IDX[(st, fr)]] += 1
                vec[EDGE_IDX[(fr, to)]] += 1
                if mod is not None:
                    vec = [x % mod for x in vec]
                dp[fr][to][st] = vec
    return dp


def _step_counts(dp, mod: Optional[int]):
    """Advance the counts DP from n-1 to n using the Hanoi recursion."""
    new = [[[[0] * 6 for _ in range(3)] for _ in range(3)] for _ in range(3)]
    for fr in range(3):
        for to in range(3):
            if fr == to:
                continue
            aux = 3 - fr - to
            for st in range(3):
                v1 = dp[fr][aux][st]  # move n-1 disks: fr -> aux
                v2 = dp[aux][to][to]  # move n-1 disks: aux -> to, starting at 'to'
                vec = [v1[i] + v2[i] for i in range(6)]
                vec[EDGE_IDX[(aux, fr)]] += 1  # go aux -> fr to pick up largest disk
                vec[EDGE_IDX[(fr, to)]] += 1  # go fr  -> to to drop it
                if mod is not None:
                    vec = [x % mod for x in vec]
                new[fr][to][st] = vec
    return new


def expected_distance_exact(n: int, k: int, a: int, b: int, c: int) -> int:
    """Exact E(n,k,a,b,c) for small inputs (used for problem statement asserts)."""
    pos = {0: a, 1: b, 2: c}
    d = {
        (u, v): expected_steps_reflecting(pos[u], pos[v], k)
        for u in range(3)
        for v in range(3)
        if u != v
    }

    dp = _init_counts(mod=None)
    for _ in range(2, n + 1):
        dp = _step_counts(dp, mod=None)

    counts = dp[0][2][1]  # move n disks A->C, Bob starts at B
    total = 0
    for idx, (u, v) in enumerate(EDGES):
        total += counts[idx] * d[(u, v)]
    return total


def _dist_mod_i_lt_j(i: int, j: int) -> int:
    # (j-i)*(j+i-2) mod MOD
    return ((j - i) % MOD) * ((j + i - 2) % MOD) % MOD


def _dist_mod_i_gt_j(i: int, j: int, k: int) -> int:
    # (i-j)*(2k-i-j) mod MOD
    return ((i - j) % MOD) * ((2 * k - i - j) % MOD) % MOD


def solve(limit: int = 10_000) -> int:
    """Return the answer modulo 1e9 (i.e., the last nine digits)."""
    dp = _init_counts(mod=MOD)  # base corresponds to n=1

    # modular powers (we only need residues mod 1e9)
    a = b = c = k = 1

    total = 0
    for n in range(1, limit + 1):
        a = (a * 3) % MOD
        b = (b * 6) % MOD
        c = (c * 9) % MOD
        k = (k * 10) % MOD

        if n > 1:
            dp = _step_counts(dp, mod=MOD)

        # For these inputs, ordering is always a < b < c < 10^n.
        d01 = _dist_mod_i_lt_j(a, b)  # A -> B
        d02 = _dist_mod_i_lt_j(a, c)  # A -> C
        d10 = _dist_mod_i_gt_j(b, a, k)  # B -> A
        d12 = _dist_mod_i_lt_j(b, c)  # B -> C
        d20 = _dist_mod_i_gt_j(c, a, k)  # C -> A
        d21 = _dist_mod_i_gt_j(c, b, k)  # C -> B
        d = [d01, d02, d10, d12, d20, d21]

        counts = dp[0][2][1]
        e = 0
        for i in range(6):
            e = (e + counts[i] * d[i]) % MOD

        total = (total + e) % MOD

    return total


def main() -> None:
    # Asserts for example values in the problem statement:
    assert expected_distance_exact(2, 5, 1, 3, 5) == 60
    assert expected_distance_exact(3, 20, 4, 9, 17) == 2358

    ans = solve(10_000)
    sys.stdout.write(f"{ans:09d}\n")


if __name__ == "__main__":
    main()
