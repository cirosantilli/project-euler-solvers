#!/usr/bin/env python3
"""Project Euler 399: Squarefree Fibonacci Numbers

Computes the 100,000,000th squarefree Fibonacci number under the assumption
stated in the problem (Wall's conjecture for prime squares in Fibonacci entry
points).

Output format:
  last sixteen digits, then a comma, then scientific notation rounded to 1 digit
  after the decimal point.

No external libraries are used (standard library only).
"""

from __future__ import annotations

import math
import sys
from collections import defaultdict

LAST16_MOD = 10**16


# ----------------------------- Fibonacci (fast doubling) -----------------------------


def fib_mod(n: int, mod: int) -> int:
    """Return F_n mod mod, with F_0 = 0, F_1 = 1."""
    a, b = 0, 1
    # Process bits from MSB to LSB.
    for bit in range(n.bit_length() - 1, -1, -1):
        # (a, b) = (F_k, F_{k+1})
        two_b_minus_a = (2 * b - a) % mod
        c = (a * two_b_minus_a) % mod  # F_{2k}
        d = (a * a + b * b) % mod  # F_{2k+1}
        if (n >> bit) & 1:
            a, b = d, (c + d) % mod
        else:
            a, b = c, d
    return a


def fib_big(n: int) -> int:
    """Return exact F_n as Python int, with F_0 = 0, F_1 = 1."""
    a, b = 0, 1
    for bit in range(n.bit_length() - 1, -1, -1):
        c = a * (2 * b - a)
        d = a * a + b * b
        if (n >> bit) & 1:
            a, b = d, c + d
        else:
            a, b = c, d
    return a


# ----------------------------- Number theory helpers -----------------------------


def primes_upto(n: int) -> list[int]:
    """Simple sieve of Eratosthenes."""
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    limit = int(n**0.5)
    for i in range(2, limit + 1):
        if sieve[i]:
            step = i
            start = i * i
            sieve[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i in range(2, n + 1) if sieve[i]]


def unique_prime_factors_small(n: int, small_primes: list[int]) -> list[int]:
    """Return the unique prime factors of n (n is expected to be <= a few million)."""
    factors: list[int] = []
    x = n
    for p in small_primes:
        if p * p > x:
            break
        if x % p == 0:
            factors.append(p)
            while x % p == 0:
                x //= p
    if x > 1:
        factors.append(x)
    return factors


def legendre_symbol_5(p: int) -> int:
    """Legendre symbol (5/p) for odd prime p != 5; returns +1 or -1."""
    r = pow(5, (p - 1) // 2, p)
    return 1 if r == 1 else -1


def rank_of_apparition_prime(p: int, small_primes: list[int]) -> int:
    """Compute z(p): smallest n >= 1 such that p | F_n.

    Uses the well-known fact that for prime p != 5:
      z(p) divides p - (5/p), where (5/p) is the Legendre symbol.

    Then reduces that candidate by testing divisors using Fibonacci mod p.
    """
    if p == 2:
        return 3
    if p == 5:
        return 5

    s = legendre_symbol_5(p)
    cand = p - 1 if s == 1 else p + 1
    d = cand

    for q in unique_prime_factors_small(cand, small_primes):
        while d % q == 0 and fib_mod(d // q, p) == 0:
            d //= q

    return d


# ----------------------------- Core counting logic -----------------------------


def prime_upper_bound_for_moduli(nmax: int) -> int:
    """Upper bound for primes p that can satisfy p*z(p) <= nmax.

    If z(p) = k then p divides F_k, so p <= F_k and also p <= nmax/k.
    Thus p <= max_k min(F_k, nmax/k).

    For nmax in this problem's range, the maximum occurs at modest k.
    """
    a, b = 0, 1
    best = 0
    for k in range(1, 200):
        a, b = b, a + b
        fk = a
        best = max(best, min(fk, nmax // k))
        # Once fk is huge and nmax//k is dropping, there's no chance to beat best.
        if k > 60 and (nmax // k) <= best:
            break
    return best


def build_moduli(nmax: int) -> list[int]:
    """Build the list of moduli m(p) = z(p^2) = p*z(p) <= nmax.

    The equality z(p^2) = p*z(p) is exactly the assumption requested by the
    problem statement (a consequence of Wall's conjecture).

    We also remove redundant moduli that are multiples of smaller ones.
    """
    pmax = prime_upper_bound_for_moduli(nmax)

    primes = primes_upto(pmax)
    small_primes = primes_upto(int((pmax + 1) ** 0.5) + 1)

    mods: list[int] = []
    for p in primes:
        zp = rank_of_apparition_prime(p, small_primes)
        m = p * zp
        if m <= nmax:
            mods.append(m)

    mods.sort()

    # Remove moduli that are multiples of smaller moduli (they add no new forbidden indices).
    filtered: list[int] = []
    for m in mods:
        redundant = False
        for k in filtered:
            if m % k == 0:
                redundant = True
                break
        if not redundant:
            filtered.append(m)

    return filtered


def build_lcm_coefficients(mods: list[int], nmax: int) -> tuple[list[int], list[int]]:
    """Precompute inclusion-exclusion coefficients grouped by LCM.

    We count squarefree Fibonacci indices up to N by:
      count(N) = sum_{S subset mods} (-1)^{|S|} floor(N / lcm(S))
    (with the empty subset contributing lcm=1, sign=+1).

    Many different subsets can share the same LCM; we accumulate their signs.
    """
    mods = [m for m in mods if m <= nmax]
    L = len(mods)

    coeff = defaultdict(int)
    coeff[1] = 1

    sys.setrecursionlimit(10000)

    def dfs(start: int, lcm_val: int, sign: int) -> None:
        for i in range(start, L):
            m = mods[i]
            if lcm_val % m == 0:
                # Including m would not change the LCM; such branches cancel in inclusion-exclusion.
                continue

            g = math.gcd(lcm_val, m)
            nl = (lcm_val // g) * m
            if nl > nmax:
                continue

            s = -sign
            coeff[nl] += s
            dfs(i + 1, nl, s)

    dfs(0, 1, 1)

    items = sorted(coeff.items())
    lcms = [k for (k, _) in items]
    coeffs = [v for (_, v) in items]
    return lcms, coeffs


def count_squarefree_indices_upto(n: int, lcms: list[int], coeffs: list[int]) -> int:
    total = 0
    for L, c in zip(lcms, coeffs):
        total += c * (n // L)
    return total


def kth_squarefree_index(k: int, nmax: int, lcms: list[int], coeffs: list[int]) -> int:
    """Return the smallest index n such that there are at least k squarefree Fibonacci numbers in F_1..F_n."""
    if count_squarefree_indices_upto(nmax, lcms, coeffs) < k:
        raise ValueError("nmax too small for requested k")

    lo, hi = 1, nmax
    while lo < hi:
        mid = (lo + hi) // 2
        if count_squarefree_indices_upto(mid, lcms, coeffs) >= k:
            hi = mid
        else:
            lo = mid + 1
    return lo


def format_fibonacci_answer(n: int) -> str:
    """Return output string for Fibonacci number F_n per the problem statement."""
    last16 = fib_mod(n, LAST16_MOD)

    # F_n ≈ phi^n / sqrt(5)
    phi = (1.0 + 5.0**0.5) / 2.0
    log10F = n * math.log10(phi) - 0.5 * math.log10(5.0)

    exp = int(math.floor(log10F))
    mant = 10.0 ** (log10F - exp)
    mant_rounded = round(mant, 1)
    if mant_rounded >= 10.0:
        mant_rounded = 1.0
        exp += 1

    return f"{last16:016d},{mant_rounded:.1f}e{exp}"


# ----------------------------- Tests from the statement -----------------------------


def is_squarefree_int(x: int) -> bool:
    """Squarefree test for small integers (used only for tiny statement examples)."""
    n = x
    p = 2
    while p * p <= n:
        if n % p == 0:
            n //= p
            if n % p == 0:
                return False
            while n % p == 0:
                n //= p
        p += 1 if p == 2 else 2
    return True


def run_statement_asserts(lcms: list[int], coeffs: list[int], nmax: int) -> None:
    # First 15 Fibonacci numbers (F_1..F_15)
    fib15 = []
    a, b = 1, 1
    for _ in range(15):
        fib15.append(a)
        a, b = b, a + b
    assert fib15 == [1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610]

    # First 13 squarefree Fibonacci numbers
    sqfree = [v for v in fib15 if is_squarefree_int(v)]
    assert sqfree == [1, 1, 2, 3, 5, 13, 21, 34, 55, 89, 233, 377, 610]

    # 200th squarefree Fibonacci number example
    n200 = kth_squarefree_index(200, nmax, lcms, coeffs)
    assert n200 == 260  # implied by the given 200th value

    F200 = fib_big(n200)
    assert F200 == int("971183874599339129547649988289594072811608739584170445")

    sample = format_fibonacci_answer(n200)
    assert sample == "1608739584170445,9.7e53"


# ----------------------------- Solve PE399 -----------------------------


def solve(k: int = 100_000_000) -> str:
    # A safe upper bound for the index needed for k=100,000,000.
    # (The actual index is ~1.31e8; nmax=2e8 is comfortably above.)
    nmax = 200_000_000

    mods = build_moduli(nmax)
    lcms, coeffs = build_lcm_coefficients(mods, nmax)

    run_statement_asserts(lcms, coeffs, nmax)

    n = kth_squarefree_index(k, nmax, lcms, coeffs)
    return format_fibonacci_answer(n)


def main() -> None:
    k = 100_000_000
    if len(sys.argv) > 1:
        k = int(sys.argv[1])
    print(solve(k))


if __name__ == "__main__":
    main()
