#!/usr/bin/env python3
"""
Project Euler 621: Expressing an Integer as the Sum of Triangular Numbers

No external libraries used.

We use the identity:
  8*T_k + 1 = (2k+1)^2
so T_i + T_j + T_k = n  <=>  x^2 + y^2 + z^2 = 8n + 3
with x,y,z odd. For numbers congruent to 3 (mod 8) every representation as
a sum of three squares automatically has x,y,z odd, so we can count all integer
solutions (with order and signs) and divide by 8.

A classical formula (Gauss / Cohen) expresses r_3(N) (ordered, signed reps)
in terms of an imaginary quadratic class number h(D) and a short divisor sum.
For N = 8n+3 we get:
  r_3(N) = 24 * L(chi_D, 0) * S
  G(n)   = r_3(N) / 8 = 3 * L(chi_D, 0) * S
where
  N = n0 * f^2   with n0 squarefree,
  D = -n0        (a negative fundamental discriminant because n0 ≡ 3 mod 4),
  S = sum_{d|f} mu(d) * (D/d) * sigma(f/d).
L(chi_D,0) equals h(D)/(w(D)/2), with w(D) in {2,4,6}; only D=-3,-4 are special.

We compute:
- factorization using deterministic Miller-Rabin (64-bit) + Pollard-Rho,
- class number h(D) by enumerating reduced binary quadratic forms of discriminant D,
  using modular square roots (Tonelli-Shanks + Hensel) and CRT to avoid O(a^2) scans.
"""

from __future__ import annotations

import math
import random
from typing import Dict, List, Tuple


# ---------------------------
# Basic number theory helpers
# ---------------------------


def isqrt(n: int) -> int:
    return int(math.isqrt(n))


def gcd(a: int, b: int) -> int:
    return math.gcd(a, b)


def mul_mod(a: int, b: int, mod: int) -> int:
    return (a * b) % mod


def pow_mod(a: int, e: int, mod: int) -> int:
    return pow(a, e, mod)


# ---------------------------
# Miller-Rabin primality test
# (deterministic for 64-bit)
# ---------------------------

_MR_BASES_64 = (2, 3, 5, 7, 11, 13, 17)


def is_probable_prime(n: int) -> bool:
    if n < 2:
        return False
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return False

    # write n-1 = d * 2^s
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    def check(a: int) -> bool:
        x = pow_mod(a, d, n)
        if x == 1 or x == n - 1:
            return True
        for _ in range(s - 1):
            x = mul_mod(x, x, n)
            if x == n - 1:
                return True
        return False

    for a in _MR_BASES_64:
        if a % n == 0:
            continue
        if not check(a):
            return False
    return True


# ---------------------------
# Pollard-Rho factorization
# ---------------------------


def pollard_rho(n: int) -> int:
    if n % 2 == 0:
        return 2
    if n % 3 == 0:
        return 3
    if is_probable_prime(n):
        return n

    while True:
        c = random.randrange(1, n)
        f = lambda x: (mul_mod(x, x, n) + c) % n
        x = random.randrange(0, n)
        y = x
        d = 1
        while d == 1:
            x = f(x)
            y = f(f(y))
            d = gcd(abs(x - y), n)
        if d != n:
            return d


def factorize(n: int, out: Dict[int, int] | None = None) -> Dict[int, int]:
    if out is None:
        out = {}
    if n == 1:
        return out
    if is_probable_prime(n):
        out[n] = out.get(n, 0) + 1
        return out
    d = pollard_rho(n)
    factorize(d, out)
    factorize(n // d, out)
    return out


def normalize_factorization(fac: Dict[int, int]) -> Dict[int, int]:
    # Pollard recursion can add primes in any order; ensure it's merged and clean
    out: Dict[int, int] = {}
    for p, e in fac.items():
        out[p] = out.get(p, 0) + e
    return out


# ---------------------------
# Modular square roots & CRT
# ---------------------------


def legendre_symbol(a: int, p: int) -> int:
    """Legendre symbol (a/p) for odd prime p. Returns -1,0,1."""
    a %= p
    if a == 0:
        return 0
    t = pow_mod(a, (p - 1) // 2, p)
    return -1 if t == p - 1 else 1


def tonelli_shanks(n: int, p: int) -> int | None:
    """Find r such that r^2 ≡ n (mod p), p odd prime. Return None if no root."""
    n %= p
    if n == 0:
        return 0
    if legendre_symbol(n, p) != 1:
        return None
    if p % 4 == 3:
        return pow_mod(n, (p + 1) // 4, p)

    # factor p-1 = q * 2^s with q odd
    q = p - 1
    s = 0
    while q % 2 == 0:
        q //= 2
        s += 1

    # find z non-residue
    z = 2
    while legendre_symbol(z, p) != -1:
        z += 1

    c = pow_mod(z, q, p)
    r = pow_mod(n, (q + 1) // 2, p)
    t = pow_mod(n, q, p)
    m = s

    while t != 1:
        i = 1
        t2 = (t * t) % p
        while i < m and t2 != 1:
            t2 = (t2 * t2) % p
            i += 1
        b = pow_mod(c, 1 << (m - i - 1), p)
        r = (r * b) % p
        t = (t * b * b) % p
        c = (b * b) % p
        m = i
    return r


def hensel_lift_root(n: int, p: int, e: int, r: int) -> int:
    """
    Lift root r mod p to a root mod p^e.
    Preconditions: p odd prime, r^2 ≡ n (mod p), gcd(2r,p)=1.
    """
    pe = p
    r_mod = r % p
    for _k in range(1, e):
        # solve for t in r' = r + t*pe such that r'^2 ≡ n (mod pe*p)
        # (r^2 - n)/pe + 2r t ≡ 0 (mod p)
        diff = r_mod * r_mod - n
        rhs = (diff // pe) % p
        inv = pow((2 * r_mod) % p, -1, p)
        t = (-rhs * inv) % p
        r_mod = r_mod + t * pe
        pe *= p
    return r_mod % pe


def roots_mod_prime_power(n: int, p: int, e: int) -> List[int]:
    """All roots of x^2 ≡ n (mod p^e) for odd prime p."""
    pe = p**e
    n %= pe

    if n % p == 0:
        # n divisible by p.
        if n == 0:
            # x^2 ≡ 0 (mod p^e): solutions x ≡ 0 (mod p^{ceil(e/2)})
            step = p ** ((e + 1) // 2)
            return list(range(0, pe, step))
        # n divisible by p but not by p^e: only solvable when e==1 (x≡0 mod p)
        return [0] if e == 1 else []

    r = tonelli_shanks(n, p)
    if r is None:
        return []
    if e > 1:
        r = hensel_lift_root(n, p, e, r)
    r2 = (-r) % pe
    if r2 == r:
        return [r]
    return [r, r2]


def crt_pair(a1: int, m1: int, a2: int, m2: int) -> Tuple[int, int]:
    """CRT combine x≡a1 (mod m1), x≡a2 (mod m2), assuming gcd(m1,m2)=1."""
    if m1 == 1:
        return a2 % m2, m2
    if m2 == 1:
        return a1 % m1, m1
    # x = a1 + m1*t, m1*t ≡ a2-a1 (mod m2)
    t = ((a2 - a1) % m2) * pow(m1, -1, m2) % m2
    x = a1 + m1 * t
    return x % (m1 * m2), m1 * m2


# ---------------------------
# Sieve for fast small factoring
# ---------------------------


def sieve_spf(n: int) -> List[int]:
    spf = list(range(n + 1))
    for i in range(2, int(n**0.5) + 1):
        if spf[i] == i:
            step = i
            start = i * i
            for j in range(start, n + 1, step):
                if spf[j] == j:
                    spf[j] = i
    return spf


def factorize_small(x: int, spf: List[int]) -> List[Tuple[int, int]]:
    fac: List[Tuple[int, int]] = []
    while x > 1:
        p = spf[x]
        e = 0
        while x % p == 0:
            x //= p
            e += 1
        fac.append((p, e))
    return fac


# ---------------------------
# Class number h(D) by counting reduced forms
# (D negative fundamental, D ≡ 5 mod 8 for this problem)
# ---------------------------


def class_number(D: int) -> int:
    """
    Compute class number h(D) for a negative fundamental discriminant D.
    For this Euler problem we only encounter D ≡ 5 (mod 8), D odd.
    """
    if D >= 0:
        raise ValueError("D must be negative")
    absD = -D
    amax = isqrt(absD // 3)

    spf = sieve_spf(amax)

    # cache roots for prime powers for this fixed D
    root_cache: Dict[Tuple[int, int], List[int]] = {}

    def roots_mod_prime_power_cached(p: int, e: int) -> List[int]:
        key = (p, e)
        if key in root_cache:
            return root_cache[key]
        root_cache[key] = roots_mod_prime_power(D, p, e)
        return root_cache[key]

    h = 0

    # For D ≡ 5 (mod 8), there are no reduced forms with even 'a'
    for a in range(1, amax + 1, 2):
        fac_a = factorize_small(a, spf)

        # If p|D and p^2|a, no solution to x^2 ≡ D (mod p^2)
        bad = False
        for p, e in fac_a:
            if e >= 2 and D % p == 0:
                bad = True
                break
        if bad:
            continue

        # Build roots modulo a via CRT from prime power roots
        roots = [0]
        mod = 1
        ok = True
        for p, e in fac_a:
            pe = p**e
            rset = roots_mod_prime_power_cached(p, e)
            if not rset:
                ok = False
                break
            new_roots: List[int] = []
            new_mod = mod * pe
            for r0 in roots:
                for r in rset:
                    x, m = crt_pair(r0, mod, r, pe)
                    new_roots.append(x)
            roots = new_roots
            mod = new_mod
        if not ok:
            continue

        # Each residue r mod a corresponds to a unique b in [-a, a] with correct parity:
        # - If r==0, the odd choice is b=+a (b=0 even, b=-a not allowed in reduced boundary cases)
        # - Else choose b=r if odd else b=r-a (which flips parity because a is odd)
        for r in roots:
            if r == 0:
                b = a
            else:
                b = r if (r & 1) else (r - a)

            if abs(b) > a:
                continue

            num = b * b - D
            den = 4 * a
            if num % den != 0:
                continue
            c = num // den
            if a > c:
                continue

            # reduced boundary rule
            if (abs(b) == a or a == c) and b < 0:
                continue

            h += 1

    return h


# ---------------------------
# Sigma and the main G(n)
# ---------------------------


def sigma_from_factorization(fac: Dict[int, int]) -> int:
    s = 1
    for p, e in fac.items():
        s *= (p ** (e + 1) - 1) // (p - 1)
    return s


def G(n: int) -> int:
    N = 8 * n + 3
    facN = normalize_factorization(factorize(N))

    # write N = n0 * f^2 with n0 squarefree
    n0 = 1
    f = 1
    for p, e in facN.items():
        if e & 1:
            n0 *= p
        f *= p ** (e // 2)

    D = -n0  # fundamental discriminant for this problem
    h = class_number(D)

    # L(chi_D, 0) = h(D)/(w(D)/2), where w(-3)=6, w(-4)=4, otherwise w=2
    if D == -3:
        w_div2 = 3
    elif D == -4:
        w_div2 = 2
    else:
        w_div2 = 1

    # S = sum_{d|f} mu(d) * (D/d) * sigma(f/d)
    # Only squarefree d contribute, so iterate over subsets of primes dividing f.
    if f == 1:
        S = 1
    else:
        facF = normalize_factorization(factorize(f))
        primes = list(facF.keys())
        exps = [facF[p] for p in primes]

        # precompute sigma for each subset by adjusting exponents
        S = 0
        for mask in range(1 << len(primes)):
            bits = 0
            jac = 1
            sig = 1
            for i, p in enumerate(primes):
                e = exps[i]
                if (mask >> i) & 1:
                    bits += 1
                    # (D/p), can be 0 if p|D
                    jac *= legendre_symbol(D, p)
                    e -= 1
                if e < 0:
                    sig = 0
                    break
                sig *= (p ** (e + 1) - 1) // (p - 1)
            if sig == 0:
                continue
            sign = -1 if (bits & 1) else 1
            S += sign * jac * sig

    # G(n) = 3 * L(chi_D,0) * S = 3 * h * S / w_div2
    numerator = 3 * h * S
    if numerator % w_div2 != 0:
        raise ArithmeticError("Expected exact division failed")
    return numerator // w_div2


def main() -> None:
    # Tests from the problem statement
    assert G(9) == 7
    assert G(1000) == 78
    assert G(10**6) == 2106

    target = 17526 * 10**9
    print(G(target))


if __name__ == "__main__":
    main()
