#!/usr/bin/env python3
"""
Project Euler 302: Strong Achilles Numbers

We count strong Achilles numbers < 10^18.
A number n is Achilles if:
  - n is powerful (every prime exponent >= 2)
  - n is not a perfect power (gcd of exponents == 1)

Strong Achilles means n is Achilles and phi(n) is also Achilles.

This implementation uses a DFS over prime factorizations n = Π p_i^e_i (e_i >= 2),
maintaining the prime-exponent multiset of phi(n) incrementally:
  phi(n) = Π p_i^(e_i-1) * (p_i - 1)

We prune aggressively using:
  - "pending primes": primes with exponent 1 in phi so far (must be fixed later)
  - feasibility checks based on remaining headroom and prime bounds
  - a safe incompatibility lower-bound on how many distinct future primes are required
    to fix large pending primes (based on lcm constraints)
"""

from __future__ import annotations
from math import gcd, isqrt
import sys

LIMIT = 10**18

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------


def iroot(n: int, k: int) -> int:
    """floor(k-th root of n) for small k (k=2 or 3 used here)."""
    if k == 1:
        return n
    if k == 2:
        return isqrt(n)
    # k == 3
    x = int(n ** (1.0 / k))
    while (x + 1) ** k <= n:
        x += 1
    while x**k > n:
        x -= 1
    return x


def sieve_spf(n: int):
    """Return (primes, spf) up to n using linear sieve."""
    spf = list(range(n + 1))
    primes = []
    spf[0] = 0
    if n >= 1:
        spf[1] = 1
    for i in range(2, n + 1):
        if spf[i] == i:
            primes.append(i)
        for p in primes:
            v = p * i
            if v > n:
                break
            spf[v] = p
            if i % p == 0:
                break
    return primes, spf


def factorize_small(x: int, spf: list[int]) -> list[tuple[int, int]]:
    """Factorize x <= len(spf)-1 using smallest prime factor table."""
    out = []
    while x > 1:
        p = spf[x]
        e = 0
        while x % p == 0:
            x //= p
            e += 1
        out.append((p, e))
    return out


def factorize_with_primes(n: int, primes: list[int]) -> dict[int, int]:
    """Factorization for test helpers (n small in asserts)."""
    res = {}
    x = n
    for p in primes:
        if p * p > x:
            break
        if x % p == 0:
            e = 0
            while x % p == 0:
                x //= p
                e += 1
            res[p] = e
    if x > 1:
        res[x] = res.get(x, 0) + 1
    return res


def is_achilles(n: int, primes: list[int]) -> bool:
    """Check Achilles for small n (used only in asserts)."""
    fac = factorize_with_primes(n, primes)
    if not fac:
        return False
    exps = list(fac.values())
    if any(e < 2 for e in exps):
        return False
    return gcd_many(exps) == 1


def phi_from_factorization(fac: dict[int, int]) -> dict[int, int]:
    """Return factorization of phi given n's factorization (small for asserts)."""
    # phi(n) = Π p^(e-1) * (p-1)
    out = {}
    # naïve factorization of p-1 by trial division (small primes only)
    # This is used only for asserts.
    primes_small = []
    # build a tiny prime list for trial division
    # (p-1 <= n, n is small in asserts)
    maxv = max(fac.keys())
    sieve = [True] * (maxv + 1)
    sieve[0:2] = [False, False]
    for i in range(2, len(sieve)):
        if sieve[i]:
            primes_small.append(i)
            step = i
            for j in range(i * i, len(sieve), step):
                sieve[j] = False

    def fac_small(x: int) -> dict[int, int]:
        d = {}
        y = x
        for p in primes_small:
            if p * p > y:
                break
            if y % p == 0:
                e = 0
                while y % p == 0:
                    y //= p
                    e += 1
                d[p] = e
        if y > 1:
            d[y] = d.get(y, 0) + 1
        return d

    for p, e in fac.items():
        if e - 1 > 0:
            out[p] = out.get(p, 0) + (e - 1)
        for q, a in fac_small(p - 1).items():
            out[q] = out.get(q, 0) + a
    return out


def gcd_many(vals: list[int]) -> int:
    g = 0
    for v in vals:
        g = v if g == 0 else gcd(g, v)
        if g == 1:
            return 1
    return g


def is_strong_achilles(n: int, primes: list[int]) -> bool:
    """Strong Achilles test for small n (used only in asserts)."""
    if not is_achilles(n, primes):
        return False
    fac = factorize_with_primes(n, primes)
    phi_fac = phi_from_factorization(fac)
    exps = list(phi_fac.values())
    if not exps:
        return False
    if any(e < 2 for e in exps):
        return False
    return gcd_many(exps) == 1


# ------------------------------------------------------------
# Core solver
# ------------------------------------------------------------


def count_strong_achilles(limit_exclusive: int) -> int:
    """
    Count strong Achilles numbers n < limit_exclusive.
    Uses DFS over prime factorisations.
    """
    N = limit_exclusive - 1
    # Largest prime factor must have exponent >=3, hence p^3 <= N -> p <= N^(1/3)
    MAXP = iroot(N, 3)

    primes, spf = sieve_spf(MAXP)

    # Precompute factorisations of p-1 for primes p
    pminus1 = {}
    for p in primes:
        if p == 2:
            pminus1[p] = []
        else:
            pminus1[p] = factorize_small(p - 1, spf)

    phi_exps: dict[int, int] = {}
    pending: set[int] = set()  # primes with exponent exactly 1 in current phi
    ans = 0

    sys.setrecursionlimit(10_000_000)

    def add_exp(q: int, delta: int, changed: list[tuple[int, int]]):
        old = phi_exps.get(q, 0)
        new = old + delta
        changed.append((q, old))
        if new:
            phi_exps[q] = new
        else:
            phi_exps.pop(q, None)
        if new == 1:
            pending.add(q)
        else:
            pending.discard(q)

    def rollback(changed: list[tuple[int, int]]):
        for q, old in reversed(changed):
            if old:
                phi_exps[q] = old
            else:
                phi_exps.pop(q, None)
            if old == 1:
                pending.add(q)
            else:
                pending.discard(q)

    def phi_is_achilles() -> bool:
        # phi must be powerful and gcd(exponents)==1
        g = 0
        for e in phi_exps.values():
            if e < 2:
                return False
            g = e if g == 0 else gcd(g, e)
            if g == 1:
                # still need to check all e>=2, but that's done above
                pass
        return g == 1

    def dfs(start_idx: int, current_n: int, gcd_n: int, num_primes: int, last_exp: int):
        nonlocal ans

        # Count current n if it's strong Achilles:
        if num_primes >= 2 and gcd_n == 1 and last_exp >= 3 and not pending:
            if phi_is_achilles():
                ans += 1

        remaining = N // current_n
        if remaining < 4:
            return

        max_p2 = isqrt(remaining)
        if max_p2 > MAXP:
            max_p2 = MAXP

        # Basic pending feasibility: pending primes must be <= max possible future prime
        for q in pending:
            if q > max_p2:
                return

        # Safe extra prune:
        # Build a subset of pending primes that are pairwise incompatible (cannot be fixed by
        # a single future prime <= max_p2). Each of these requires a distinct future prime r
        # and thus at least (q+1)^2 multiplicative budget in n.
        if len(pending) >= 2:
            chosen = []
            prod_lb = 1
            for q in sorted(pending, reverse=True):
                ok = True
                for s in chosen:
                    # if lcm(q,s) <= max_p2 then a prime could be 1 mod both
                    if (q // gcd(q, s)) * s <= max_p2:
                        ok = False
                        break
                if ok:
                    chosen.append(q)
                    prod_lb *= (q + 1) * (q + 1)
                    if prod_lb > remaining:
                        return

        # If current last exponent is 2, we must still be able to add some future prime^3
        if last_exp == 2:
            max_p3 = iroot(remaining, 3)
            if max_p3 > MAXP:
                max_p3 = MAXP
            if start_idx >= len(primes) or primes[start_idx] > max_p3:
                return

        # Try adding a new prime factor p^e (e >= 2)
        for i in range(start_idx, len(primes)):
            p = primes[i]
            if p > max_p2:
                break
            pe = p * p
            if pe > remaining:
                break

            e = 2
            while pe <= remaining:
                changed = []
                add_exp(p, e - 1, changed)
                for q, a in pminus1[p]:
                    add_exp(q, a, changed)

                new_n = current_n * pe
                new_g = e if gcd_n == 0 else gcd(gcd_n, e)

                dfs(i + 1, new_n, new_g, num_primes + 1, e)

                rollback(changed)
                e += 1
                pe *= p

    dfs(0, 1, 0, 0, 2)
    return ans


# ------------------------------------------------------------
# Main + required asserts from statement
# ------------------------------------------------------------


def main():
    # For asserts we only need small primes
    primes_small, _ = sieve_spf(200000)

    # Problem statement examples:
    assert is_achilles(864, primes_small) is True
    assert is_achilles(1800, primes_small) is True
    assert is_strong_achilles(864, primes_small) is True
    assert is_strong_achilles(1800, primes_small) is False

    # Counts given in statement:
    assert count_strong_achilles(10**4) == 7
    assert count_strong_achilles(10**8) == 656

    # Final answer
    print(count_strong_achilles(10**18))


if __name__ == "__main__":
    main()
