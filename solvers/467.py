#!/usr/bin/env python3
"""
Project Euler 467 - Superinteger

Compute f(10_000) mod 1_000_000_007.

No external libraries are used (standard library only).
"""

from __future__ import annotations

import math

MOD = 1_000_000_007


def digital_root(x: int) -> int:
    """Digital root for positive integers (returns 1..9)."""
    return 1 + (x - 1) % 9


def first_primes_and_composites(count: int) -> tuple[list[int], list[int]]:
    """
    Return (primes, composites) where:
      primes     = first `count` primes
      composites = first `count` composite numbers (starting at 4)
    """
    # Safe upper bound for the 10_000th prime is well below 200_000.
    # Keep it adaptive anyway.
    if count < 6:
        limit = 50
    else:
        # n (log n + log log n) is an upper bound for n-th prime for n>=6 (Dusart-like).
        limit = (
            int(count * (math.log(count) + math.log(math.log(count)))) + 3 * count + 100
        )
        limit = max(limit, 200_000)

    is_prime = bytearray(b"\x01") * (limit + 1)
    is_prime[0:2] = b"\x00\x00"
    r = math.isqrt(limit)
    for p in range(2, r + 1):
        if is_prime[p]:
            start = p * p
            step = p
            is_prime[start : limit + 1 : step] = b"\x00" * (
                ((limit - start) // step) + 1
            )

    primes: list[int] = []
    comps: list[int] = []
    for x in range(2, limit + 1):
        if is_prime[x]:
            primes.append(x)
        else:
            if x >= 4:
                comps.append(x)
        if len(primes) >= count and len(comps) >= count:
            break

    if len(primes) < count or len(comps) < count:
        raise RuntimeError("Sieve limit too small; increase limit.")

    return primes[:count], comps[:count]


def _build_lcs_rows(X: list[int], Y: list[int]) -> list[int]:
    """
    Bit-parallel LCS-length DP, storing the DP bitset after each prefix of Y.

    rows[b] is a bitset (Python int) representing the DP state after processing
    first b characters of Y, against the full X.

    This is the classic bit-vector LCS-length algorithm:
        U = D | matches[y]
        V = (U - ((D << 1) | 1)) mod 2^n
        D = U & ~V
    where D's popcount equals LCS length for full prefixes.
    """
    n = len(X)
    limit_mask = (1 << n) - 1

    matches = [0] * 10  # digits 1..9 are used
    for i, ch in enumerate(X):
        matches[ch] |= 1 << i

    rows = [0] * (len(Y) + 1)
    D = 0
    for b, ch in enumerate(Y, 1):
        U = D | matches[ch]
        V = (U - ((D << 1) | 1)) & limit_mask
        D = U & (limit_mask ^ V)  # equals U & ~V within n bits
        rows[b] = D
    return rows


def _prefix_masks(n: int) -> list[int]:
    """mask[a] has its lowest a bits set (a in [0..n])."""
    masks = [0] * (n + 1)
    cur = 0
    for a in range(1, n + 1):
        cur = (cur << 1) | 1
        masks[a] = cur
    return masks


def scs_value(A: list[int], B: list[int], want_string: bool = False) -> int | str:
    """
    Return the lexicographically smallest shortest common supersequence (SCS)
    of A and B, interpreted as:
      - mod value (base-10) if want_string == False
      - full digit string if want_string == True

    For this problem, A and B are digit sequences (1..9) of equal length.
    """
    n = len(A)
    if n != len(B):
        raise ValueError("A and B must have the same length for this solver.")

    # We need fast LCS lengths of suffixes A[i:], B[j:].
    # Reverse both strings so suffix queries become prefix queries.
    X = A[::-1]
    Y = B[::-1]

    rows = _build_lcs_rows(X, Y)  # rows[b] bitset for Y prefix length b
    pm = _prefix_masks(n)  # pm[a] mask for X prefix length a

    mod = 0
    out = [] if want_string else None

    i = j = 0
    while i < n and j < n:
        ai = A[i]
        bj = B[j]
        if ai == bj:
            d = ai
            i += 1
            j += 1
        else:
            # Compare LCS(A[i+1:], B[j:]) vs LCS(A[i:], B[j+1:])
            a1 = n - (i + 1)
            b1 = n - j
            if a1 <= 0 or b1 <= 0:
                l1 = 0
            else:
                l1 = (rows[b1] & pm[a1]).bit_count()

            a2 = n - i
            b2 = n - (j + 1)
            if a2 <= 0 or b2 <= 0:
                l2 = 0
            else:
                l2 = (rows[b2] & pm[a2]).bit_count()

            # Take the branch that keeps the LCS as large as possible (min SCS length).
            # If equal, take the smaller next digit (lexicographically smallest SCS).
            if l1 > l2 or (l1 == l2 and ai < bj):
                d = ai
                i += 1
            else:
                d = bj
                j += 1

        mod = (mod * 10 + d) % MOD
        if want_string:
            out.append(str(d))

    while i < n:
        d = A[i]
        i += 1
        mod = (mod * 10 + d) % MOD
        if want_string:
            out.append(str(d))

    while j < n:
        d = B[j]
        j += 1
        mod = (mod * 10 + d) % MOD
        if want_string:
            out.append(str(d))

    if want_string:
        return "".join(out)
    return mod


def main() -> None:
    N = 10_000
    primes, comps = first_primes_and_composites(N)

    PD = [digital_root(p) for p in primes]  # prime digital roots
    CD = [digital_root(c) for c in comps]  # composite digital roots

    # --- Tests from the problem statement ---
    assert "".join(map(str, PD[:10])) == "2357248152"
    assert "".join(map(str, CD[:10])) == "4689135679"
    assert scs_value(PD[:10], CD[:10], want_string=True) == "2357246891352679"
    assert scs_value(PD[:100], CD[:100], want_string=False) == 771661825

    # --- Final answer ---
    print(scs_value(PD, CD, want_string=False))


if __name__ == "__main__":
    main()
