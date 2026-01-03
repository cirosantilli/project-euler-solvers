#!/usr/bin/env python3
"""
Project Euler 384: Rudin-Shapiro Sequence

Compute:
    sum_{t=2..45} GF(t), where GF(t) = g(F(t), F(t-1)),
    F(0)=F(1)=1, F(n)=F(n-1)+F(n-2).

The key is a fast recursion for g(t,c) (the index where value t occurs
for the c-th time in the Rudin–Shapiro summatory sequence s(n)).
"""

from __future__ import annotations


def a_adjacent_ones(n: int) -> int:
    """a(n): number of (overlapping) '11' blocks in the binary expansion of n."""
    if n < 0:
        raise ValueError("n must be non-negative")
    return (n & (n >> 1)).bit_count()


def b_rudin_shapiro(n: int) -> int:
    """b(n) = (-1)^{a(n)} in {+1,-1}."""
    return -1 if (a_adjacent_ones(n) & 1) else 1


def s_summatory(n: int) -> int:
    """s(n) = sum_{i=0..n} b(i). Only used for small self-tests."""
    if n < 0:
        raise ValueError("n must be non-negative")
    total = 0
    for i in range(n + 1):
        total += b_rudin_shapiro(i)
    return total


def g_index(t: int, c: int) -> int:
    """
    g(t,c): index n in s(n) where value t occurs for the c-th time.
    Assumes 1 <= c <= t and t >= 1.

    Runs in O(log t) via a self-similar decomposition by the highest power of two <= t.
    """
    if t < 1:
        raise ValueError("t must be >= 1")
    if not (1 <= c <= t):
        raise ValueError("c must satisfy 1 <= c <= t")

    # Base: value 1 occurs once, at index 0 (s(0)=1).
    if t == 1:
        return 0

    h = 1 << (t.bit_length() - 1)  # highest power of 2 <= t
    d = t - h

    if d == 0:
        # t is a power of two
        if c <= t // 2:
            return t * t // 4 + g_index(t // 2, c)
        else:
            return t * t // 2 + g_index(t, c - t // 2)

    # General case, as a function of (h,d,c)
    if c > h:
        return h * h + g_index(2 * h - d, c - h)
    elif c > h - d:
        return h * h + g_index(d, c + d - h)
    elif c <= d:
        return h * h // 2 + g_index(d, c)
    else:
        return h * h // 2 + g_index(2 * h - t, c)


def solve() -> int:
    # --- Problem-statement test values ---
    # a(n) examples
    assert a_adjacent_ones(5) == 0  # 101_2
    assert a_adjacent_ones(6) == 1  # 110_2
    assert a_adjacent_ones(7) == 2  # 111_2

    # Table for n=0..7
    a_expected = [0, 0, 0, 1, 0, 0, 1, 2]
    b_expected = [1, 1, 1, -1, 1, 1, -1, 1]
    s_expected = [1, 2, 3, 2, 3, 4, 3, 4]
    for n in range(8):
        assert a_adjacent_ones(n) == a_expected[n]
        assert b_rudin_shapiro(n) == b_expected[n]
        assert s_summatory(n) == s_expected[n]

    # g(t,c) examples
    assert g_index(3, 3) == 6
    assert g_index(4, 2) == 7
    assert g_index(54321, 12345) == 1220847710

    # --- Main computation ---
    F = [1, 1]
    for _ in range(2, 46):
        F.append(F[-1] + F[-2])

    total = 0
    for t in range(2, 46):
        total += g_index(F[t], F[t - 1])

    return total


if __name__ == "__main__":
    print(solve())
