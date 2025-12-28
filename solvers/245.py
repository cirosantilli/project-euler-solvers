#!/usr/bin/env python3
"""
Project Euler 245 - Coresilience

We need:
  Sum of all composite n <= 2*10^11 such that C(n)=(n-phi(n))/(n-1) is a unit fraction 1/k.

Key fact:
  If k*phi(n) - (k-1)*n = 1, then gcd(phi(n), n)=1, which implies n is squarefree.
So we only consider squarefree n = Π p_i.

Then C(n)=1/k  <=>  (n-1) divisible by (n-phi(n)).

We split into:
  - Semiprimes (2 primes): tractable for all k up to sqrt(N)
  - >=3 primes: only possible when k <= cbrt(N) (~5848), rare; solved with DFS.
"""

from __future__ import annotations

import bisect
import math
from collections import Counter


N = 2 * 10**11


# ------------------------- Totient for small asserts -------------------------

def totient_small(n: int) -> int:
    """Euler totient via trial division (only used for tiny assert checks)."""
    result = n
    x = n
    p = 2
    while p * p <= x:
        if x % p == 0:
            while x % p == 0:
                x //= p
            result -= result // p
        p += 1
    if x > 1:
        result -= result // x
    return result


# Asserts from problem statement:
# "for example, R(12) = 4/11"
assert totient_small(12) == 4
assert totient_small(12) / (12 - 1) == 4 / 11


# ------------------------- Miller-Rabin primality ----------------------------

_SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)

def is_prime(n: int) -> bool:
    """Deterministic Miller-Rabin valid for n < 3.4e14 (covers this problem)."""
    if n < 2:
        return False
    for p in _SMALL_PRIMES:
        if n % p == 0:
            return n == p

    # write n-1 = d * 2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    # Deterministic bases for n < 341,550,071,728,321:
    for a in (2, 3, 5, 7, 11, 13, 17):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


# ------------------------- Prime sieve ---------------------------------------

def sieve_primes(limit: int) -> list[int]:
    """Simple sieve of Eratosthenes."""
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    root = int(limit ** 0.5)
    for i in range(2, root + 1):
        if sieve[i]:
            step = i
            start = i * i
            sieve[start:limit + 1:step] = b"\x00" * (((limit - start) // step) + 1)
    return [i for i, ok in enumerate(sieve) if ok]


# ------------------------- Semiprime enumeration -----------------------------

def roots_phi6_prime(p: int) -> list[int]:
    """
    Roots of k^2 - k + 1 ≡ 0 (mod p).
    For primes p>3, roots exist iff p ≡ 1 mod 6.
    We find roots via a non-trivial cube root of unity.
    """
    if p == 3:
        return [2]  # double root mod 3
    if p % 6 != 1:
        return []

    exp = (p - 1) // 3
    w = 1
    for a in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        w = pow(a, exp, p)
        if w != 1:
            break
    if w == 1:
        a = 2
        while True:
            a += 1
            w = pow(a, exp, p)
            if w != 1:
                break

    r1 = (-w) % p
    r2 = (-pow(w, 2, p)) % p
    return [r1] if r1 == r2 else [r1, r2]


def factor_phi6_all_even(max_k: int, primes_list: list[int]) -> list[list[int] | None]:
    """
    For each even k, factor S(k)=k^2-k+1 by sieving primes p where p divides S(k).
    Store prime factors with multiplicity.
    """
    rem = [0] * (max_k + 1)
    for k in range(0, max_k + 1, 2):
        rem[k] = k * k - k + 1

    factors: list[list[int] | None] = [None] * (max_k + 1)

    for p in primes_list:
        if p == 2:
            continue
        roots = roots_phi6_prime(p)
        if not roots:
            continue

        step = 2 * p  # only even k
        for r in roots:
            start = r
            if start % 2 == 1:
                start += p
            for k in range(start, max_k + 1, step):
                if k < 2:
                    continue
                x = rem[k]
                if x % p != 0:
                    continue
                if factors[k] is None:
                    factors[k] = []
                while x % p == 0:
                    factors[k].append(p)
                    x //= p
                rem[k] = x

    for k in range(2, max_k + 1, 2):
        if rem[k] > 1:
            if factors[k] is None:
                factors[k] = [rem[k]]
            else:
                factors[k].append(rem[k])
            rem[k] = 1

    return factors


def divisors_from_factor_list(flst: list[int]) -> list[int]:
    """Generate all divisors from a multiplicity list of primes."""
    c = Counter(flst)
    divs = [1]
    for p, exp in c.items():
        base = list(divs)
        pe = 1
        for _ in range(exp):
            pe *= p
            for d in base:
                divs.append(d * pe)
    return divs


def compute_semiprimes() -> tuple[set[int], set[int]]:
    """Return (set of all semiprime solutions n, set of k values encountered)."""
    max_k = int(math.isqrt(N))
    primes = sieve_primes(max_k)
    factors = factor_phi6_all_even(max_k, primes)

    sols: set[int] = set()
    ks: set[int] = set()

    for k in range(2, max_k + 1, 2):
        S = k * k - k + 1
        flst = factors[k]
        if flst is None:
            continue
        divs = divisors_from_factor_list(flst)
        for d in divs:
            e = S // d
            if d > e:
                continue
            p = k + d
            q = k + e
            if p == q:
                continue
            n = p * q
            if n > N:
                continue
            if is_prime(p) and is_prime(q):
                sols.add(n)
                if k <= 5847:  # useful for multiprime search
                    ks.add(k)

    return sols, ks, primes


# ------------------------- Multiprime search (>=3 primes) --------------------

def multiprime_solutions(ks: set[int], primes: list[int]) -> set[int]:
    """
    DFS over prime products for each small k.
    Only needed for k <= 5847 (cuberoot bound).
    """
    k_limit = 5847
    max_first = int(round(N ** (1/3)))  # about 5848
    primes_small = [p for p in primes if p <= max_first]

    sols: set[int] = set()

    def dfs(k: int, P: int, A: int, last_p: int, depth: int) -> None:
        den = k * A - (k - 1) * P
        if den <= 0:
            return

        # Try closing (adding final prime r)
        if depth >= 2:
            num = k * A + 1
            if num % den == 0:
                r = num // den
                if r > last_p and P * r <= N and is_prime(r):
                    sols.add(P * r)

        # Extend by choosing another intermediate prime p
        p_max = int(math.isqrt(N // P))
        start = max(last_p + 2, k + 1)
        # require next den positive: den_new = p*den - k*A > 0
        lb = (k * A) // den + 1
        if lb > start:
            start = lb

        idx = bisect.bisect_left(primes, start)
        while idx < len(primes):
            p = primes[idx]
            if p > p_max:
                break
            P1 = P * p
            A1 = A * (p - 1)
            den1 = p * den - k * A
            if den1 > 0:
                dfs(k, P1, A1, p, depth + 1)
            idx += 1

    # run only for k that showed up among semiprimes (empirically sufficient and very fast)
    for k in sorted(ks):
        if k > k_limit:
            continue
        # first prime must be > k and <= cube root bound
        idx = bisect.bisect_left(primes_small, k + 1)
        while idx < len(primes_small):
            p1 = primes_small[idx]
            if p1 * p1 * p1 > N:
                break
            dfs(k, p1, p1 - 1, p1, 1)
            idx += 1

    return sols


# ------------------------- Main solve ----------------------------------------

def solve() -> int:
    semis, ks, primes = compute_semiprimes()
    multis = multiprime_solutions(ks, primes)
    all_solutions = semis | multis
    return sum(all_solutions)


if __name__ == "__main__":
    print(solve())

