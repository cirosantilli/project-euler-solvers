#!/usr/bin/env python3
"""
Project Euler 633: Square Prime Factors II

Compute c_7^{infty} = lim_{N->infty} C_7(N)/N, where C_k(N) counts integers 1..N
with exactly k primes p such that p^2 divides n.

No external libraries are used.
"""

from __future__ import annotations

import math
from typing import List, Tuple, Dict


# --------- Basic number theory helpers ---------


def primes_upto(n: int) -> List[int]:
    """Return all primes <= n using an odd-only sieve."""
    if n < 2:
        return []
    # Represent only odd numbers: index i represents (2*i + 1)
    size = (n + 1) // 2
    sieve = bytearray(b"\x01") * size
    sieve[0] = 0  # 1 is not prime
    limit = math.isqrt(n)
    for p in range(3, limit + 1, 2):
        if sieve[p // 2]:
            start = p * p
            step = p  # in index units (value steps by 2*p)
            count = ((n - start) // (2 * p)) + 1
            sieve[start // 2 : size : step] = b"\x00" * count
    primes = [2]
    primes.extend(2 * i + 1 for i in range(1, size) if sieve[i])
    return primes


def mobius_and_omega_upto(n: int) -> Tuple[List[int], List[int]]:
    """
    Linear sieve for Mobius mu[0..n] and omega[0..n] where omega(x) is the number
    of DISTINCT prime factors of x.
    """
    lp = [0] * (n + 1)
    mu = [0] * (n + 1)
    omega = [0] * (n + 1)
    primes: List[int] = []

    mu[1] = 1
    omega[1] = 0
    for i in range(2, n + 1):
        if lp[i] == 0:
            lp[i] = i
            primes.append(i)
            mu[i] = -1
            omega[i] = 1
        for p in primes:
            v = p * i
            if v > n:
                break
            lp[v] = p
            if i % p == 0:
                mu[v] = 0
                omega[v] = omega[i]  # p already counted
                break
            else:
                mu[v] = -mu[i]
                omega[v] = omega[i] + 1
    return mu, omega


def square_prime_factors(n: int) -> List[int]:
    """Return primes p such that p^2 divides n (for small sanity checks)."""
    out = []
    x = n
    p = 2
    while p * p <= x:
        if x % p == 0:
            cnt = 0
            while x % p == 0:
                x //= p
                cnt += 1
            if cnt >= 2:
                out.append(p)
        p += 1 if p == 2 else 2  # 2 then odd numbers
    return out


# --------- Exact finite-N checker (used only for asserts) ---------


def squarefree_count(M: int, mu: List[int]) -> int:
    """
    Count squarefree integers <= M using:
        Q(M) = sum_{i=1..floor(sqrt(M))} mu(i) * floor(M / i^2)
    """
    r = math.isqrt(M)
    s = 0
    for i in range(1, r + 1):
        s += mu[i] * (M // (i * i))
    return s


def Ck_counts(N: int, mu: List[int], omega: List[int], max_k: int = 10) -> List[int]:
    """
    Compute C_k(N) for k<=max_k using the bijection n = a * b^2 where a is squarefree.
    Then square prime factors of n are exactly the primes dividing b, hence count = omega(b).

    C_k(N) = sum_{b^2 <= N, omega(b)=k} Q(floor(N/b^2)), where Q is squarefree_count.
    """
    bmax = math.isqrt(N)
    C = [0] * (max_k + 1)
    cache: Dict[int, int] = {}  # memoize Q(M) for this N

    for b in range(1, bmax + 1):
        w = omega[b]
        if w > max_k:
            continue
        M = N // (b * b)
        q = cache.get(M)
        if q is None:
            q = squarefree_count(M, mu)
            cache[M] = q
        C[w] += q
    return C


# --------- Limit constant computation ---------


def c_infty(k: int, prime_limit: int = 10_000_000) -> float:
    """
    The limiting distribution factorizes over primes:
        G(x) = Π_p ((1 - 1/p^2) + (1/p^2) x)
    and
        c_k^∞ = [x^k] G(x).

    Rewriting gives:
        c_k^∞ = (Π_p (1 - 1/p^2)) * e_k( 1/(p^2 - 1) over primes p )
             = (6/π^2) * e_k(...)

    We compute e_k via DP on the polynomial Π_p (1 + r_p t), r_p = 1/(p^2 - 1).
    """
    primes = primes_upto(prime_limit)
    coeff = [0.0] * (k + 1)
    coeff[0] = 1.0
    for p in primes:
        r = 1.0 / (p * p - 1.0)
        for j in range(k, 0, -1):
            coeff[j] += coeff[j - 1] * r
    c0 = 6.0 / (math.pi * math.pi)
    return c0 * coeff[k]


def format_scientific_5(x: float) -> str:
    """
    Scientific notation with 5 significant digits, and exponent without leading zeros.
    Example: 1.2346e-4
    """
    mant, exp = f"{x:.4e}".split("e")
    return f"{mant}e{int(exp)}"


def _run_asserts() -> None:
    # Example in statement
    assert set(square_prime_factors(1500)) == {2, 5}

    # Table values in statement for C_k(10^n), k=0..4
    table = {
        10: [7, 3, 0, 0, 0],
        10**2: [61, 36, 3, 0, 0],
        10**3: [608, 343, 48, 1, 0],
        10**4: [6083, 3363, 533, 21, 0],
        10**5: [60794, 33562, 5345, 297, 2],
        10**6: [607926, 335438, 53358, 3218, 60],
        10**7: [6079291, 3353956, 533140, 32777, 834],
        10**8: [60792694, 33539196, 5329747, 329028, 9257],
        10**9: [607927124, 335389706, 53294365, 3291791, 95821],
    }
    maxN = max(table)
    mu, omega = mobius_and_omega_upto(math.isqrt(maxN))

    for N, expected in table.items():
        got = Ck_counts(N, mu, omega, max_k=8)[:5]
        assert got == expected, f"C_k({N}) mismatch: got {got}, expected {expected}"


def main() -> None:
    _run_asserts()
    ans = c_infty(7, prime_limit=10_000_000)
    print(format_scientific_5(ans))


if __name__ == "__main__":
    main()
