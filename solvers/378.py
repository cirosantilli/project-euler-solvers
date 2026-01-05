#!/usr/bin/env python3
"""
Project Euler 378 — Triangle Triples

Let T(n) = n(n+1)/2 be the nth triangular number.
Let dT(n) be the number of divisors of T(n).
Let Tr(n) be the number of triples (i, j, k) with 1 ≤ i < j < k ≤ n and
dT(i) > dT(j) > dT(k).

Compute Tr(60_000_000) and output the last 18 digits.
No external libraries are used.
"""

from __future__ import annotations

from array import array
from math import isqrt
import sys


MOD_18 = 10**18


def _build_divisor_counts(limit: int) -> array:
    """
    Build tau[x] = number of divisors of x for x in [0..limit].

    This uses:
      - a sieve storing smallest prime factor for odd composites only
      - a one-pass recurrence to compute tau and exponent-of-spf arrays

    Memory notes:
      - tau fits in unsigned short ('H') for limit <= 60_000_001 (max tau <= 1536).
      - exponent fits in unsigned char ('B').
    """
    # Smallest prime factor for odd numbers only:
    # spf_odd[n >> 1] corresponds to odd n, storing its smallest prime factor if composite, else 0.
    spf_odd = array("I", [0]) * ((limit >> 1) + 1)

    root = isqrt(limit)
    for p in range(3, root + 1, 2):
        if spf_odd[p >> 1] == 0:  # p is prime
            step = p << 1
            start = p * p
            for m in range(start, limit + 1, step):
                idx = m >> 1
                if spf_odd[idx] == 0:
                    spf_odd[idx] = p

    tau = array("H", [0]) * (limit + 1)
    exp = array("B", [0]) * (
        limit + 1
    )  # exponent of smallest prime factor in factorization

    tau[1] = 1
    for x in range(2, limit + 1):
        if x & 1 == 0:
            # x is even, smallest prime factor is 2
            m = x >> 1
            if m & 1 == 0:
                # 2 still divides m; increase exponent of 2
                e = exp[m] + 1
                exp[x] = e
                tau[x] = (tau[m] // e) * (e + 1)
            else:
                # exponent of 2 is 1
                exp[x] = 1
                tau[x] = tau[m] * 2
        else:
            p = spf_odd[x >> 1]
            if p == 0:
                # x is prime
                exp[x] = 1
                tau[x] = 2
            else:
                m = x // p
                if m % p == 0:
                    e = exp[m] + 1
                    exp[x] = e
                    tau[x] = (tau[m] // e) * (e + 1)
                else:
                    exp[x] = 1
                    tau[x] = tau[m] * 2

    return tau


def _dT(n: int, tau: array) -> int:
    """
    dT(n) = number of divisors of T(n) = n(n+1)/2.

    Since gcd(n, n+1) = 1, we can split the factor 2 to keep the two factors coprime:
      - if n is even: T(n) = (n/2) * (n+1) so dT(n) = tau[n/2] * tau[n+1]
      - if n is odd : T(n) = n * ((n+1)/2) so dT(n) = tau[n] * tau[(n+1)/2]
    """
    if n & 1 == 0:
        return tau[n >> 1] * tau[n + 1]
    return tau[n] * tau[(n + 1) >> 1]


def triangle_triples(
    n: int, *, checkpoints: set[int] | None = None
) -> tuple[int, dict[int, int]]:
    """
    Return (Tr(n), checkpoint_values). checkpoint_values maps each checkpoint m to Tr(m).

    Counting strategy:
      Let a_i = dT(i). We count strict decreasing subsequences of length 3.
      Maintain two Fenwick (BIT) structures over "value axis" (a_i):
        - bit1[v] = count of seen elements with value v
        - bit2[v] = count of decreasing pairs (i,j) seen so far with middle value == v,
                    i.e. a_i > a_j and j is the second index.

      When reading next value x=a_k:
        pairs_ending_at_k = #seen values > x  = seen - prefix(bit1, x)
        triples_ending_at_k = #seen pairs with middle value > x = total_pairs - prefix(bit2, x)

      Update:
        total_pairs += pairs_ending_at_k
        bit2.add(x, pairs_ending_at_k)
        bit1.add(x, 1)
    """
    if n < 3:
        return 0, {}

    tau = _build_divisor_counts(n + 1)

    # Fenwick trees (1-indexed). dT values are small enough that direct indexing is feasible.
    # Start with 2^16 and grow if needed.
    size = 1 << 16
    bit1 = [0] * (size + 1)  # counts (<= n fits in int)
    bit2 = [0] * (size + 1)  # pair counts (<= n*(n-1)/2 fits in int)

    def prefix_sum(bit: list[int], idx: int) -> int:
        s = 0
        while idx:
            s += bit[idx]
            idx &= idx - 1
        return s

    def add(bit: list[int], idx: int, delta: int) -> None:
        nonlocal size
        while idx <= size:
            bit[idx] += delta
            idx += idx & -idx

    want = checkpoints or set()
    got: dict[int, int] = {}

    seen = 0
    total_pairs = 0
    ans = 0

    for i in range(1, n + 1):
        x = _dT(i, tau)

        # Grow BIT arrays if we ever exceed the current capacity.
        if x > size:
            new_size = 1 << x.bit_length()
            bit1.extend([0] * (new_size - size))
            bit2.extend([0] * (new_size - size))
            size = new_size

        # pairs ending here
        leq = prefix_sum(bit1, x)
        pairs_here = seen - leq

        # triples ending here
        pairs_leq = prefix_sum(bit2, x)
        triples_here = total_pairs - pairs_leq
        ans += triples_here

        # update structures
        total_pairs += pairs_here
        add(bit2, x, pairs_here)
        add(bit1, x, 1)
        seen += 1

        if i in want:
            got[i] = ans

    return ans, got


def solve(n: int = 60_000_000) -> int:
    tr, _ = triangle_triples(n)
    return tr % MOD_18


def _self_test() -> None:
    # Uses the values given in the problem statement.
    tr_1000, got = triangle_triples(1000, checkpoints={20, 100, 1000})
    assert got[20] == 14
    assert got[100] == 5772
    assert got[1000] == 11174776
    assert tr_1000 == 11174776

    # Also from the statement: T(7)=28 has 6 divisors.
    # We can compute dT(7) via a tiny precompute.
    tau = _build_divisor_counts(8)
    assert _dT(7, tau) == 6


def main(argv: list[str]) -> None:
    _self_test()

    if len(argv) >= 2:
        if argv[1].lower() in {"test", "--test"}:
            print("ok")
            return
        n = int(argv[1].replace("_", ""))
    else:
        n = 60_000_000

    print(solve(n))


if __name__ == "__main__":
    main(sys.argv)
