#!/usr/bin/env python3
"""
Project Euler 328: Lowest-cost Search

We must compute S(N) = sum_{n=1..N} C(n), where C(n) is the minimal worst-case
total "guess cost" when searching for a hidden number in {1..n}.

This implementation uses a well-known structural property of optimal strategies:
for the optimal first guess k (often close to n), the *right* subproblem (k+1..n)
is solved by a "complete" (balanced) search tree, whose cost can be computed
very fast for any interval via memoized coefficients.
"""

from __future__ import annotations

from bisect import bisect_left
from functools import lru_cache


# Precompute g = (2^t - 1) for the complete-tree recursion.
# Needs to cover lengths up to at least 200000.
_G = []
_x = 1
while _x < 400000:
    _G.append(_x)
    _x = _x * 2 + 1


@lru_cache(maxsize=None)
def _complete_coeff(L: int) -> tuple[int, int]:
    """
    Return (m, c) such that the worst-case cost of the *complete-tree* strategy on
    the interval [a, a+L] (inclusive) equals m*a + c, for any integer a.

    Here L = (hi - lo) is the interval difference; the interval size is L+1.
    """
    if L <= 0:
        return (0, 0)
    if L == 1:
        # [a, a+1]: ask 'a' (worst-case cost = a)
        return (1, 0)
    if L == 2:
        # [a, a+2]: ask 'a+1' (worst-case cost = a+1)
        return (1, 1)

    # Pick the median-like pivot of the complete search tree.
    # Let t = largest (2^k - 1) strictly less than L.
    idx = bisect_left(_G, L)  # _G[idx] >= L
    t = _G[idx - 1]

    # Pivot offset d (so pivot is at a + d)
    d = min(t, L - (t - 1) // 2)

    L_left = d - 1
    L_right = L - d - 1

    m1, c1 = _complete_coeff(L_left)
    m2, c2 = _complete_coeff(L_right)

    # Right subtree starts at (a + d + 1), so its constant term shifts.
    right_const = c2 + m2 * (d + 1)

    # Worst-case is max(left, right). Its dominating branch is independent of 'a'
    # because slopes differ by at most 1 (complete-tree structure).
    if m1 > m2:
        m_dom, c_dom = m1, c1
    elif m2 > m1:
        m_dom, c_dom = m2, right_const
    else:
        # Equal slopes => pick the larger constant term.
        if c1 >= right_const:
            m_dom, c_dom = m1, c1
        else:
            m_dom, c_dom = m2, right_const

    # Total cost = pivot (a+d) + dominating_subtree_cost
    return (m_dom + 1, d + c_dom)


def _complete_cost(lo: int, hi: int) -> int:
    """Complete-tree worst-case cost on [lo..hi], inclusive."""
    L = hi - lo
    m, c = _complete_coeff(L)
    return m * lo + c


def solve(limit: int = 200000) -> int:
    """
    Compute sum_{n=1..limit} C(n).

    We build C(n) incrementally. Let dist(n) = n - k(n) where k(n) is the optimal
    first guess for size n. Empirically and provably for this problem, dist(n)
    changes only near powers of two, so we only test a small set of candidate
    distances around dist(n-1).

    For each candidate first guess k, we evaluate:
        cost(k) = k + max( C(k-1), complete_cost(k+1, n) )
    and take the minimum.
    """
    if limit <= 0:
        return 0

    # C[n] = C(n). Keep C[0]=0 as a convenience (empty set).
    C = [0] * (limit + 1)

    # Seed exact small values (these also help bootstrap the incremental search).
    # These are consistent with the optimal strategy definition.
    seed = {1: 0, 2: 1, 3: 2, 4: 4, 5: 6, 6: 8}
    for n, v in seed.items():
        if n <= limit:
            C[n] = v
    if limit <= 6:
        return sum(C[1 : limit + 1])

    # For n=6, an optimal first guess is k=3, so dist = n-k = 3.
    dist = 3

    # Candidate "perturbations" around dist: 0, 4, 8, 16, ...
    q = [0]
    p = 4
    while p <= 131072:
        q.append(p)
        p *= 2

    # Controls how many q-values we consider. Grows very slowly with dist.
    i = 2

    running_sum = sum(C[1:7])

    for n in range(7, limit + 1):
        if dist > 4**i:
            i += 1

        best_cost = None
        best_dist = None

        for delta in q[:i]:
            k = n - dist - delta
            if not (0 < k < n):
                continue

            left = C[k - 1]
            right = 0 if k == n else _complete_cost(k + 1, n)
            worst = left if left > right else right
            total = k + worst

            new_dist = dist + delta
            if best_cost is None or total < best_cost:
                best_cost = total
                best_dist = new_dist

        if best_cost is None or best_dist is None:
            raise RuntimeError("No valid candidate pivot found (unexpected).")

        C[n] = best_cost
        dist = best_dist
        running_sum += best_cost

    return running_sum


def _self_test() -> None:
    # Test values from the problem statement.
    assert solve(1) == 0  # C(1)
    assert solve(2) == 1  # C(1)+C(2)=1 => C(2)=1
    assert solve(3) == 3  # 0+1+2

    # Direct C(n) checks:
    # (Compute via prefix differences)
    def Cn(n: int) -> int:
        return solve(n) - solve(n - 1)

    assert Cn(1) == 0
    assert Cn(2) == 1
    assert Cn(3) == 2
    assert Cn(8) == 12
    assert Cn(100) == 400
    assert solve(100) == 17575


if __name__ == "__main__":
    _self_test()
    print(solve(200000))
