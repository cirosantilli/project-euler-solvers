#!/usr/bin/env python3
"""
Project Euler 152: Writing 1/2 as a sum of inverse squares.

Count the number of subsets S ⊆ {2..80} such that:
    sum_{n in S} 1/n^2 = 1/2

Approach:
- Use the standard pruning that (for this problem) any solution only needs numbers whose
  prime factors are among {2,3,5,7,13}. This drastically cuts the search space.
- Convert the rational equation into an integer subset-sum by scaling with L^2 where
  L = lcm(candidates). Each term 1/n^2 becomes (L/n)^2 / L^2.
- Meet-in-the-middle:
  * Precompute all subset sums of the "large" candidates (n >= max_n//2).
  * DFS on the remaining candidates, and for each partial sum, look up the required
    complement among the precomputed sums.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from math import gcd
from typing import Dict, List, Tuple


ALLOWED_PRIMES = (2, 3, 5, 7, 13)


def lcm(a: int, b: int) -> int:
    return a // gcd(a, b) * b


def candidates_up_to(max_n: int) -> List[int]:
    """Return candidate denominators in [2..max_n] with no prime factors outside ALLOWED_PRIMES."""
    cand: List[int] = []
    for n in range(2, max_n + 1):
        t = n
        for p in ALLOWED_PRIMES:
            while t % p == 0:
                t //= p
        if t == 1:
            cand.append(n)
    return cand


def count_ways(max_n: int = 80) -> int:
    """
    Count ways to write 1/2 as a sum of inverse squares using distinct integers in [2..max_n].
    """
    cand = candidates_up_to(max_n)

    # Common denominator for 1/n^2 terms
    L = 1
    for n in cand:
        L = lcm(L, n)

    # Integer weights: 1/n^2 == (L/n)^2 / L^2
    weights = [(L // n) ** 2 for n in cand]
    target = (L * L) // 2  # because we need sum = 1/2

    # Split at a value threshold to keep the second half small enough for full enumeration
    threshold = max_n // 2
    split_idx = 0
    for i, n in enumerate(cand):
        if n >= threshold:
            split_idx = i
            break

    first = sorted(
        weights[:split_idx], reverse=True
    )  # large weights first -> better pruning
    last = weights[split_idx:]

    # Precompute all subset sums of the last part
    sum_count: Dict[int, int] = defaultdict(int)
    sums = [0]
    for w in last:
        sums += [s + w for s in sums]
    for s in sums:
        sum_count[s] += 1
    max_last = sum(last)

    # Suffix sums for pruning on the first part
    suffix = [0] * (len(first) + 1)
    for i in range(len(first) - 1, -1, -1):
        suffix[i] = suffix[i + 1] + first[i]

    ans = 0

    def dfs(i: int, acc: int) -> None:
        nonlocal ans
        if acc > target:
            return
        # Even taking all remaining 'first' and all 'last', we still can't reach target.
        if acc + suffix[i] + max_last < target:
            return
        if i == len(first):
            ans += sum_count.get(target - acc, 0)
            return
        dfs(i + 1, acc + first[i])  # include
        dfs(i + 1, acc)  # exclude

    dfs(0, 0)
    return ans


def _asserts_from_statement() -> None:
    # Statement example:
    ex = [2, 3, 4, 5, 7, 12, 15, 20, 28, 35]
    s = sum(Fraction(1, n * n) for n in ex)
    assert s == Fraction(1, 2), s

    # Statement claim: exactly 3 ways using numbers between 2 and 45 inclusive.
    assert count_ways(45) == 3


def solve() -> int:
    return count_ways(80)


if __name__ == "__main__":
    _asserts_from_statement()
    ans = solve()
    print(ans)
