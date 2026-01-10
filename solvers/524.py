#!/usr/bin/env python3
"""
Project Euler 524 - First Sort II

We compute R(12^12).

No external libraries are used.

The key is a closed-form for F(P) (number of "move-to-front" operations),
and a constructive way to build the lexicographically first permutation
of {1..n} whose F-value equals k.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional, Tuple


# ----------------------------
# 1) Compute F(P) efficiently
# ----------------------------


class Fenwick:
    """Fenwick tree / BIT for prefix sums over 1..n."""

    __slots__ = ("n", "bit")

    def __init__(self, n: int) -> None:
        self.n = n
        self.bit = [0] * (n + 1)

    def add(self, i: int, delta: int) -> None:
        n = self.n
        bit = self.bit
        while i <= n:
            bit[i] += delta
            i += i & -i

    def sum(self, i: int) -> int:
        s = 0
        bit = self.bit
        while i > 0:
            s += bit[i]
            i -= i & -i
        return s


def F_value(p: Tuple[int, ...]) -> int:
    """
    Closed form for F(P):

    Scan left-to-right. Let M be the maximum seen so far.
    If x is a new maximum -> contributes 0.
    Otherwise let r = (# of earlier elements < x). Add 2^r.
    """
    n = len(p)
    if n <= 1:
        return 0
    ft = Fenwick(n)
    max_so_far = 0
    f = 0
    for x in p:
        if x > max_so_far:
            max_so_far = x
        else:
            r = ft.sum(x - 1)
            f += 1 << r
        ft.add(x, 1)
    return f


# -----------------------------------------
# 2) Lexicographic index I_n(P) in [1..n!]
# -----------------------------------------


def lex_index(p: Tuple[int, ...]) -> int:
    """1-based lexicographic rank of permutation p among all permutations of 1..n."""
    n = len(p)
    fact = [1] * (n + 1)
    for i in range(2, n + 1):
        fact[i] = fact[i - 1] * i

    avail = list(range(1, n + 1))
    rank = 1
    for i, x in enumerate(p):
        j = avail.index(x)
        rank += j * fact[n - 1 - i]
        avail.pop(j)
    return rank


# ---------------------------------------------------------
# 3) Construct lexicographically first permutation for (n,k)
# ---------------------------------------------------------


def _dfs_lex_first_hard(n: int, k: int) -> Tuple[int, ...]:
    """
    Fallback solver for the remaining (n,k) case:
      k odd, k < 2^(n-2), k % 4 == 3.

    We do a lexicographic DFS with memoization on (mask, remaining_k),
    plus strong min/max pruning computed per mask.
    This is fast for the small 'hard core' that appears in this problem.
    """
    full = (1 << n) - 1
    lower_mask = [0] * (n + 1)
    for v in range(1, n + 1):
        lower_mask[v] = (1 << (v - 1)) - 1

    @lru_cache(None)
    def min_max(mask: int) -> Tuple[int, int]:
        """
        Returns (min_possible, max_possible) extra F achievable from this prefix (mask).
        - current maximum is max used value = mask.bit_length()
        """
        if mask == full:
            return (0, 0)

        current_max = mask.bit_length()
        rem_vals = [v for v in range(1, n + 1) if not (mask >> (v - 1)) & 1]

        # Minimum: make as many future elements records as possible (those > current_max),
        # and for the forced non-records (<= current_max), order them decreasing so that
        # no additional smaller elements appear before them.
        mn = 0
        for v in rem_vals:
            if v <= current_max:
                base = (mask & lower_mask[v]).bit_count()
                mn += 1 << base

        # Maximum: if we can, place the largest remaining value first as a record,
        # then place the rest increasing (so each sees all smaller remaining values before it).
        if current_max == n:
            # already have the global max: everything remaining is forced non-record
            ordered = sorted(rem_vals)
            mx = 0
            for idx, v in enumerate(ordered):
                base = (mask & lower_mask[v]).bit_count()
                mx += 1 << (base + idx)
            return (mn, mx)

        vmax = max(rem_vals)
        ordered = sorted(v for v in rem_vals if v != vmax)
        mx = 0
        for idx, v in enumerate(ordered):
            base = (mask & lower_mask[v]).bit_count()
            mx += 1 << (base + idx)
        return (mn, mx)

    @lru_cache(None)
    def solve(mask: int, rem_k: int) -> Optional[Tuple[int, ...]]:
        if mask == full:
            return () if rem_k == 0 else None

        mn, mx = min_max(mask)
        if rem_k < mn or rem_k > mx:
            return None

        current_max = mask.bit_length()

        # Try smallest available value first to enforce lexicographic minimality.
        for v in range(1, n + 1):
            bit = 1 << (v - 1)
            if mask & bit:
                continue
            r = (mask & lower_mask[v]).bit_count()
            contrib = 0 if v > current_max else 1 << r
            if contrib > rem_k:
                continue
            suffix = solve(mask | bit, rem_k - contrib)
            if suffix is not None:
                return (v,) + suffix
        return None

    ans = solve(0, k)
    if ans is None:
        raise RuntimeError(f"No permutation exists for n={n}, k={k} (unexpected).")
    return ans


@lru_cache(None)
def lex_first_perm(n: int, k: int) -> Tuple[int, ...]:
    """
    Returns the lexicographically first permutation P of {1..n} with F(P) = k.

    The construction uses 3 proved structural recurrences; everything else
    falls back to the bounded DFS above.
    """
    if k == 0:
        return tuple(range(1, n + 1))
    if n <= 1:
        raise ValueError("k>0 requires n>=2")

    # (E) If k is even, the lex-first permutation starts with 1.
    if k & 1 == 0:
        p = lex_first_perm(n - 1, k >> 1)
        return (1,) + tuple(v + 1 for v in p)

    # (H) If k >= 2^(n-2), then bit (n-2) is set, which forces (n-1) to be last.
    high = 1 << (n - 2)
    if k >= high:
        p = lex_first_perm(n - 1, k - high)  # perm of {1..n-1}
        p2 = tuple(n if v == n - 1 else v for v in p)  # map max (n-1) -> n
        return p2 + (n - 1,)

    # (M1) If k ≡ 1 (mod 4), lex-first starts with 2,1 (can't start with 1, and 1 must be as early as possible).
    if (k & 3) == 1:
        p = lex_first_perm(n - 2, (k - 1) >> 2)
        return (2, 1) + tuple(v + 2 for v in p)

    # Remaining case: k odd, k < 2^(n-2), k ≡ 3 (mod 4).
    return _dfs_lex_first_hard(n, k)


# -----------------------------
# 4) Compute R(12^12)
# -----------------------------


def R(k: int) -> int:
    """
    R(k) = min(Q(n,k)) over all n where Q(n,k) is defined.
    For even k, we can prepend 1 and halve k without changing the rank,
    so we strip factors of 2 first.
    For the resulting odd k>0, the minimal feasible n is fixed (otherwise max F is too small),
    and larger n would make the rank at least (n-1)! which is larger, so the minimum is at that n.
    """
    if k == 0:
        return 1  # permutation (1) has rank 1

    # Strip factors of 2: R(2m) = R(m)
    while (k & 1) == 0:
        k >>= 1

    n = k.bit_length() + 1  # minimal n with 2^(n-1)-1 >= k
    p = lex_first_perm(n, k)
    return lex_index(p)


def _run_asserts() -> None:
    # Example from statement:
    assert F_value((4, 1, 3, 2)) == 5

    # Q(4,k) values from the statement's table:
    expected = {
        0: 1,
        1: 7,
        2: 3,
        3: 12,
        4: 2,
        5: 8,
        6: 5,
        7: 19,
    }
    for k, q in expected.items():
        p = lex_first_perm(4, k)
        assert F_value(p) == k
        assert lex_index(p) == q


def main() -> None:
    _run_asserts()
    ans = R(12**12)
    print(ans)


if __name__ == "__main__":
    main()
