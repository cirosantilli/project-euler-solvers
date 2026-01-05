#!/usr/bin/env python3
"""Project Euler 489 - Common Factors Between Two Sequences

Let G(a,b) be the smallest non-negative integer n for which
    gcd(n^3 + b, (n+a)^3 + b)
is maximized.

Let H(m,n) = sum_{1<=a<=m, 1<=b<=n} G(a,b).

Given:
    G(1,1) = 5
    H(5,5) = 128878
    H(10,10) = 32936544

Find H(18,1900).

This script computes the answer directly (no input).
"""

from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple


# ------------------------- basic number theory helpers -------------------------


def sieve(limit: int) -> List[int]:
    """Return list of all primes <= limit."""
    if limit < 2:
        return []
    is_prime = bytearray(b"\x01") * (limit + 1)
    is_prime[0:2] = b"\x00\x00"
    for p in range(2, int(limit**0.5) + 1):
        if is_prime[p]:
            step = p
            start = p * p
            is_prime[start : limit + 1 : step] = b"\x00" * (
                ((limit - start) // step) + 1
            )
    return [i for i, v in enumerate(is_prime) if v]


def inv_mod(a: int, m: int) -> int:
    """Modular inverse of a mod m (m>0, gcd(a,m)=1)."""
    # Python supports pow(a, -1, m) for inverses.
    return pow(a, -1, m)


def tonelli_shanks(n: int, p: int) -> Optional[int]:
    """Return r such that r^2 ≡ n (mod p) for odd prime p, or None if no sqrt."""
    n %= p
    if n == 0:
        return 0
    if p == 2:
        return n

    # Legendre symbol
    if pow(n, (p - 1) // 2, p) != 1:
        return None

    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)

    # Factor p-1 = q * 2^s with q odd
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1

    # Find z, a quadratic non-residue
    z = 2
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1

    m = s
    c = pow(z, q, p)
    t = pow(n, q, p)
    r = pow(n, (q + 1) // 2, p)

    while t != 1:
        # Find least i (0<i<m) such that t^(2^i) == 1
        i = 1
        t2i = (t * t) % p
        while i < m and t2i != 1:
            t2i = (t2i * t2i) % p
            i += 1
        if i == m:
            return None  # should not happen
        b = pow(c, 1 << (m - i - 1), p)
        r = (r * b) % p
        c = (b * b) % p
        t = (t * c) % p
        m = i
    return r


# ------------------------------- factorization --------------------------------

# We only ever factor numbers up to:
#   a^6 + 27 b^2 <= 18^6 + 27*1900^2 ~= 1.32e8
# Trial division with primes up to sqrt(max) is fast.
PRIMES = sieve(12000)


def factorize_upto_1e8(n: int) -> Dict[int, int]:
    """Prime factorization for n <= ~1.4e8."""
    res: Dict[int, int] = {}
    x = n
    for p in PRIMES:
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


# -------------------------- solving modulo prime powers ------------------------


def _initial_solutions_mod_p(a: int, b: int, p: int) -> List[int]:
    """All n mod prime p satisfying:
        n^3 + b ≡ 0 (mod p)
        (n+a)^3 + b ≡ 0 (mod p)

    For p | a (which implies p <= 17 here), brute force.
    For p ∤ a and p not 2/3, use that common roots must also satisfy
        (n+a)^3 - n^3 = a(3n^2+3an+a^2) ≡ 0 (mod p)
    which is a quadratic.
    """
    b_mod = b % p

    # If p divides a, p is tiny (a <= 18), brute.
    if a % p == 0:
        sols = []
        for n in range(p):
            if (pow(n, 3, p) + b_mod) % p == 0 and (pow(n + a, 3, p) + b_mod) % p == 0:
                sols.append(n)
        return sols

    # If p == 3 and 3 ∤ a, then 3n^2+3an vanishes mod 3, leaving a^2 ≡ 0, impossible.
    if p == 3:
        return []

    # For p == 2, brute.
    if p == 2:
        return [
            n
            for n in range(2)
            if ((n * n * n + b) % 2 == 0 and (((n + a) ** 3) + b) % 2 == 0)
        ]

    # Solve 3n^2 + 3a n + a^2 ≡ 0 (mod p)
    a_mod = a % p
    disc = (-3 * a_mod * a_mod) % p  # Δ ≡ -3a^2
    sqrt_disc = tonelli_shanks(disc, p)
    if sqrt_disc is None:
        return []

    inv6 = inv_mod(6 % p, p)
    t = (-3 * a_mod) % p

    n1 = (t + sqrt_disc) * inv6 % p
    n2 = (t - sqrt_disc) * inv6 % p

    sols = []
    for n in {n1, n2}:
        # If quadratic holds, the two cubics are equal mod p; check both anyway.
        if (pow(n, 3, p) + b_mod) % p == 0 and (pow(n + a, 3, p) + b_mod) % p == 0:
            sols.append(n)
    sols.sort()
    return sols


def _linear_solutions_mod_prime(A: int, B: int, p: int) -> List[int]:
    """Solve A*t ≡ B (mod p) for prime p.

    Returns:
      - [] if no solutions
      - [t] if unique solution
      - list(range(p)) if all solutions
    """
    A %= p
    B %= p
    if A == 0:
        return list(range(p)) if B == 0 else []
    return [(B * inv_mod(A, p)) % p]


def solutions_for_prime_power(
    a: int, b: int, p: int, e_max: int
) -> Tuple[int, List[int]]:
    """Return (e, sols) where e is the maximum exponent <= e_max such that there
    exists n with both congruences holding modulo p^e, and sols are all such n
    modulo p^e.

    If no solution modulo p, returns (0, []).
    """
    if e_max <= 0:
        return 0, []

    sols = _initial_solutions_mod_p(a, b, p)
    if not sols:
        return 0, []

    mod = p
    e = 1

    # Lift solutions from p^e to p^(e+1)
    while e < e_max:
        mod2 = mod * p
        new_sols = set()

        for r in sols:
            # For k>=1, exact lifting uses:
            #   f(r + t*mod) ≡ f(r) + t*mod*f'(r) (mod mod*p)
            # So we solve two linear congruences for t mod p.
            v1 = (pow(r, 3, mod2) + b) % mod2
            v2 = (pow(r + a, 3, mod2) + b) % mod2
            if v1 % mod != 0 or v2 % mod != 0:
                continue

            c1 = (v1 // mod) % p
            c2 = (v2 // mod) % p

            r_mod_p = r % p
            s_mod_p = (r + a) % p

            A1 = (3 * r_mod_p * r_mod_p) % p
            A2 = (3 * s_mod_p * s_mod_p) % p
            B1 = (-c1) % p
            B2 = (-c2) % p

            t1 = _linear_solutions_mod_prime(A1, B1, p)
            if not t1:
                continue
            t2 = _linear_solutions_mod_prime(A2, B2, p)
            if not t2:
                continue

            # Intersect t-sets
            if len(t1) == p and len(t2) == p:
                ts = range(p)
            elif len(t1) == p:
                ts = t2
            elif len(t2) == p:
                ts = t1
            else:
                ts = t1 if t1[0] == t2[0] else []

            for t in ts:
                new_sols.add(r + t * mod)

        if not new_sols:
            break

        sols = sorted(new_sols)
        mod = mod2
        e += 1

    return e, sols


# ------------------------------ CRT combination --------------------------------


def combine_congruences(
    sols1: List[int], mod1: int, sols2: List[int], mod2: int
) -> Tuple[List[int], int]:
    """Combine x ≡ sols1 (mod mod1) with x ≡ sols2 (mod mod2), gcd(mod1,mod2)=1."""
    if mod1 == 1:
        return sorted({s % mod2 for s in sols2}), mod2
    if mod2 == 1:
        return sorted({s % mod1 for s in sols1}), mod1

    inv_mod1 = inv_mod(mod1 % mod2, mod2)
    new_mod = mod1 * mod2
    out = set()

    for x in sols1:
        x %= mod1
        for y in sols2:
            y %= mod2
            t = ((y - x) % mod2) * inv_mod1 % mod2
            out.add(x + mod1 * t)

    return sorted(out), new_mod


# ----------------------------- main computation --------------------------------


def precompute_a_data(max_a: int) -> Tuple[List[int], List[int], List[Dict[int, int]]]:
    a3 = [0] * (max_a + 1)
    a6 = [0] * (max_a + 1)
    fac_a = [dict() for _ in range(max_a + 1)]

    for a in range(1, max_a + 1):
        a3[a] = a**3
        a6[a] = a**6

        x = a
        f: Dict[int, int] = {}
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
        fac_a[a] = f

    return a3, a6, fac_a


A3, A6, FAC_A = precompute_a_data(18)


def compute_G(a: int, b: int) -> int:
    """Compute G(a,b) as defined in the statement."""
    # Resultant bound: Res(x^3+b, (x+a)^3+b) = a^3 * (a^6 + 27 b^2)
    R = A6[a] + 27 * b * b
    fac_R = factorize_upto_1e8(R)

    # Merge factors of a^3.
    fac_M: Dict[int, int] = dict(fac_R)
    for p, e in FAC_A[a].items():
        fac_M[p] = fac_M.get(p, 0) + 3 * e

    blocks: List[Tuple[int, int, List[int]]] = []  # (p, exponent, solutions mod p^e)
    for p, eM in fac_M.items():
        e, sols = solutions_for_prime_power(a, b, p, eM)
        if e > 0:
            blocks.append((p, e, sols))

    # If no prime power can divide both, the maximal gcd is 1 and the smallest n is 0.
    if not blocks:
        return 0

    # Combine all constraints via CRT and take smallest residue.
    blocks.sort(key=lambda t: t[0])
    sols = [0]
    mod = 1
    for p, e, sols_p in blocks:
        sols, mod = combine_congruences(sols, mod, sols_p, p**e)

    return min(sols)


def compute_H(m: int, n: int) -> int:
    total = 0
    for a in range(1, m + 1):
        for b in range(1, n + 1):
            total += compute_G(a, b)
    return total


def main() -> None:
    # Asserts for the test values in the problem statement.
    assert compute_G(1, 1) == 5
    assert compute_H(5, 5) == 128878
    assert compute_H(10, 10) == 32936544

    print(compute_H(18, 1900))


if __name__ == "__main__":
    main()
