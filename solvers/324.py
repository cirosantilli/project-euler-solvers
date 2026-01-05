#!/usr/bin/env python3
"""Project Euler 324: Building a Tower

Let f(n) be the number of ways to fill a 3×3×n tower with 2×1×1 blocks.
Blocks may be rotated arbitrarily; symmetries of the *tower* are counted as
*distinct*.

We need:
    f(10^10000) mod 100000007

Solution strategy
-----------------
1) Profile DP over slices of thickness 1 along the tower axis.
   Each slice has 9 cells, so the "boundary" state is a 9-bit mask describing
   which cells in the current slice are already occupied by dominoes that
   started in the previous slice (i.e., oriented along the axis).

   For each input mask (0..511), we recursively enumerate all ways to fill the
   remaining cells using:
     - dominoes inside the slice (x/y directions), or
     - dominoes pointing forward (z direction), which set bits in the *next*
       slice's mask.

   This yields a transition list mask -> [(next_mask, count), ...].

2) Only even n are tileable (3×3×n has 9n cells; must be even), so we define:
       a(m) = f(2m)
   We generate a moderate number of initial a(m) values modulo MOD via the DP.

3) Berlekamp–Massey over the prime field MOD finds the shortest linear
   recurrence for a(m) modulo MOD.

4) Kitamasa (polynomial exponentiation) evaluates the recurrence at
   m = (10^10000)/2 = 5·10^9999 in O(k^2 log m) time (k = recurrence order).

The code also asserts the example values from the problem statement.
"""

from __future__ import annotations

from collections import defaultdict
from typing import DefaultDict, Dict, List, Sequence, Tuple

MOD = 100000007
FULL = (1 << 9) - 1  # 9 bits for a 3x3 slice
BIT_TO_INDEX = {1 << i: i for i in range(9)}


def build_transitions() -> List[List[Tuple[int, int]]]:
    """Build transitions for all 512 masks.

    For each mask (occupied cells in current slice), enumerate all completions
    of the slice with dominoes, returning counts for resulting next_mask.
    """

    def transitions_for_mask(mask: int) -> List[Tuple[int, int]]:
        out: DefaultDict[int, int] = defaultdict(int)

        def dfs(occ: int, next_mask: int) -> None:
            if occ == FULL:
                out[next_mask] += 1
                return

            empty = FULL ^ occ
            lowbit = empty & -empty
            i = BIT_TO_INDEX[lowbit]
            bit = lowbit

            # Place a domino forward (along the tower axis): occupy this cell now
            # and the same cell in the next slice.
            dfs(occ | bit, next_mask | bit)

            # Place a domino to the right (within slice)
            if i % 3 != 2:
                bitx = bit << 1
                if not (occ & bitx):
                    dfs(occ | bit | bitx, next_mask)

            # Place a domino downward (within slice)
            if i < 6:
                bity = bit << 3
                if not (occ & bity):
                    dfs(occ | bit | bity, next_mask)

        dfs(mask, 0)
        return list(out.items())

    return [transitions_for_mask(m) for m in range(1 << 9)]


def compute_a_terms(num_terms: int, trans: List[List[Tuple[int, int]]]) -> List[int]:
    """Compute a(m) = f(2m) for m=0..num_terms-1 (mod MOD) using the slice DP."""

    if num_terms <= 0:
        return []

    max_slices = 2 * (num_terms - 1)
    dp = [0] * (1 << 9)
    dp[0] = 1

    a = [1]  # a(0) = f(0) = 1

    for n in range(1, max_slices + 1):
        nxt = [0] * (1 << 9)
        for mask, val in enumerate(dp):
            if not val:
                continue
            for next_mask, count in trans[mask]:
                nxt[next_mask] = (nxt[next_mask] + val * count) % MOD
        dp = nxt
        if n % 2 == 0:
            a.append(dp[0])

    return a


def modinv(x: int, mod: int = MOD) -> int:
    # MOD is prime, so x^(MOD-2) is the inverse.
    return pow(x, mod - 2, mod)


def berlekamp_massey(seq: Sequence[int], mod: int = MOD) -> List[int]:
    """Berlekamp–Massey over a prime modulus.

    Returns recurrence coefficients rec of length L such that for all n >= L:
        seq[n] = sum_{i=1..L} rec[i-1] * seq[n-i]  (mod mod)
    """

    C = [1]
    B = [1]
    L = 0
    m = 1
    b = 1

    for n in range(len(seq)):
        # discrepancy d = sum_{i=0..L} C[i] * seq[n-i]
        d = 0
        for i in range(L + 1):
            d = (d + C[i] * seq[n - i]) % mod

        if d == 0:
            m += 1
            continue

        T = C.copy()
        coef = d * modinv(b, mod) % mod

        needed = len(B) + m
        if len(C) < needed:
            C += [0] * (needed - len(C))

        for i in range(len(B)):
            C[i + m] = (C[i + m] - coef * B[i]) % mod

        if 2 * L <= n:
            L = n + 1 - L
            B = T
            b = d
            m = 1
        else:
            m += 1

    # Convert connection polynomial to forward recurrence coefficients
    return [(-C[i]) % mod for i in range(1, L + 1)]


def kitamasa_nth(
    init: Sequence[int], rec: Sequence[int], n: int, mod: int = MOD
) -> int:
    """Compute the n-th term of a linear recurrence in O(k^2 log n).

    rec length k defines:
        a(t) = rec[0]*a(t-1) + ... + rec[k-1]*a(t-k)
    init must contain at least k initial terms a(0..k-1).
    """

    k = len(rec)
    if n < k:
        return init[n] % mod

    def mul(p: List[int], q: List[int]) -> List[int]:
        # Multiply polynomials p and q (both degree<k), then reduce using
        # x^k = rec[0]x^(k-1)+...+rec[k-1].
        tmp = [0] * (2 * k - 1)
        for i in range(k):
            pi = p[i]
            if not pi:
                continue
            for j in range(k):
                qj = q[j]
                if qj:
                    tmp[i + j] = (tmp[i + j] + pi * qj) % mod

        for d in range(2 * k - 2, k - 1, -1):
            val = tmp[d]
            if not val:
                continue
            # x^d = val * x^(d-k) * x^k
            #     = val * sum_{i=1..k} rec[i-1] * x^(d-i)
            for i in range(1, k + 1):
                tmp[d - i] = (tmp[d - i] + val * rec[i - 1]) % mod

        return tmp[:k]

    # Exponentiate the polynomial x (mod characteristic) to power n.
    res = [1] + [0] * (k - 1)  # x^0
    if k == 1:
        base = [rec[0] % mod]  # x ≡ rec[0]
    else:
        base = [0] * k
        base[1] = 1  # x

    e = n
    while e:
        if e & 1:
            res = mul(res, base)
        e >>= 1
        if e:
            base = mul(base, base)

    ans = 0
    for coeff, v in zip(res, init[:k]):
        ans = (ans + coeff * v) % mod
    return ans


def f_mod(n: int, init: Sequence[int], rec: Sequence[int]) -> int:
    """Compute f(n) mod MOD."""

    if n & 1:
        return 0
    return kitamasa_nth(init, rec, n // 2, MOD)


def main() -> None:
    trans = build_transitions()

    # Generate enough even terms a(m)=f(2m) to infer a short recurrence.
    a_terms = compute_a_terms(120, trans)
    rec = berlekamp_massey(a_terms, MOD)
    k = len(rec)
    init = a_terms[:k]

    # Sanity-check the inferred recurrence against the computed prefix.
    for i in range(k, len(a_terms)):
        pred = 0
        for j, c in enumerate(rec, start=1):
            pred = (pred + c * a_terms[i - j]) % MOD
        assert pred == a_terms[i]

    # Asserts from the problem statement (q = 100000007)
    assert f_mod(2, init, rec) == 229
    assert f_mod(4, init, rec) == 117805
    assert f_mod(10, init, rec) == 96149360
    assert f_mod(10**3, init, rec) == 24806056
    assert f_mod(10**6, init, rec) == 30808124

    # Target: f(10^10000) mod 100000007.
    # Only even n are tileable, so f(10^10000) = a((10^10000)/2) = a(5*10^9999).
    index = 5 * (10**9999)
    print(kitamasa_nth(init, rec, index, MOD))


if __name__ == "__main__":
    main()
