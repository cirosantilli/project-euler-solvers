#!/usr/bin/env python3
"""
Project Euler 242 - Odd Triplets

We define f(n, k) as the number of k-element subsets of {1,2,...,n} having an odd sum.
An "odd-triplet" is [n, k, f(n,k)] where n, k, and f(n,k) are all odd.

This script prints the number of odd-triplets with n <= 10^12 (or a user-supplied N).
"""

from __future__ import annotations

import sys
from math import comb


def f_small(n: int, k: int) -> int:
    """Exact f(n,k) for small n using the defining combinatorial sum."""
    if k < 0 or k > n:
        return 0
    # odds: 1,3,5,... ; evens: 2,4,6,...
    o = (n + 1) // 2
    e = n // 2
    total = 0
    # odd sum <=> choose an odd number of odd elements
    for j in range(1, k + 1, 2):
        if j <= o and k - j <= e:
            total += comb(o, j) * comb(e, k - j)
    return total


def prefix_sum_pow2_popcount(t: int) -> int:
    """
    Compute F(t) = sum_{x=0..t} 2^{popcount(x)} in O(bitlength(t)) time.

    Uses:
      - For a full block [0, 2^m - 1], sum is 3^m (each bit contributes factor 1 or 2).
      - For [2^m, 2^m + r], contributions equal 2 * F(r) (leading bit adds +1 popcount).
    """
    if t < 0:
        return 0
    res = 0
    mult = 1
    while True:
        if t == 0:
            res += mult
            break
        m = t.bit_length() - 1
        p = 1 << m
        if t == p - 1:
            res += mult * pow(3, m)
            break
        res += mult * pow(3, m)
        t -= p
        mult *= 2
    return res


def count_odd_triplets_upto(n_max: int) -> int:
    """
    Count odd-triplets [n,k,f(n,k)] with n <= n_max.

    Key result:
      - If n ≡ 3 (mod 4), then f(n,k) is even for all k.
      - If n = 4t + 1, then f(n,k) is odd (with k odd) iff (k-1) is a bit-subset of (n-1),
        so the number of valid k for this n equals 2^{popcount(n-1)} = 2^{popcount(t)}.
      - Therefore the total count is sum_{t=0..T} 2^{popcount(t)} where T = floor((n_max - 1)/4).
    """
    if n_max <= 0:
        return 0
    t_max = (n_max - 1) // 4
    return prefix_sum_pow2_popcount(t_max)


def _run_problem_statement_asserts() -> None:
    # Given example
    assert f_small(5, 3) == 4

    # "There are exactly five odd-triplets with n ≤ 10, namely: ..."
    expected = [(1, 1, 1), (5, 1, 3), (5, 5, 1), (9, 1, 5), (9, 9, 1)]
    found = []
    for n in range(1, 11):
        for k in range(1, n + 1):
            v = f_small(n, k)
            if (n & 1) and (k & 1) and (v & 1):
                found.append((n, k, v))
    assert found == expected
    assert count_odd_triplets_upto(10) == 5


def main(argv: list[str]) -> None:
    _run_problem_statement_asserts()

    n_max = 10**12
    if len(argv) >= 2:
        n_max = int(argv[1])
    print(count_odd_triplets_upto(n_max))


if __name__ == "__main__":
    main(sys.argv)
