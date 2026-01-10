#!/usr/bin/env python3
"""
Project Euler 519 - Tricoloured Coin Fountains

Compute T(20000) mod 1_000_000_000.

No external libraries are used.
"""

from __future__ import annotations

import sys
import math

MOD = 1_000_000_000


def T(n: int) -> int:
    """
    Return T(n) modulo 1_000_000_000.

    DP meaning (high level):
      dp[s][h] = total number of valid 3-colourings over all fountains
                 of total size s, in a Catalan/Dyck-path encoding whose
                 current boundary-height parameter is h.

    Recurrence used (from the problem's combinatorics, see README):
      dp[1][1] = 3
      dp[s + k][k] += dp[s][h] * w(h, k)    for 1 <= k <= h+1
      where w(h,k) = 2 if (h==1 or k==1) else 1

    Answer:
      T(n) = sum_{h: h*h <= 2n} dp[n][h]
    """
    if n <= 0:
        return 0
    if n == 1:
        return 3

    max_h = math.isqrt(2 * n) + 2  # safe bound for all h that can matter
    # We only ever write dp[s+k] with k <= max_h, so a rolling buffer of size > max_h is safe.
    buf = max_h + 3
    dp = [[0] * (max_h + 2) for _ in range(buf)]

    dp[1 % buf][1] = 3

    for s in range(1, n):
        row = dp[s % buf]

        # h cannot exceed ~sqrt(2*s); using the same safe bound as the original solution.
        maxj = min(max_h, math.isqrt(2 * s) + 1)

        # Suffix sums: suff[t] = sum_{h>=t} dp[s][h]
        suff = [0] * (maxj + 3)
        running = 0
        for h in range(maxj, 0, -1):
            running = (running + row[h]) % MOD
            suff[h] = running

        remaining = n - s
        if remaining <= 0 or running == 0:
            # Clear this buffer row (safe because buf > max_h, so it won't be referenced again soon).
            for h in range(1, maxj + 1):
                row[h] = 0
            continue

        # k = 1: weight is always 2 (because k == 1)
        dp[(s + 1) % buf][1] = (dp[(s + 1) % buf][1] + 2 * suff[1]) % MOD

        if remaining >= 2:
            # k = 2: all h>=1 contribute, but h==1 has weight 2
            # => total + dp[s][1]
            dp[(s + 2) % buf][2] = (dp[(s + 2) % buf][2] + suff[1] + row[1]) % MOD

        # k >= 3: only h >= k-1 contribute, weight 1
        maxk = min(max_h, maxj + 1, remaining)
        for k in range(3, maxk + 1):
            dp[(s + k) % buf][k] = (dp[(s + k) % buf][k] + suff[k - 1]) % MOD

        # Clear current row after using it.
        for h in range(1, maxj + 1):
            row[h] = 0

    # Sum over feasible h
    limit = math.isqrt(2 * n)
    ans_row = dp[n % buf]
    return sum(ans_row[1 : limit + 1]) % MOD


def solve(n: int = 20000) -> str:
    # Problem statement checks:
    assert T(4) == 48
    assert T(10) == 17760

    return f"{T(n):09d}"  # "last 9 digits" (pad with leading zeros if needed)


def main() -> None:
    n = 20000
    if len(sys.argv) > 1:
        n = int(sys.argv[1])
    print(solve(n))


if __name__ == "__main__":
    main()
