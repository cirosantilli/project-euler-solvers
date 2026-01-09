#!/usr/bin/env python3
"""
Project Euler 626 - Counting Binary Matrices

We count n×n binary matrices up to:
- row permutations
- column permutations
- row flips (bitwise complement of a row)
- column flips

Let c(n) be the number of equivalence classes (orbits). We compute c(20) mod 1_001_001_011.

No external libraries are used.
"""

from __future__ import annotations

from math import gcd
from typing import Dict, Generator, List, Tuple

MOD = 1_001_001_011


def v2(x: int) -> int:
    """2-adic valuation: exponent of 2 in x."""
    c = 0
    while x % 2 == 0:
        x //= 2
        c += 1
    return c


def max_v2_upto(n: int) -> int:
    """max v2(k) for 1<=k<=n."""
    t = 0
    p = 1
    while p * 2 <= n:
        p *= 2
        t += 1
    return t


def partitions(n: int, max_part: int | None = None) -> Generator[List[int], None, None]:
    """Generate integer partitions of n as non-increasing lists."""
    if max_part is None or max_part > n:
        max_part = n
    if n == 0:
        yield []
        return
    for first in range(min(max_part, n), 0, -1):
        for rest in partitions(n - first, first):
            yield [first] + rest


class PartInfo:
    __slots__ = ("lens_mults", "k_cycles", "tmin", "prefix_lt", "count_mod")

    def __init__(
        self,
        lens_mults: List[Tuple[int, int]],
        k_cycles: int,
        tmin: int,
        prefix_lt: List[int],
        count_mod: int,
    ):
        # lens_mults: list of (cycle_length, multiplicity), sorted by cycle_length
        self.lens_mults = lens_mults
        self.k_cycles = k_cycles
        self.tmin = tmin
        # prefix_lt[t] = number of cycles with v2(length) < t
        self.prefix_lt = prefix_lt
        # number of permutations of this cycle type, modulo MOD
        self.count_mod = count_mod


def precompute_factorials(n: int, mod: int) -> Tuple[List[int], List[int]]:
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = (fact[i - 1] * i) % mod

    invfact = [1] * (n + 1)
    invfact[n] = pow(fact[n], mod - 2, mod)  # MOD is prime in this problem
    for i in range(n, 0, -1):
        invfact[i - 1] = (invfact[i] * i) % mod
    return fact, invfact


def build_part_infos(n: int, mod: int) -> Tuple[List[PartInfo], List[int]]:
    """Enumerate all partitions of n and compute the needed metadata for each."""
    fact, invfact = precompute_factorials(n, mod)
    inv_int = [0] * (n + 1)
    for i in range(1, n + 1):
        inv_int[i] = pow(i, mod - 2, mod)

    tmax = max_v2_upto(n)

    infos: List[PartInfo] = []
    for p in partitions(n):
        counts: Dict[int, int] = {}
        for x in p:
            counts[x] = counts.get(x, 0) + 1

        lens_mults = sorted(counts.items())
        k_cycles = len(p)
        tmin = min(v2(length) for length in counts)

        count_v2 = [0] * (tmax + 1)
        for length, mult in counts.items():
            count_v2[v2(length)] += mult

        prefix_lt = [0] * (tmax + 2)
        s = 0
        for t in range(tmax + 1):
            s += count_v2[t]
            prefix_lt[t + 1] = s

        # number of permutations with this cycle type:
        # n! / ∏_l (l^{m_l} * m_l!)
        count_mod = fact[n]
        for length, mult in counts.items():
            count_mod = (count_mod * pow(inv_int[length], mult, mod)) % mod
            count_mod = (count_mod * invfact[mult]) % mod

        infos.append(PartInfo(lens_mults, k_cycles, tmin, prefix_lt, count_mod))

    return infos, fact


def c_mod(n: int, mod: int = MOD) -> int:
    """Compute c(n) modulo mod."""
    infos, fact = build_part_infos(n, mod)

    # Precompute gcd table and powers of two up to n*n
    gcd_tab = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, n + 1):
            gcd_tab[i][j] = gcd(i, j)

    pow2 = [1] * (n * n + 1)
    for i in range(1, n * n + 1):
        pow2[i] = (pow2[i - 1] * 2) % mod

    total = 0
    for pr in infos:
        for pc in infos:
            # cycles of the product permutation π_r × π_c acting on positions (i,j)
            cycles = 0
            for lr, mr in pr.lens_mults:
                for lc, mc in pc.lens_mults:
                    cycles += mr * mc * gcd_tab[lr][lc]

            tr, tc = pr.tmin, pc.tmin
            if tr < tc:
                d = pr.prefix_lt[tc]  # row cycles with v2 < tc
            elif tc < tr:
                d = pc.prefix_lt[tr]  # col cycles with v2 < tr
            else:
                d = 1

            e = cycles - pr.k_cycles - pc.k_cycles + d
            term = pr.count_mod * pc.count_mod
            term %= mod
            term = (term * pow2[e]) % mod
            total += term
            total %= mod

    inv_fact_n = pow(fact[n], mod - 2, mod)
    inv_den = (inv_fact_n * inv_fact_n) % mod  # 1/(n!)^2
    return (total * inv_den) % mod


def main() -> None:
    # Test values given in the problem statement
    assert c_mod(3) == 3
    assert c_mod(5) == 39
    assert c_mod(8) == 656108

    print(c_mod(20))


if __name__ == "__main__":
    main()
