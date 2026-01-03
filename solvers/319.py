#!/usr/bin/env python3
"""Project Euler 319: Bounded Sequences

Let x_1, x_2, ..., x_n be a sequence of length n of integers such that:
  * x_1 = 2
  * x_1 < x_2 < ... < x_n
  * for all i,j: (x_i)^j < (x_j + 1)^i

Let t(n) be the number of such sequences.

We need t(10^10) mod 10^9.

This implementation follows a standard number-theory approach:
  * Convert the inequality into a "floor(alpha^k)" representation.
  * Count how many distinct boundary points (alpha where alpha^k is integer) exist.
  * Use Möbius inversion and a fast Mertens-function (summatory Möbius) sieve to
    evaluate the resulting sum in ~O(n^(2/3)) preprocessing and ~O(sqrt(n)) queries.
"""

from __future__ import annotations

from array import array
from functools import lru_cache


MOD = 10**9


def _integer_cuberoot_floor(n: int) -> int:
    """Return floor(n^(1/3)) for n >= 0."""
    if n < 0:
        raise ValueError("n must be non-negative")
    # Float seed + correction (safe for n=1e10; corrected by loop anyway)
    x = int(round(n ** (1.0 / 3.0)))
    while (x + 1) ** 3 <= n:
        x += 1
    while x**3 > n:
        x -= 1
    return x


def _linear_sieve_mobius_prefix(limit: int) -> tuple[array, array]:
    """Return (mu, prefix_mu) for 0..limit using a linear sieve.

    mu is stored as signed bytes (-1, 0, 1).
    prefix_mu[i] = sum_{k=1..i} mu[k] stored as 32-bit signed ints.
    """
    if limit < 1:
        raise ValueError("limit must be >= 1")

    is_comp = bytearray(limit + 1)
    mu = array("b", [0]) * (limit + 1)
    mu[1] = 1
    primes: list[int] = []

    for i in range(2, limit + 1):
        if not is_comp[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            ip = i * p
            if ip > limit:
                break
            is_comp[ip] = 1
            if i % p == 0:
                mu[ip] = 0
                break
            mu[ip] = -mu[i]

    pref = array("i", [0]) * (limit + 1)
    s = 0
    for i in range(1, limit + 1):
        s += mu[i]
        pref[i] = s
    return mu, pref


class Mertens:
    """Fast summatory Möbius function M(n) = sum_{k<=n} mu(k) via a Dujiao sieve."""

    def __init__(self, max_n: int):
        c = _integer_cuberoot_floor(max_n)
        # A standard, practical choice for Dujiao sieve: precompute up to floor(n^(2/3)).
        self.limit = c * c
        _, self.pref = _linear_sieve_mobius_prefix(self.limit)
        self.cache: dict[int, int] = {}

    def M(self, n: int) -> int:
        if n <= 0:
            return 0
        if n <= self.limit:
            return int(self.pref[n])
        if n in self.cache:
            return self.cache[n]

        # Dujiao recursion:
        # M(n) = 1 - sum_{i=2..n} (j-i+1) * M(n//i) over blocks where n//i is constant.
        res = 1
        i = 2
        while i <= n:
            q = n // i
            j = n // q
            res -= (j - i + 1) * self.M(q)
            i = j + 1

        self.cache[n] = res
        return res


@lru_cache(maxsize=None)
def _G_mod(m: int, mod: int = MOD) -> int:
    """G(m) = sum_{k=1..m} (3^k - 2^k - 1)  (mod mod).

    Note: mod is 10^9 (even), so we compute the 3^k geometric series using modulus 2*mod
    and an integer divide-by-2 at the end.
    """
    if m <= 0:
        return 0
    mod2 = 2 * mod
    # sum_{k=1..m} 3^k = (3^(m+1) - 3)/2
    num = (pow(3, m + 1, mod2) - 3) % mod2
    sum3 = (num // 2) % mod
    # sum_{k=1..m} 2^k = 2^(m+1) - 2
    sum2 = (pow(2, m + 1, mod) - 2) % mod
    return (sum3 - sum2 - (m % mod)) % mod


def t_mod(n: int, mod: int = MOD) -> int:
    """Return t(n) modulo mod for n up to 10^10."""
    mert = Mertens(n)
    ans = 0
    i = 1
    while i <= n:
        q = n // i
        j = n // q
        mu_sum = mert.M(j) - mert.M(i - 1)
        ans = (ans + (mu_sum % mod) * _G_mod(q, mod)) % mod
        i = j + 1
    return (ans + 1) % mod


def t_exact_small(n: int) -> int:
    """Exact t(n) for small n (used for asserts from the problem statement)."""
    # Compute mu up to n and do the straightforward divisor-sum formula.
    mu = [0] * (n + 1)
    mu[1] = 1
    primes: list[int] = []
    is_comp = [False] * (n + 1)
    for i in range(2, n + 1):
        if not is_comp[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            ip = i * p
            if ip > n:
                break
            is_comp[ip] = True
            if i % p == 0:
                mu[ip] = 0
                break
            mu[ip] = -mu[i]

    def g(m: int) -> int:
        return pow(3, m) - pow(2, m) - 1

    total_boundaries = 0
    for k in range(1, n + 1):
        ck = 0
        # c(k) = sum_{d|k} mu(d) * (3^(k/d) - 2^(k/d) - 1)
        for d in range(1, k + 1):
            if k % d == 0:
                ck += mu[d] * g(k // d)
        total_boundaries += ck
    return total_boundaries + 1


def main() -> None:
    # Test values given in the problem statement.
    assert t_exact_small(2) == 5
    assert t_exact_small(5) == 293
    assert t_exact_small(10) == 86195
    assert t_exact_small(20) == 5227991891

    print(t_mod(10**10, MOD))


if __name__ == "__main__":
    main()
