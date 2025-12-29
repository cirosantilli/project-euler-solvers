#!/usr/bin/env python3
"""Project Euler 276: Primitive Triangles.

Consider integer-sided triangles (a, b, c) with a <= b <= c.
An integer-sided triangle (a,b,c) is called primitive if gcd(a,b,c)=1.

How many primitive integer-sided triangles exist with a perimeter not exceeding
10_000_000?

This program prints the answer.
"""

from __future__ import annotations

from array import array

LIMIT = 10_000_000

# --- Counting (not-necessarily-primitive) integer triangles up to perimeter n ---
#
# Let t(p) be the number of integer-sided triangles with *exact* perimeter p
# (counted with a<=b<=c). A classical result gives:
#   t(p) = round(p^2/48)             if p is even
#   t(p) = round((p+3)^2/48)         if p is odd
# For positive integers, "round" can be done as (x + denom/2)//denom.
#
# We also need the cumulative count A(n) = sum_{p<=n} t(p).
# With a change of variables p=2m and p=2m+1, one can show:
#   A(n) = S(n//2) + S((n+1)//2 + 1)
# where S(m) = sum_{k=1..m} floor((k^2 + 6)/12).
#
# S(m) is computed in O(1) using the identity:
#   floor((k^2+6)/12) = (k^2+6 - ((k^2+6) mod 12)) / 12
# The remainder ((k^2+6) mod 12) depends only on k mod 6.

# Prefix sums of r(k) = (k^2+6) % 12 for k = 1..6:
# k: 1  2  3  4  5  6
# r: 7 10  3 10  7  6
_REM_PREFIX = (0, 7, 17, 20, 30, 37, 43)  # prefix sums over 0..6
_REM_CYCLE_SUM = 43


def _sum_k2(m: int) -> int:
    """Sum of squares: 1^2 + 2^2 + ... + m^2."""
    return m * (m + 1) * (2 * m + 1) // 6


def _sum_rem(m: int) -> int:
    """Sum_{k=1..m} ((k^2+6) mod 12), using period 6."""
    q, r = divmod(m, 6)
    return q * _REM_CYCLE_SUM + _REM_PREFIX[r]


def _S(m: int) -> int:
    """S(m) = sum_{k=1..m} floor((k^2 + 6)/12) computed in O(1)."""
    if m <= 0:
        return 0
    return (_sum_k2(m) + 6 * m - _sum_rem(m)) // 12


def triangles_with_perimeter(p: int) -> int:
    """t(p): number of integer-sided triangles with exact perimeter p."""
    if p & 1:
        t = p + 3
        return (t * t + 24) // 48
    return (p * p + 24) // 48


def triangles_upto(n: int) -> int:
    """A(n): number of integer-sided triangles with perimeter <= n."""
    return _S(n // 2) + _S((n + 1) // 2 + 1)


# --- Extract primitive triangles via Möbius inversion ---
#
# Every triangle has gcd d>=1; dividing sides by d gives a primitive triangle.
# Let P(N) be the number of primitive triangles with perimeter <= N.
# Then the number of triangles with all sides divisible by d is A(N//d).
# By Möbius inversion:
#   P(N) = sum_{d=1..N} mu(d) * A(N//d)
# We compute the summatory Möbius function M(n) = sum_{k<=n} mu(k) with a
# linear sieve, and evaluate the above sum in O(sqrt(N)) using divisor grouping.


def mobius_prefix(n: int) -> array:
    """Return M where M[x] = sum_{k<=x} mu(k) for 0<=x<=n."""
    mu = array("b", [0]) * (n + 1)
    mu[1] = 1
    is_comp = bytearray(n + 1)
    primes: list[int] = []

    mu_local = mu
    is_comp_local = is_comp
    primes_append = primes.append

    for i in range(2, n + 1):
        if not is_comp_local[i]:
            primes_append(i)
            mu_local[i] = -1
        mi = mu_local[i]
        for p in primes:
            ip = i * p
            if ip > n:
                break
            is_comp_local[ip] = 1
            if i % p == 0:
                mu_local[ip] = 0
                break
            mu_local[ip] = -mi

    M = array("i", [0]) * (n + 1)
    s = 0
    for i in range(1, n + 1):
        s += mu_local[i]
        M[i] = s
    return M


def primitive_triangles_upto(n: int) -> int:
    """P(n): number of primitive integer triangles with perimeter <= n."""
    M = mobius_prefix(n)
    A = triangles_upto

    ans = 0
    l = 1
    while l <= n:
        q = n // l
        r = n // q
        ans += (M[r] - M[l - 1]) * A(q)
        l = r + 1
    return ans


def solve(limit: int = LIMIT) -> int:
    return primitive_triangles_upto(limit)


if __name__ == "__main__":
    # Problem statement does not include explicit sample outputs,
    # but we add small sanity checks for the known triangle-count formula.
    assert triangles_with_perimeter(1) == 0
    assert triangles_with_perimeter(3) == 1
    assert triangles_with_perimeter(7) == 2
    assert triangles_upto(10) == 11
    assert primitive_triangles_upto(10) == 8

    print(solve())
