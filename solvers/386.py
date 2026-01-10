#!/usr/bin/env python3
"""
Project Euler 386: Maximum length of an antichain

We work with the divisor poset of n. If n = ∏ p_i^{a_i}, the divisors form a product of chains
of lengths (a_i + 1). This poset is Sperner, so the maximum antichain size equals the maximum
rank size. Rank = total exponent sum, so N(n) is the maximum coefficient of:

    ∏ (1 + x + ... + x^{a_i})

N(n) depends only on the multiset of exponents (a_i), not on the primes.

We enumerate all feasible exponent multisets for n ≤ LIMIT, compute their width N(·) by a small DP,
count how many integers n realize each multiset, and sum.
"""

from __future__ import annotations

import sys
from bisect import bisect_left
from functools import lru_cache
from math import isqrt
from array import array


LIMIT = 100_000_000
SIEVE_MAX = 1_000_000  # enough for Lehmer pi() on x <= 1e8


# -----------------------
# Prime sieve up to SIEVE_MAX
# -----------------------
def _prime_sieve(n: int) -> tuple[array, array]:
    """Return (primes, pi_small) for 0..n inclusive using an odd-only sieve."""
    if n < 2:
        return array("I"), array("I", [0]) * (n + 1)

    size = n // 2  # only odds; index i represents (2*i+1)
    sieve = bytearray(b"\x01") * size
    sieve[0] = 0  # 1 is not prime

    r = isqrt(n)
    for p in range(3, r + 1, 2):
        if sieve[p // 2]:
            start = p * p
            step = 2 * p
            sieve[start // 2 :: p] = b"\x00" * (((n - start) // step) + 1)

    primes = array("I", [2])
    for i in range(1, size):
        if sieve[i]:
            primes.append(2 * i + 1)

    pi_small = array("I", [0]) * (n + 1)
    cnt = 0
    for x in range(2, n + 1):
        if x == 2:
            cnt = 1
        elif (x & 1) and sieve[x // 2]:
            cnt += 1
        pi_small[x] = cnt
    return primes, pi_small


PRIMES, PI_SMALL = _prime_sieve(SIEVE_MAX)


# -----------------------
# Integer k-th roots (exact floor)
# -----------------------
def iroot(n: int, k: int) -> int:
    """Return floor(n^(1/k)) for n>=0, k>=1."""
    if k <= 1:
        return n
    if n < 2:
        return n
    if k == 2:
        return isqrt(n)
    # float seed then adjust (safe for n<=1e8 here, but still adjusted to exact)
    x = int(n ** (1.0 / k))
    while (x + 1) ** k <= n:
        x += 1
    while x**k > n:
        x -= 1
    return x


# -----------------------
# Lehmer prime counting pi(x)
# -----------------------
_PHI_CACHE_MAX_X = 200_000
_PHI_CACHE_MAX_S = 100
_phi_cache: dict[tuple[int, int], int] = {}


def phi(x: int, s: int) -> int:
    """Count integers in [1..x] that are not divisible by the first s primes."""
    if s == 0:
        return x
    if s == 1:
        return x - x // 2

    if x < _PHI_CACHE_MAX_X and s < _PHI_CACHE_MAX_S:
        key = (x, s)
        v = _phi_cache.get(key)
        if v is not None:
            return v
        v = phi(x, s - 1) - phi(x // PRIMES[s - 1], s - 1)
        _phi_cache[key] = v
        return v

    return phi(x, s - 1) - phi(x // PRIMES[s - 1], s - 1)


@lru_cache(maxsize=None)
def lehmer_pi(x: int) -> int:
    """Prime counting function pi(x) for x >= 0."""
    if x <= SIEVE_MAX:
        return PI_SMALL[x]

    # Lehmer (Meissel-Lehmer) prime counting
    a = lehmer_pi(iroot(x, 4))
    b = lehmer_pi(isqrt(x))
    c = lehmer_pi(iroot(x, 3))

    res = phi(x, a) + (b + a - 2) * (b - a + 1) // 2

    # subtract contributions
    for i in range(a + 1, b + 1):
        p = PRIMES[i - 1]
        w = x // p
        res -= lehmer_pi(w)
        if i <= c:
            lim = lehmer_pi(isqrt(w))
            for j in range(i, lim + 1):
                res -= lehmer_pi(w // PRIMES[j - 1]) - (j - 1)
    return res


def pi(x: int) -> int:
    if x <= 1:
        return 0
    if x <= SIEVE_MAX:
        return PI_SMALL[x]
    return lehmer_pi(x)


# -----------------------
# Antichain width for an exponent multiset
# -----------------------
def antichain_width(exps: tuple[int, ...]) -> int:
    """
    Given exponents a_i, return max coefficient of ∏ (1 + x + ... + x^{a_i}).
    Small DP with sliding window.
    """
    if not exps:
        return 1
    dp = [1]
    for a in exps:
        new = [0] * (len(dp) + a)
        window = 0
        # new[k] = sum_{t=0..a} dp[k-t]
        for k in range(len(new)):
            if k < len(dp):
                window += dp[k]
            if k - (a + 1) >= 0:
                window -= dp[k - (a + 1)]
            new[k] = window
        dp = new
    return max(dp)


# -----------------------
# Enumerate feasible exponent multisets
# -----------------------
def generate_patterns(limit: int) -> list[tuple[int, ...]]:
    """
    Generate all exponent multisets (sorted non-increasing) that occur for some n<=limit.
    We test feasibility using the smallest primes (which minimize the numeric value).
    """
    # need at most 9 distinct primes because 2*3*5*7*11*13*17*19*23 < 1e8 < ...*29
    base_primes = [int(p) for p in PRIMES[:15]]

    patterns: set[tuple[int, ...]] = set()

    def dfs(idx_prime: int, last_exp: int, cur_val: int, exps: list[int]) -> None:
        patterns.add(tuple(exps))
        if idx_prime >= len(base_primes):
            return
        p = base_primes[idx_prime]
        # try next exponent e <= last_exp
        for e in range(1, last_exp + 1):
            nxt = cur_val * (p**e)
            if nxt > limit:
                break
            exps.append(e)
            dfs(idx_prime + 1, e, nxt, exps)
            exps.pop()

    dfs(0, 60, 1, [])
    patterns.discard(())  # handle n=1 separately
    return sorted(patterns, key=lambda t: (len(t), t), reverse=False)


# -----------------------
# Count numbers for a pattern (exponent multiset)
# -----------------------
def minimal_product(exps: tuple[int, ...], excluded: set[int]) -> int:
    """
    Lower bound on the product contributed by exps using the smallest available distinct primes.
    """
    prod = 1
    idx = 0
    for e in exps:
        while idx < len(PRIMES) and int(PRIMES[idx]) in excluded:
            idx += 1
        if idx >= len(PRIMES):
            return 10**30  # unreachable (should not happen for this problem)
        prod *= int(PRIMES[idx]) ** e
        idx += 1
    return prod


def count_numbers_for_pattern(exps: tuple[int, ...], limit: int) -> int:
    """
    Count integers n<=limit whose prime-exponent multiset equals `exps` (sorted non-increasing).
    Representation: exponents sorted descending; primes for equal exponents are chosen in increasing order.
    """
    r = len(exps)
    if r == 0:
        return 1

    # quick single factor
    if r == 1:
        return pi(iroot(limit, exps[0]))

    exps = tuple(sorted(exps, reverse=True))
    used: list[int] = []
    used_set: set[int] = set()

    def rec(pos: int, lim: int, last_in_group: int) -> int:
        if pos == r - 1:
            e = exps[pos]
            lo = last_in_group if (pos > 0 and exps[pos] == exps[pos - 1]) else 1
            max_p = iroot(lim, e)
            if max_p <= lo:
                return 0
            cnt = pi(max_p) - pi(lo)
            # exclude already-used primes that fall inside (lo, max_p]
            for u in used:
                if lo < u <= max_p:
                    cnt -= 1
            return cnt

        e = exps[pos]

        # how many consecutive exps (including current) equal to e?
        rem_same = 1
        while pos + rem_same < r and exps[pos + rem_same] == e:
            rem_same += 1

        # optimistic lower bound for primes used by later (smaller) exponent groups
        other_exps = exps[pos + rem_same :]
        min_other = minimal_product(other_exps, used_set)
        if min_other > lim:
            return 0

        # bound current prime using p^(e*rem_same) <= lim / min_other
        max_p = iroot(lim // min_other, e * rem_same)

        start = last_in_group + 1 if (pos > 0 and exps[pos] == exps[pos - 1]) else 2
        if start > max_p:
            return 0

        # iterate primes in [start..max_p]
        idx = bisect_left(PRIMES, start)
        total = 0
        for i in range(idx, len(PRIMES)):
            p = int(PRIMES[i])
            if p > max_p:
                break
            if p in used_set:
                continue
            p_pow = p**e
            if p_pow > lim:
                break

            # prune: must be possible to fill remaining exponents with distinct primes
            min_rest = minimal_product(exps[pos + 1 :], used_set | {p})
            if p_pow * min_rest > lim:
                continue

            used.append(p)
            used_set.add(p)

            next_last = p if (pos + 1 < r and exps[pos + 1] == e) else 0
            total += rec(pos + 1, lim // p_pow, next_last)

            used_set.remove(p)
            used.pop()

        return total

    return rec(0, limit, 0)


# -----------------------
# Statement checks
# -----------------------
def is_antichain(subset: list[int]) -> bool:
    """True iff no element divides another (unless size 1)."""
    if len(subset) <= 1:
        return True
    subset = sorted(subset)
    for i, a in enumerate(subset):
        for b in subset[i + 1 :]:
            if b % a == 0:
                return False
    return True


def divisors(n: int) -> list[int]:
    """All positive divisors of n (simple, used only in small statement tests)."""
    ds = []
    for d in range(1, isqrt(n) + 1):
        if n % d == 0:
            ds.append(d)
            if d * d != n:
                ds.append(n // d)
    return sorted(ds)


def run_statement_asserts() -> None:
    # From the problem statement
    s30 = divisors(30)
    assert s30 == [1, 2, 3, 5, 6, 10, 15, 30]
    assert is_antichain([2, 5, 6]) is False
    assert is_antichain([2, 3, 5]) is True


# -----------------------
# Solve
# -----------------------
def solve(limit: int = LIMIT) -> int:
    total = 1  # n=1, N(1)=1

    patterns = generate_patterns(limit)
    for exps in patterns:
        width = antichain_width(exps)
        cnt = count_numbers_for_pattern(exps, limit)
        total += width * cnt
    return total


def main(argv: list[str]) -> None:
    run_statement_asserts()

    if len(argv) >= 2 and argv[1] == "--test":
        # small internal cross-check (bruteforce) for confidence
        # (does not run for the real LIMIT)
        test_limit = 5000

        def brute_sum(m: int) -> int:
            # brute for small m: factor each n and compute N(n) by DP on exponents
            def factor_exps(x: int) -> tuple[int, ...]:
                out = []
                tmp = x
                for p in PRIMES:
                    p = int(p)
                    if p * p > tmp:
                        break
                    if tmp % p == 0:
                        e = 0
                        while tmp % p == 0:
                            tmp //= p
                            e += 1
                        out.append(e)
                if tmp > 1:
                    out.append(1)
                out.sort(reverse=True)
                return tuple(out)

            s = 0
            for n in range(1, m + 1):
                s += antichain_width(factor_exps(n))
            return s

        fast = 0
        # pattern method restricted to <=test_limit
        for exps in generate_patterns(test_limit):
            fast += antichain_width(exps) * count_numbers_for_pattern(exps, test_limit)
        fast += 1  # n=1

        brute = brute_sum(test_limit)
        assert fast == brute, (fast, brute)
        print("OK")
        return

    print(solve(limit=LIMIT))


if __name__ == "__main__":
    main(sys.argv)
