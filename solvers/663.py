#!/usr/bin/env python3
"""Project Euler 663: Sums of Subarrays

This script prints the answer to:
  S(10_000_003, 10_200_000) - S(10_000_003, 10_000_000)

It also asserts all test values given in the problem statement.

No external (third‑party) libraries are used.
"""

from __future__ import annotations

from array import array


# Must fit in signed 64-bit for array('q')
NEG_INF = -(10**18)


def add_mod3(a: int, b: int, c: int, mod: int) -> int:
    """Return (a+b+c) % mod, assuming 0 <= a,b,c < mod.

    Since a+b+c < 3*mod, we can reduce using a few subtractions.
    """
    s = a + b + c
    if s >= mod:
        s -= mod
    if s >= mod:
        s -= mod
    if s >= mod:
        s -= mod
    return s


def _block_summary(A: array, start: int, end: int) -> tuple[int, int, int, int]:
    """Return (tot, pref, suff, best) for A[start:end] (non-empty subarrays)."""
    tot = 0
    pref = NEG_INF
    best = NEG_INF
    cur = NEG_INF

    for i in range(start, end):
        x = A[i]
        tot += x
        if tot > pref:
            pref = tot
        if cur == NEG_INF:
            cur = x
        else:
            y = cur + x
            cur = x if y < x else y
        if cur > best:
            best = cur

    suff = NEG_INF
    s = 0
    for i in range(end - 1, start - 1, -1):
        s += A[i]
        if s > suff:
            suff = s

    return tot, pref, suff, best


class MaxSubarrayByBlocks:
    """Maintain max subarray sum with point updates using block summaries + segment tree."""

    __slots__ = ("A", "n", "B", "nb", "base", "tot", "pref", "suff", "best")

    def __init__(self, A: array, B: int = 128):
        self.A = A
        self.n = len(A)
        self.B = B
        self.nb = (self.n + B - 1) // B
        self.base = 1 << (self.nb - 1).bit_length()

        size = 2 * self.base
        self.tot = array("q", [0]) * size
        self.pref = array("q", [0]) * size
        self.suff = array("q", [0]) * size
        self.best = array("q", [0]) * size

        # Initialize padding leaves as neutral elements
        # (won't affect combining for non-empty subarrays)
        for pos in range(self.base, self.base + self.base):
            self.pref[pos] = NEG_INF
            self.suff[pos] = NEG_INF
            self.best[pos] = NEG_INF

        # Fill real leaves with block summaries
        for bi in range(self.nb):
            start = bi * B
            end = start + B
            if end > self.n:
                end = self.n
            t, p, s, b = _block_summary(A, start, end)
            pos = self.base + bi
            self.tot[pos] = t
            self.pref[pos] = p
            self.suff[pos] = s
            self.best[pos] = b

        # Build internal nodes
        for i in range(self.base - 1, 0, -1):
            self._pull(i)

    def _pull(self, i: int) -> None:
        l = i * 2
        r = l + 1

        totL = self.tot[l]
        totR = self.tot[r]
        self.tot[i] = totL + totR

        prefL = self.pref[l]
        prefR = self.pref[r]
        x = totL + prefR
        self.pref[i] = prefL if prefL > x else x

        suffL = self.suff[l]
        suffR = self.suff[r]
        x = totR + suffL
        self.suff[i] = suffR if suffR > x else x

        bestL = self.best[l]
        bestR = self.best[r]
        cross = suffL + prefR
        m = bestL if bestL > bestR else bestR
        self.best[i] = m if m > cross else cross

    def point_add(self, idx: int, delta: int) -> None:
        """A[idx] += delta and update structure."""
        A = self.A
        A[idx] += delta

        B = self.B
        bi = idx // B
        start = bi * B
        end = start + B
        if end > self.n:
            end = self.n
        t, p, s, b = _block_summary(A, start, end)

        pos = self.base + bi
        self.tot[pos] = t
        self.pref[pos] = p
        self.suff[pos] = s
        self.best[pos] = b

        pos //= 2
        while pos:
            self._pull(pos)
            pos //= 2

    def max_subarray_sum(self) -> int:
        return int(self.best[1])


def simulate_small_S(n: int, l: int) -> int:
    """Direct simulation for small n,l.

    Keeps full array and runs Kadane each step (O(n*l)).
    Used only for asserts from the problem statement.
    """
    A = [0] * n

    a = 0
    b = 0
    c = 1 % n

    def step(idx: int, odd: int) -> int:
        A[idx] += 2 * odd - n + 1
        best = NEG_INF
        cur = NEG_INF
        for x in A:
            if cur == NEG_INF:
                cur = x
            else:
                y = cur + x
                cur = x if y < x else y
            if cur > best:
                best = cur
        return best

    total = 0

    # i = 1 uses (t0,t1) = (a,b)
    total += step(a, b)

    # shift once -> state for i=2 has (a,b,c) = (t1,t2,t3)
    d = add_mod3(a, b, c, n)
    a, b, c = b, c, d

    for _ in range(2, l + 1):
        total += step(b, c)
        # advance 2 tribonacci steps
        d = add_mod3(a, b, c, n)
        a, b, c = b, c, d
        d = add_mod3(a, b, c, n)
        a, b, c = b, c, d

    return total


def solve() -> int:
    # --- Asserts from the statement ---
    assert simulate_small_S(5, 6) == 32
    assert simulate_small_S(5, 100) == 2416
    assert simulate_small_S(14, 100) == 3881
    assert simulate_small_S(107, 1000) == 1618572

    # --- Main computation ---
    n = 10_000_003
    l1 = 10_000_000
    l2 = 10_200_000

    # Build A after l1 steps, without maintaining M_n(i)
    A = array("q", [0]) * n

    a = 0
    b = 0
    c = 1

    # i = 1 (uses t0,t1)
    A[a] += 2 * b - n + 1

    # shift once => state for i=2: (a,b,c) = (t1,t2,t3)
    d = add_mod3(a, b, c, n)
    a, b, c = b, c, d

    for _ in range(2, l1 + 1):
        A[b] += 2 * c - n + 1
        # advance two tribonacci steps
        d = add_mod3(a, b, c, n)
        a, b, c = b, c, d
        d = add_mod3(a, b, c, n)
        a, b, c = b, c, d

    # Now (b,c) correspond to (t_{2*l1} mod n, t_{2*l1+1} mod n),
    # i.e. the pair needed for step l1+1.

    # Data structure for M_n(i) (point updates)
    ds = MaxSubarrayByBlocks(A, B=128)

    total = 0
    for _ in range(l1 + 1, l2 + 1):
        idx = b
        delta = 2 * c - n + 1
        ds.point_add(idx, delta)
        total += ds.max_subarray_sum()

        # advance two tribonacci steps
        d = add_mod3(a, b, c, n)
        a, b, c = b, c, d
        d = add_mod3(a, b, c, n)
        a, b, c = b, c, d

    return total


def main() -> None:
    print(solve())


if __name__ == "__main__":
    main()
