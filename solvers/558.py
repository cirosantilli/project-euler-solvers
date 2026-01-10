#!/usr/bin/env python3
"""
Project Euler 558 - Irrational Base

We work with the unique representation of integers in base r (real root of r^3 = r^2 + 1)
using digits {0,1} with the spacing constraint: no two 1s occur within distance < 3.

The key operation is: "insert a 1 at exponent e and renormalize", implemented as a small
deterministic rewrite automaton (stack-based).

We compute:
  S(N) = sum_{n=1..N} w(n^2)
incrementally using n^2 = (n-1)^2 + (2n-1).

No external libraries are used.
"""

from __future__ import annotations
import sys


# We store a representation as a bitset in a Python int.
# Bit index i corresponds to exponent (i - SHIFT). We choose SHIFT big enough
# so all indices stay non-negative, and aligned to 8 bits (requested "8-bit").
SHIFT = 256  # exponent 0 lives at index SHIFT


def _build_pow2(limit: int) -> list[int]:
    """Precompute powers of two up to 'limit' inclusive."""
    return [1 << i for i in range(limit + 1)]


# Indices stay in a few hundred bits for N=5_000_000, but keep generous headroom.
_POW2 = _build_pow2(1400)


def _dfs_insert_many(bits: int, stack: list[int]) -> int:
    """
    Add 1 at each position in 'stack' to the canonical representation 'bits',
    renormalizing after each local rewrite.

    This is the exact automaton used by a known fast approach:
    it repeatedly rewrites around the insertion point using identities
    derived from r^3 = r^2 + 1, preserving the represented integer while
    maintaining the spacing constraint.
    """
    pow2 = _POW2
    pop = stack.pop
    append = stack.append

    while stack:
        x = pop()

        # The SHIFT choice guarantees x stays comfortably >= 7 for this problem size.
        # (If this ever fails, increase SHIFT.)
        # We keep this check cheap and only in debug-style form.
        if x < 7:
            raise RuntimeError(f"Index underflow at {x}; increase SHIFT")

        # Rewrite rules (same order as the canonical insertion algorithm)
        m = pow2[x + 2]
        if bits & m:
            bits ^= m
            append(x + 3)
            continue

        m = pow2[x - 2]
        if bits & m:
            bits ^= m
            append(x + 1)
            continue

        m = pow2[x - 1]
        if bits & m:
            bits ^= m
            append(x + 1)
            append(x - 4)
            continue

        m = pow2[x + 1]
        if bits & m:
            bits ^= m
            append(x + 2)
            append(x - 3)
            continue

        m = pow2[x]
        if bits & m:
            bits ^= m
            append(x + 1)
            append(x - 2)
            append(x - 7)
            continue

        # No conflicts: set the bit.
        bits |= m

    return bits


def _repr_of_int(n: int) -> int:
    """Return the canonical representation (as bitset int) of the ordinary integer n."""
    bits = 0
    stk: list[int] = []
    for _ in range(n):
        stk.clear()
        stk.append(SHIFT)
        bits = _dfs_insert_many(bits, stk)
    return bits


def w(n: int) -> int:
    """w(n) = number of terms (1-bits) in the canonical representation of integer n."""
    return _repr_of_int(n).bit_count()


def S(limit: int) -> int:
    """
    Compute S(limit) = sum_{i=1..limit} w(i^2) using:
        i^2 = (i-1)^2 + (2i-1)
    maintaining representations of the running odd increment and the running square.
    """
    f = 0  # representation of current odd number (2i-1)
    g = 0  # representation of i^2
    ans = 0

    stk_f: list[int] = []
    stk_g: list[int] = []

    dfs = _dfs_insert_many

    for i in range(1, limit + 1):
        # Update odd increment: f <- f + 2 (except the first step gives 1)
        stk_f.clear()
        stk_f.append(SHIFT)
        if i != 1:
            stk_f.append(SHIFT)
        f = dfs(f, stk_f)

        # Add f into g: g <- g + f  (f is sparse; push all its 1-bits into one stack)
        stk_g.clear()
        t = f
        while t:
            lsb = t & -t
            stk_g.append(lsb.bit_length() - 1)
            t ^= lsb
        g = dfs(g, stk_g)

        ans += g.bit_count()

    return ans


def solve(n: int = 5_000_000) -> int:
    return S(n)


def _self_test() -> None:
    # Examples from the statement:
    # 3 = r^{-10} + r^{-5} + r^{-1} + r^2  => w(3) = 4
    # 10 = r^{-10} + r^{-7} + r^6          => w(10) = 3
    assert w(3) == 4
    assert w(10) == 3

    # Also given: S(1000) = 19403
    assert S(1000) == 19403


if __name__ == "__main__":
    _self_test()
    n = 5_000_000
    if len(sys.argv) >= 2:
        n = int(sys.argv[1])
    print(solve(n))
