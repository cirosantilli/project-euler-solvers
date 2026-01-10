#!/usr/bin/env python3
"""Project Euler 598: Split Divisibilities

We need C(100!) where C(n) counts pairs (a,b) with a*b=n, a<=b and
both a and b have the same number of divisors.

Let n = \prod p^e. Any divisor a corresponds to exponents x (0<=x<=e).
Then
  d(a)      = \prod (x+1)
  d(n/a)    = \prod (e-x+1)
We must count exponent choices with d(a)=d(n/a).

For 100! this is huge, so we count solutions using a divisor-count ratio:
  r = d(a)/d(n/a) = \prod (x+1)/(e-x+1).
We need r=1.
Represent each term as prime-exponent differences of its numerator and
denominator, and do a DP over these differences.

Crucial simplification for 100!:
- Only the splits for prime 2 (e=97) and prime 3 (e=48) can introduce
  primes >=29 into the ratio (because they allow factors up to 98 and 49).
- All other primes in 100! have e<=24, hence (x+1) and (e-x+1) are <=25,
  so they never introduce primes >=29.

Therefore we can:
1) Enumerate all (u2,u3) with u2 in 1..98 (v2=99-u2) and u3 in 1..49
   (v3=50-u3) such that all prime-exponent differences for primes
   {29,31,37,41,43,47} cancel.
2) For the remaining primes {5,7,11,13,17,19,23}, build a DP distribution
   over differences for primes <=23.
3) The primes with small exponents (e=1,2,3) affect only the 2- and 3-
   exponents in the ratio, so we keep them as a small 2D distribution and
   apply it at query-time.

Finally, if S is the set of divisors a with d(a)=d(n/a), then
  C(n) = |S|/2    if n is not a square
  C(n) = (|S|+1)/2 if n is a square.
(100! is not a square.)
"""

from __future__ import annotations

from collections import defaultdict


# ----------------------- basic number theory helpers -----------------------


def primes_upto(n: int) -> list[int]:
    """Simple sieve."""
    sieve = bytearray(b"\x01") * (n + 1)
    if n >= 0:
        sieve[0] = 0
    if n >= 1:
        sieve[1] = 0
    p = 2
    while p * p <= n:
        if sieve[p]:
            step = p
            start = p * p
            sieve[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
        p += 1
    return [i for i in range(2, n + 1) if sieve[i]]


def factorial_prime_exponents(n: int) -> dict[int, int]:
    """Prime exponents in n! via Legendre's formula."""
    exps: dict[int, int] = {}
    for p in primes_upto(n):
        e = 0
        m = n
        while m:
            m //= p
            e += m
        exps[p] = e
    return exps


def factorize_small(n: int) -> dict[int, int]:
    """Trial division factorization (sufficient for small test values)."""
    exps: dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            exps[d] = exps.get(d, 0) + 1
            n //= d
        d += 1 if d == 2 else 2
    if n > 1:
        exps[n] = exps.get(n, 0) + 1
    return exps


# --------------------------- brute-force for tests --------------------------


def C_from_prime_exponents_bruteforce(exps: dict[int, int]) -> int:
    """Compute C(n) from a prime-exponent dict by enumerating all divisors.

    Only meant for small factorizations (e.g. 48, 10!).
    """
    es = list(exps.values())

    count_vectors = 0

    def dfs(i: int, da: int, db: int) -> None:
        nonlocal count_vectors
        if i == len(es):
            if da == db:
                count_vectors += 1
            return
        e = es[i]
        for x in range(e + 1):
            dfs(i + 1, da * (x + 1), db * (e - x + 1))

    dfs(0, 1, 1)

    is_square = all(e % 2 == 0 for e in es)
    # If n is a square, the middle divisor a=b is only counted once.
    return (count_vectors + (1 if is_square else 0)) // 2


# ---------------------------- fast solver for 100! --------------------------


def build_spf(limit: int) -> list[int]:
    """Smallest prime factor sieve."""
    spf = list(range(limit + 1))
    spf[0] = 0
    if limit >= 1:
        spf[1] = 1
    for i in range(2, int(limit**0.5) + 1):
        if spf[i] == i:  # prime
            for j in range(i * i, limit + 1, i):
                if spf[j] == j:
                    spf[j] = i
    return spf


def factor_exponents(n: int, spf: list[int]) -> dict[int, int]:
    """Prime exponent dict for 1 <= n <= len(spf)-1."""
    out: dict[int, int] = {}
    while n > 1:
        p = spf[n]
        c = 0
        while n % p == 0:
            n //= p
            c += 1
        out[p] = out.get(p, 0) + c
    return out


def precompute_vectors(
    limit: int, primes_low: list[int], primes_high: list[int]
) -> tuple[list[tuple[int, ...]], list[tuple[int, ...]], list[bool]]:
    """For each 0..limit, precompute exponent vectors for primes_low/high.

    Also returns has_big[n]: True if n has any prime factor > 47.
    """
    spf = build_spf(limit)
    vec_low = [(0,) * len(primes_low) for _ in range(limit + 1)]
    vec_high = [(0,) * len(primes_high) for _ in range(limit + 1)]
    has_big = [False] * (limit + 1)

    idx_low = {p: i for i, p in enumerate(primes_low)}
    idx_high = {p: i for i, p in enumerate(primes_high)}

    for n in range(2, limit + 1):
        f = factor_exponents(n, spf)
        low = [0] * len(primes_low)
        high = [0] * len(primes_high)
        big = False
        for p, e in f.items():
            if p in idx_low:
                low[idx_low[p]] = e
            if p in idx_high:
                high[idx_high[p]] = e
            if p > 47:
                big = True
        vec_low[n] = tuple(low)
        vec_high[n] = tuple(high)
        has_big[n] = big

    return vec_low, vec_high, has_big


def vec_sub(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x - y for x, y in zip(a, b))


def vec_add(a: tuple[int, ...], b: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(x + y for x, y in zip(a, b))


def solve_C_100_factorial() -> int:
    # We only track prime-exponent differences in divisor-count ratios for primes <= 47.
    primes_low = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    primes_high = [29, 31, 37, 41, 43, 47]

    # Precompute exponent vectors for numbers we will split: up to 99.
    vec_low, vec_high, has_big = precompute_vectors(99, primes_low, primes_high)

    # Build DP distribution for primes {5,7,11,13,17,19,23} (their exponents in 100!).
    # DP key structure:
    #   outer key R = (d5,d7,d11,d13,d17,d19,d23)
    #   inner key (d2,d3)
    primes_100_fact = factorial_prime_exponents(100)
    big_primes = [5, 7, 11, 13, 17, 19, 23]
    big_es = [primes_100_fact[p] for p in big_primes]

    # Precompute options for each big exponent e:
    # each option gives (delta_d2, delta_d3, delta_R_tuple)
    options_by_e: dict[int, list[tuple[int, int, tuple[int, ...]]]] = {}
    for e in set(big_es):
        opts = []
        for x in range(e + 1):
            u = x + 1
            v = e - x + 1
            diff = vec_sub(vec_low[u], vec_low[v])  # length 9
            d2, d3 = diff[0], diff[1]
            R = diff[2:]  # length 7
            opts.append((d2, d3, R))
        options_by_e[e] = opts

    M: dict[tuple[int, ...], dict[tuple[int, int], int]] = {(0,) * 7: {(0, 0): 1}}

    for e in big_es:
        opts = options_by_e[e]
        newM: dict[tuple[int, ...], dict[tuple[int, int], int]] = {}
        for R0, inner in M.items():
            for (d2_0, d3_0), cnt in inner.items():
                for d2_d, d3_d, Rd in opts:
                    R1 = vec_add(R0, Rd)
                    key23 = (d2_0 + d2_d, d3_0 + d3_d)
                    inner1 = newM.get(R1)
                    if inner1 is None:
                        inner1 = {}
                        newM[R1] = inner1
                    inner1[key23] = inner1.get(key23, 0) + cnt
        M = newM

    # Small primes groups (affect only d2 and d3):
    #  - ten primes with e=1: (d2 += ±1)
    #  - four primes with e=2: (d3 += -1/0/+1)
    #  - two primes with e=3: (d2,d3) in {(-2,0),(1,-1),(-1,1),(2,0)}
    def convolve_2d(
        dist: dict[tuple[int, int], int], deltas: list[tuple[int, int]]
    ) -> dict[tuple[int, int], int]:
        out: dict[tuple[int, int], int] = {}
        for (a, b), c in dist.items():
            for da, db in deltas:
                k = (a + da, b + db)
                out[k] = out.get(k, 0) + c
        return out

    S: dict[tuple[int, int], int] = {(0, 0): 1}
    for _ in range(10):
        S = convolve_2d(S, [(1, 0), (-1, 0)])
    for _ in range(4):
        S = convolve_2d(S, [(0, 1), (0, 0), (0, -1)])
    for _ in range(2):
        S = convolve_2d(S, [(-2, 0), (1, -1), (-1, 1), (2, 0)])

    # Enumerate valid (u2,u3) splits for primes 2 and 3.
    N_all = 0

    # Precompute low/high diffs for u3 options to save work.
    u3_infos = []
    for u3 in range(1, 49 + 1):
        v3 = 50 - u3
        dlow3 = vec_sub(vec_low[u3], vec_low[v3])
        dhigh3 = vec_sub(vec_high[u3], vec_high[v3])
        u3_infos.append((dlow3, dhigh3))

    for u2 in range(1, 98 + 1):
        v2 = 99 - u2
        # Primes > 47 can only appear here and cannot be cancelled -> exclude.
        if has_big[u2] or has_big[v2]:
            continue

        dlow2 = vec_sub(vec_low[u2], vec_low[v2])
        dhigh2 = vec_sub(vec_high[u2], vec_high[v2])

        for dlow3, dhigh3 in u3_infos:
            # High primes 29..47 must cancel using only these two splits.
            if any(x != 0 for x in vec_add(dhigh2, dhigh3)):
                continue

            dlow = vec_add(dlow2, dlow3)
            targetR = tuple(-x for x in dlow[2:])
            inner = M.get(targetR)
            if inner is None:
                continue

            t2, t3 = -dlow[0], -dlow[1]
            subtotal = 0
            # Apply the small-groups distribution along (d2,d3).
            for (s2, s3), scnt in S.items():
                subtotal += inner.get((t2 - s2, t3 - s3), 0) * scnt
            N_all += subtotal

    # 100! is not a square -> C(n) = |S|/2.
    return N_all // 2


def main() -> None:
    # Asserts from the problem statement.
    assert C_from_prime_exponents_bruteforce(factorize_small(48)) == 1
    assert C_from_prime_exponents_bruteforce(factorial_prime_exponents(10)) == 3

    ans = solve_C_100_factorial()
    print(ans)


if __name__ == "__main__":
    main()
