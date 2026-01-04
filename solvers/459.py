#!/usr/bin/env python3
"""
Project Euler 459 - Flipping Game

Pure Python solution (no external libraries).

Core idea:
- Use Sprague–Grundy theory + Pearson's "tartan theorem" to reduce the 2D game to a nim-product of two 1D
  coin-turning games (square-length moves and triangular-length moves).
- Count winning first moves by counting 1D strips by nimber (frequency tables), then matching pairs whose
  nim-product equals the nimber of the full board.
"""

from __future__ import annotations

import math
import sys
from array import array
from typing import List, Tuple, Dict


# We only ever need nimbers up to 1023 for strip values for this problem instance.
# (The 1D C_k values stay <= 512 for N=10^6, so strip XORs stay <= 1023.)
M = 1024

# Fermat 2-powers: F_n = 2^(2^n) = 1 << (1<<n)
# We'll support nim multiplication for values up to about 2^32 safely (more if needed).
FERMAT: List[int] = [1 << (1 << n) for n in range(0, 7)]  # up to 2^(64) for safety


def _fermat_index(x: int) -> int:
    """Largest i such that FERMAT[i] <= x, assuming x >= 1."""
    # FERMAT is tiny (<= 7), linear scan is fine.
    i = 0
    # F_0 = 2, so for x=1 this would be wrong; we won't call with x<2 except trivial base cases.
    while i + 1 < len(FERMAT) and FERMAT[i + 1] <= x:
        i += 1
    return i


_nim_mul_cache: Dict[Tuple[int, int], int] = {}


def nim_mul(a: int, b: int) -> int:
    """
    Nim-product (nimber multiplication) for nonnegative integers.

    Uses the recursive Fermat 2-power splitting algorithm described by Mike Earnest:
    https://math.stackexchange.com/a/3712540

    Works for all a,b >= 0 within practical range (here well below 2^64).
    """
    if a == 0 or b == 0:
        return 0
    if a == 1:
        return b
    if b == 1:
        return a
    if a < b:
        a, b = b, a
    key = (a, b)
    r = _nim_mul_cache.get(key)
    if r is not None:
        return r

    # Find largest Fermat power <= each operand
    m = _fermat_index(a)  # so F_m <= a < F_{m+1}
    n = _fermat_index(b)

    if m != n:
        # Ensure n is the larger index
        if m > n:
            # a = a1*F_m + a2, with b < F_m
            Fm = FERMAT[m]
            shift = 1 << m
            a1, a2 = divmod(a, Fm)
            r = (nim_mul(a1, b) << shift) ^ nim_mul(a2, b)
        else:
            # b = b1*F_n + b2, with a < F_n
            Fn = FERMAT[n]
            shift = 1 << n
            b1, b2 = divmod(b, Fn)
            r = (nim_mul(a, b1) << shift) ^ nim_mul(a, b2)
    else:
        # m == n, use the derived Karatsuba-style formula
        Fn = FERMAT[n]
        shift = 1 << n
        a1, a2 = divmod(a, Fn)
        b1, b2 = divmod(b, Fn)

        p1 = nim_mul(a1, b1)
        p2 = nim_mul(a2, b2)
        p3 = nim_mul(a1 ^ a2, b1 ^ b2)
        p4 = nim_mul(p1, Fn >> 1)  # p1 * (Fn/2)
        p5 = p3 ^ p2               # a1b1 + a1b2 + a2b1

        r = (p5 << shift) ^ p2 ^ p4

    _nim_mul_cache[key] = r
    return r


def nim_pow(a: int, e: int) -> int:
    """Exponentiation under nim-product."""
    res = 1
    base = a
    exp = e
    while exp:
        if exp & 1:
            res = nim_mul(res, base)
        exp >>= 1
        if exp:
            base = nim_mul(base, base)
    return res


def nim_inv_2_16(a: int) -> int:
    """
    Multiplicative inverse of a (a != 0) in the nimber field of size 2^16.

    For this problem, all strip nimbers are < 1024, hence < 2^16, so inverses live in this field.
    In GF(2^16), a^(2^16-2) = a^65534 is the inverse.
    """
    if a == 0:
        raise ZeroDivisionError("0 has no multiplicative inverse in nimbers")
    # 2^16 - 2 = 65534
    return nim_pow(a, 65534)


def make_squares_upto(n: int) -> List[int]:
    r = int(math.isqrt(n))
    return [k * k for k in range(1, r + 1)]


def make_triangles_upto(n: int) -> List[int]:
    out = []
    k = 1
    while True:
        t = k * (k + 1) // 2
        if t > n:
            break
        out.append(t)
        k += 1
    return out


def compute_1d_prefix_and_freq(n: int, lengths: List[int], verbose: bool = False) -> Tuple[array, array]:
    """
    Computes:
      - C[x] for x=0..n where C[x] is the XOR prefix of the 1D nim-values (see Pearson),
      - freq[v] = number of contiguous strips (with allowed lengths) whose nimber is v.

    The recurrence:
        C[x] = C[x-1] XOR mex( { C[x-1] XOR C[x-L] : L in lengths, L <= x } )
    and a strip of length L ending at x has nimber:
        strip = C[x] XOR C[x-L]

    Implementation detail:
    - 'mark' stores a timestamp (the current x) when a value was seen, to avoid clearing arrays.
    - We also count multiplicities of candidate values at each x, then update strip frequencies
      with one pass over distinct candidates (avoids re-indexing C twice).
    """
    C = array('H', [0]) * (n + 1)  # values stay < 1024
    freq = array('Q', [0]) * M

    mark = [0] * M     # timestamp (current x) if present
    cnt = [0] * M      # multiplicity for current x
    touched = [0] * M  # distinct values touched at current x

    m = 0
    L = lengths
    Llen = len(L)

    for x in range(1, n + 1):
        # increase m so that L[:m] are the allowable lengths <= x
        while m < Llen and L[m] <= x:
            m += 1

        cx_prev = C[x - 1]
        tlen = 0

        # Build the reachable set S = { cx_prev XOR C[x-L] }
        # and track counts for each value in S.
        for j in range(m):
            v = cx_prev ^ C[x - L[j]]
            if mark[v] != x:
                mark[v] = x
                cnt[v] = 1
                touched[tlen] = v
                tlen += 1
            else:
                cnt[v] += 1

        # mex of S
        t = 0
        while mark[t] == x:
            t += 1

        cx = cx_prev ^ t
        C[x] = cx

        # Update strip frequency: strip = cx XOR C[x-L] = (cx_prev XOR C[x-L]) XOR t = v XOR t
        for i in range(tlen):
            v = touched[i]
            freq[v ^ t] += cnt[v]

        if verbose and (x % 100000 == 0):
            print(f"  processed x={x}/{n}", file=sys.stderr)

    return C, freq


def W(n: int, verbose: bool = False) -> int:
    squares = make_squares_upto(n)
    triangles = make_triangles_upto(n)

    C_sq, freq_sq = compute_1d_prefix_and_freq(n, squares, verbose=verbose)
    C_tr, freq_tr = compute_1d_prefix_and_freq(n, triangles, verbose=verbose)

    board = nim_mul(int(C_sq[n]), int(C_tr[n]))

    # Count pairs (a,b) with a ⊗ b = board.
    # Use division via inverse in GF(2^16).
    total = 0
    sum_sq = int(sum(freq_sq))
    sum_tr = int(sum(freq_tr))

    if board == 0:
        # In a field, a⊗b=0 iff a==0 or b==0
        a0 = int(freq_sq[0])
        b0 = int(freq_tr[0])
        total = a0 * sum_tr + (sum_sq - a0) * b0
        return total

    inv_cache: Dict[int, int] = {}
    for a in range(1, M):
        fa = int(freq_sq[a])
        if fa == 0:
            continue
        inva = inv_cache.get(a)
        if inva is None:
            inva = nim_inv_2_16(a)
            inv_cache[a] = inva
        b = nim_mul(board, inva)
        if b < M:
            total += fa * int(freq_tr[b])

    return total


def main() -> None:
    verbose = ("--verbose" in sys.argv)

    # Tests from the problem statement
    assert W(1) == 1
    assert W(2) == 0
    assert W(5) == 8
    assert W(100) == 31395

    print(W(1_000_000, verbose=verbose))


if __name__ == "__main__":
    main()
