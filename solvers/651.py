#!/usr/bin/env python3
"""
Project Euler 651 - Patterned Cylinders

Counts colourings of an a×b sticker grid on an infinite cylinder with axial period a
and circumference b, modulo 1_000_000_007, up to cylinder symmetries.

No external libraries are used.
"""

from __future__ import annotations

import math
from collections import defaultdict

MOD = 1_000_000_007


def sieve(limit: int) -> list[int]:
    """Simple prime sieve up to `limit` (inclusive)."""
    if limit < 2:
        return []
    bs = bytearray(b"\x01") * (limit + 1)
    bs[0:2] = b"\x00\x00"
    r = int(limit**0.5)
    for i in range(2, r + 1):
        if bs[i]:
            step = i
            start = i * i
            bs[start : limit + 1 : step] = b"\x00" * (((limit - start) // step) + 1)
    return [i for i in range(limit + 1) if bs[i]]


# Fibonacci numbers used here are <= F_40 = 102,334,155, so sqrt(n) < 20,000 is enough.
PRIMES = sieve(20_000)


def factorize(n: int) -> dict[int, int]:
    """Prime factorization of n (n <= ~1e8 here). Returns {prime: exponent}."""
    f: dict[int, int] = {}
    x = n
    for p in PRIMES:
        if p * p > x:
            break
        if x % p == 0:
            e = 0
            while x % p == 0:
                x //= p
                e += 1
            f[p] = e
    if x > 1:
        f[x] = f.get(x, 0) + 1
    return f


def divisors_and_phi(factors: dict[int, int]) -> list[tuple[int, int]]:
    """
    Enumerate all divisors d of n (given by `factors`) together with Euler's totient φ(d).

    Uses the multiplicativity of φ and the closed form for prime powers:
      φ(p^k) = 1                if k = 0
      φ(p^k) = p^k - p^(k-1)    if k >= 1
    """
    res = [(1, 1)]
    for p, e in factors.items():
        new: list[tuple[int, int]] = []
        pk = 1
        for k in range(e + 1):
            if k == 0:
                phi_pk = 1
            else:
                # phi(p^k) = p^(k-1) * (p-1)
                phi_pk = (pk // p) * (p - 1)
            for d, ph in res:
                new.append((d * pk, ph * phi_pk))
            pk *= p
        res = new
    return res


def dihedral_types(n: int) -> list[tuple[dict[int, int], int]]:
    """
    Return a list of (cycle_length_counts, multiplicity) for the action of D_n on n positions.

    cycle_length_counts is a dict {cycle_length: number_of_cycles}.
    multiplicity is the number of group elements in D_n having that cycle structure.

    D_n has:
      - n rotations: shift by k, whose cycles all have length L = n/gcd(n,k)
      - n reflections: depending on parity of n
    """
    fac = factorize(n)
    div_phi = divisors_and_phi(fac)

    types: list[tuple[dict[int, int], int]] = []

    # Rotations: for each divisor L of n, there are φ(L) rotations with cycle length L,
    # and number of cycles is n/L.
    for L, phiL in div_phi:
        types.append(({L: n // L}, phiL))

    # Reflections:
    if n % 2 == 1:
        # 1 fixed point, (n-1)/2 transpositions
        types.append(({1: 1, 2: (n - 1) // 2}, n))
    else:
        # n/2 reflections through opposite vertices: 2 fixed points
        types.append(({1: 2, 2: (n - 2) // 2}, n // 2))
        # n/2 reflections through opposite edges: no fixed points
        types.append(({2: n // 2}, n // 2))

    return types


def cycles_on_grid(dist_a: dict[int, int], dist_b: dict[int, int]) -> int:
    """
    Given cycle decompositions of permutations on Z_a and Z_b, compute the number of cycles
    of the induced permutation on Z_a × Z_b.

    If σ has cycles of lengths r_i and τ has cycles of lengths s_j, then on pairs:
      #cycles(σ×τ) = sum_{i,j} gcd(r_i, s_j).
    """
    total = 0
    for la, ca in dist_a.items():
        for lb, cb in dist_b.items():
            total += ca * cb * math.gcd(la, lb)
    return total


def surjections_count(cycles: int, m: int, comb: list[int]) -> int:
    """
    Number of colourings fixed by a permutation with `cycles` cycles that use exactly m
    labelled colours, modulo MOD.

    Each cycle must be monochromatic, so it's the number of surjections from `cycles`
    cycle-positions to m colours:
      surj(cycles, m) = sum_{k=0..m} (-1)^k * C(m,k) * (m-k)^cycles.
    """
    s = 0
    for k in range(m + 1):
        base = m - k
        term = comb[k] * pow(base, cycles, MOD)
        if k & 1:
            s -= term
        else:
            s += term
    return s % MOD


def f(m: int, a: int, b: int) -> int:
    """
    Compute f(m, a, b) as defined in Project Euler 651, modulo MOD.

    Uses Burnside's lemma over G = D_a × D_b (size 4ab).
    """
    types_a = dihedral_types(a)
    types_b = dihedral_types(b)

    # Aggregate weights by number of induced cycles on the a×b grid.
    weights: dict[int, int] = defaultdict(int)
    for dist_a, mult_a in types_a:
        for dist_b, mult_b in types_b:
            c = cycles_on_grid(dist_a, dist_b)
            weights[c] = (weights[c] + (mult_a * mult_b) % MOD) % MOD

    comb = [math.comb(m, k) for k in range(m + 1)]
    num = 0
    cache: dict[int, int] = {}
    for c, w in weights.items():
        val = cache.get(c)
        if val is None:
            val = surjections_count(c, m, comb)
            cache[c] = val
        num = (num + w * val) % MOD

    den = (4 * (a % MOD) * (b % MOD)) % MOD
    return num * pow(den, MOD - 2, MOD) % MOD


def fibonacci_upto(n: int) -> list[int]:
    F = [0, 1]
    for _ in range(2, n + 1):
        F.append(F[-1] + F[-2])
    return F


def solve() -> int:
    # Asserts from the problem statement:
    assert f(2, 2, 3) == 11
    assert f(3, 2, 3) == 56
    assert f(2, 3, 4) == 156
    assert f(8, 13, 21) == 49718354
    assert f(13, 144, 233) == 907081451

    F = fibonacci_upto(40)

    ans = 0
    for i in range(4, 41):
        ans = (ans + f(i, F[i - 1], F[i])) % MOD
    return ans


if __name__ == "__main__":
    print(solve())
