#!/usr/bin/env python3
"""Project Euler 282: The Ackermann function.

Compute:
    S = sum_{n=0..6} A(n,n) (mod 14^8)

Ackermann:
    A(0,n) = n+1
    A(m,0) = A(m-1,1)                     (m>0)
    A(m,n) = A(m-1, A(m,n-1))             (m,n>0)

Key identity (for m>=1):
    A(m,n) = H_m(2, n+3) - 3
where H_m is the hyperoperation sequence (addition, multiplication, exponentiation,
tetration, ...). This reduces the hard cases to modular tetration of base 2.

We only need A(n,n) for n<=6, modulo 14^8.
"""

from __future__ import annotations

from functools import lru_cache
from math import gcd
from typing import Dict, Tuple


MOD = 14**8


# ---------------------------- number theory helpers ----------------------------


def _factorize(n: int) -> Dict[int, int]:
    """Trial division factorization (fast enough for n <= a few million)."""
    factors: Dict[int, int] = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        if d == 2:
            d = 3
        else:
            d += 2
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def _lcm(a: int, b: int) -> int:
    return a // gcd(a, b) * b


@lru_cache(None)
def carmichael_lambda(n: int) -> int:
    """Carmichael's lambda function for positive integers n."""
    if n <= 0:
        raise ValueError("lambda(n) requires n>0")
    if n == 1:
        return 1

    fac = _factorize(n)
    lam = 1
    for p, k in fac.items():
        if p == 2:
            # λ(2)=1, λ(4)=2, λ(2^k)=2^(k-2) for k>=3
            if k == 1:
                pk = 1
            elif k == 2:
                pk = 2
            else:
                pk = 2 ** (k - 2)
        else:
            # for odd prime powers: λ(p^k) = φ(p^k)
            pk = (p - 1) * (p ** (k - 1))
        lam = _lcm(lam, pk)
    return lam


def _egcd(a: int, b: int) -> Tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    g, x1, y1 = _egcd(b, a % b)
    return g, y1, x1 - (a // b) * y1


def crt_pair(a1: int, m1: int, a2: int, m2: int) -> int:
    """CRT for coprime moduli: x≡a1 (mod m1), x≡a2 (mod m2)."""
    if gcd(m1, m2) != 1:
        raise ValueError("CRT requires coprime moduli")
    _, x, _ = _egcd(m1, m2)
    inv_m1_mod_m2 = x % m2
    k = ((a2 - a1) % m2) * inv_m1_mod_m2 % m2
    return (a1 + k * m1) % (m1 * m2)


# --------------------------- base-2 tetration modulo --------------------------


def _tetration_exact_height(h: int) -> int:
    """Exact 2^^h for very small h."""
    v = 2
    for _ in range(2, h + 1):
        v = 2**v
    return v


def _tower_geq(h: int, limit: int) -> bool:
    """Return True iff 2^^h >= limit, without constructing huge integers."""
    if limit <= 1:
        return True
    v = 2
    if h == 1:
        return v >= limit

    # Quickly cap growth: once v is even moderately large, 2**v dwarfs any limit
    # relevant to our moduli.
    for _ in range(2, h + 1):
        if v >= 60:
            return True
        v = 2**v
        if v >= limit:
            return True
    return v >= limit


@lru_cache(None)
def tetration_mod(height: int, mod: int) -> int:
    """Compute 2^^height (tetration) modulo mod."""
    if mod == 1:
        return 0
    if height <= 0:
        raise ValueError("height must be >= 1")
    if height == 1:
        return 2 % mod

    # Split modulus into 2^k * odd (coprime parts), solve each, recombine via CRT.
    m = mod
    k = 0
    while (m & 1) == 0:
        k += 1
        m >>= 1

    # Part 1: modulo 2^k
    r2 = 0
    if k > 0:
        mod2 = 1 << k
        # 2^^height = 2^(2^^(height-1)). For 2^k, this is 0 once the exponent >= k.
        if _tower_geq(height - 1, k):
            r2 = 0
        else:
            exp = _tetration_exact_height(height - 1)
            r2 = 0 if exp >= k else (1 << exp) % mod2
        if m == 1:
            return r2

    # Part 2: modulo odd m, where gcd(2,m)=1
    lam = carmichael_lambda(m)
    exp = tetration_mod(height - 1, lam)
    rodd = pow(2, exp, m)

    if k == 0:
        return rodd
    return crt_pair(r2, 1 << k, rodd, m)


def _find_tetration_fixed_height(mod: int, max_h: int = 60) -> int:
    """Find an h such that 2^^h ≡ 2^^(h+1) (mod mod).

    For our modulus this happens quickly. We use it to represent 'astronomically large'
    tetration heights (like those arising in A(5,5) and A(6,6)).
    """
    prev = tetration_mod(1, mod)
    for h in range(2, max_h + 1):
        cur = tetration_mod(h, mod)
        if cur == prev:
            return h - 1
        prev = cur
    return max_h


# ------------------------------ Ackermann pieces ------------------------------


def ackermann_small(m: int, n: int) -> int:
    """Exact Ackermann for small m (used only for the problem's sample asserts)."""
    if m == 0:
        return n + 1
    if m == 1:
        return n + 2
    if m == 2:
        return 2 * n + 3
    if m == 3:
        return (1 << (n + 3)) - 3
    raise ValueError("ackermann_small only supports m<=3")


def solve() -> int:
    # Problem statement test values
    assert ackermann_small(1, 0) == 2
    assert ackermann_small(2, 2) == 7
    assert ackermann_small(3, 4) == 125

    m = MOD

    # A(0,0)=1
    a0 = 1 % m

    # A(1,1)=3, A(2,2)=7, A(3,3)=2^(6)-3=61
    a1 = 3 % m
    a2 = 7 % m
    a3 = 61 % m

    # A(4,4) = 2^^7 - 3
    a4 = (tetration_mod(7, m) - 3) % m

    # For our modulus, the base-2 tetration sequence reaches a fixed point quickly.
    fixed_h = _find_tetration_fixed_height(m)
    fixed_val = (tetration_mod(fixed_h, m) - 3) % m

    # A(5,5) and A(6,6) correspond to tetration heights that are far beyond fixed_h.
    a5 = fixed_val
    a6 = fixed_val

    ans = (a0 + a1 + a2 + a3 + a4 + a5 + a6) % m
    print(ans)
    return ans


if __name__ == "__main__":
    solve()
