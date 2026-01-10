#!/usr/bin/env python3
"""
Project Euler 535 - Fractal Sequence

We work with the sequence S defined by:
- The first occurrence of each integer is "circled", and the circled values are 1,2,3,...
- Immediately before each non-circled value x there are exactly floor(sqrt(x)) adjacent circled values.
- Removing all circled values leaves a sequence identical to S (fractal / self-embedding).

Let T(n) be the sum of the first n terms of S. The task is to compute the last 9 digits of T(10^18).

No external libraries are used.
"""

from __future__ import annotations

import math


MOD = 10**9


def sum_1_to_m(m: int) -> int:
    """Sum of integers 1..m (m>=0)."""
    if m <= 0:
        return 0
    return m * (m + 1) // 2


def sum_floor_sqrt_1_to_m(m: int) -> int:
    """
    Sum_{k=1..m} floor(sqrt(k)) in O(1) time.

    Values with floor(sqrt(k)) = t occur for k in [t^2, (t+1)^2 - 1], count = 2t+1.
    """
    if m <= 0:
        return 0
    t = math.isqrt(m)

    # Full blocks for s = 1..t-1
    full = t - 1
    if full <= 0:
        # t == 1 => all terms have sqrt == 1
        return t * (m - t * t + 1)

    s1 = full * (full + 1) // 2
    s2 = full * (full + 1) * (2 * full + 1) // 6
    total = 2 * s2 + s1  # sum_{s=1..full} s*(2s+1)

    # Partial block for s = t
    total += t * (m - t * t + 1)
    return total


# Memo tables
_memo_phi: dict[int, int] = {0: 0, 1: 0}
_memo_g: dict[int, int] = {0: 0}  # G(n) = sum_{i<=n} floor(sqrt(S_i))
_memo_t: dict[int, int] = {0: 0}  # T(n) = sum_{i<=n} S_i


def phi(n: int) -> int:
    """
    Let phi(n) be the number of non-circled elements among the first n elements of S.

    The r-th non-circled element appears at position P(r) = r + G(r), so:
        phi(n) = max r such that r + G(r) <= n.

    Note: For n>=1, phi(n) <= n-1 (the very first element is circled).
    """
    if n in _memo_phi:
        return _memo_phi[n]
    if n <= 1:
        _memo_phi[n] = 0
        return 0

    lo, hi = 0, n  # r is in [0, n-1], hi is exclusive
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid + G(mid) <= n:
            lo = mid
        else:
            hi = mid

    _memo_phi[n] = lo
    return lo


def G(n: int) -> int:
    """
    G(n) = sum_{i=1..n} floor(sqrt(S_i)).

    In the first n terms:
    - There are m circled terms, whose values are exactly 1..m.
    - There are r = phi(n) non-circled terms, whose values (in order) are S_1..S_r.

    Therefore:
        G(n) = G(r) + sum_{k=1..m} floor(sqrt(k))
    where m = n - r.
    """
    if n in _memo_g:
        return _memo_g[n]
    r = phi(n)
    m = n - r
    _memo_g[n] = G(r) + sum_floor_sqrt_1_to_m(m)
    return _memo_g[n]


def T(n: int) -> int:
    """
    T(n) = sum_{i=1..n} S_i.

    Using the same decomposition as for G(n):
        T(n) = T(r) + sum_{k=1..m} k
    where r = phi(n) and m = n - r.
    """
    if n in _memo_t:
        return _memo_t[n]
    r = phi(n)
    m = n - r
    _memo_t[n] = T(r) + sum_1_to_m(m)
    return _memo_t[n]


def solve() -> int:
    # Test values from the problem statement
    assert T(1) == 1
    assert T(20) == 86
    assert T(10**3) == 364089
    assert T(10**9) == 498676527978348241

    # Problem asks for last 9 digits of T(10^18)
    ans = T(10**18) % MOD
    return ans


if __name__ == "__main__":
    print(f"{solve():09d}")
