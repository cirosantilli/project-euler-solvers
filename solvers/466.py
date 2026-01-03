#!/usr/bin/env python3
"""
Project Euler 466: Distinct Terms in a Multiplication Table

Compute P(m, n): the number of distinct values in an m×n multiplication table.
No external libraries are used.
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import Iterable, List, Tuple


def _lcm(a: int, b: int) -> int:
    return a // math.gcd(a, b) * b


def _minimal_under_divisibility(nums: Iterable[int]) -> Tuple[int, ...]:
    """
    Keep only elements that are not multiples of a smaller kept element.
    This preserves the union of multiples for inclusion-exclusion.
    """
    uniq = sorted(set(x for x in nums if x > 1))
    kept: List[int] = []
    for x in uniq:
        redundant = False
        for y in kept:
            if x % y == 0:
                redundant = True
                break
        if not redundant:
            kept.append(x)
    return tuple(kept)


def _forbidden_set(d: int, m: int) -> Tuple[int, ...]:
    """
    For products x with maximal divisor (<=m) equal to d, write x = d*r.
    Such an x would also have a larger divisor e (d<e<=m) iff e | d*r,
    which is equivalent to (e/gcd(e,d)) | r.

    So r must avoid being divisible by any value in this set.
    """
    return _minimal_under_divisibility(e // math.gcd(e, d) for e in range(d + 1, m + 1))


def _count_divisible_by_any(n: int, divisors: Tuple[int, ...]) -> int:
    """
    Count integers r in [1..n] divisible by at least one divisor in `divisors`,
    via inclusion-exclusion over lcms, using memoization.
    """
    if not divisors:
        return 0
    divs = tuple(x for x in divisors if x <= n)
    if not divs:
        return 0

    @lru_cache(maxsize=None)
    def ie(start: int, cur_lcm: int) -> int:
        total = 0
        for i in range(start, len(divs)):
            nl = _lcm(cur_lcm, divs[i])
            if nl > n:
                continue
            # Include subsets starting with this divisor, then exclude supersets
            total += (n // nl) - ie(i + 1, nl)
        return total

    return ie(0, 1)


def P(m: int, n: int) -> int:
    """
    Number of distinct products i*j with 1<=i<=m and 1<=j<=n.

    Key idea:
      Let d(x) = the largest divisor of x that is <= m.
      Then x appears in the table iff x/d(x) <= n.
      Each x has a unique d(x), so we can sum over d=1..m.

    For a fixed d, x=d*r with 1<=r<=n, and we must ensure no e in (d..m]
    divides x (otherwise d(x) would be larger). That becomes a divisibility
    avoidance problem on r.
    """
    if m <= 0 or n <= 0:
        return 0

    total = 0
    cache = {}  # forbidden_set -> count(divisible by any forbidden)
    for d in range(1, m + 1):
        fs = _forbidden_set(d, m)
        bad = cache.get(fs)
        if bad is None:
            bad = _count_divisible_by_any(n, fs)
            cache[fs] = bad
        total += n - bad
    return total


def main() -> None:
    # Test values from the problem statement
    assert P(3, 4) == 8
    assert P(64, 64) == 1263
    assert P(12, 345) == 1998
    assert P(32, 10**15) == 13826382602124302

    # Required answer
    print(P(64, 10**16))


if __name__ == "__main__":
    main()
