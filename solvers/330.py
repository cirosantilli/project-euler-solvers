#!/usr/bin/env python3
"""Project Euler 330

Let a(n) be defined for all integers n by

    a(n) = \sum_{i>=1} a(n-i)/i!   for n >= 0
    a(n) = 1                      for n < 0

It can be shown that for each n >= 0 there are unique integers A(n), B(n) such that

    a(n) = (A(n)*e + B(n)) / n!

The problem asks for:

    (A(10^9) + B(10^9)) mod 77777777

This program computes the result using modular arithmetic (CRT over the prime
factorization of 77777777) and a finite-field / "divided power" trick.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import comb


MOD = 77_777_777
N_TARGET = 10**9
PRIMES = (7, 11, 73, 101, 137)  # factorization of 77777777


def compute_AB_small(n_max: int) -> tuple[list[int], list[int]]:
    """Compute exact A(n), B(n) for n<=n_max via the integer recurrence.

    Recurrences (derived from the definition):
        A(0)=1, B(0)=-1
        A(n) = n! + \sum_{k=0}^{n-1} C(n,k) A(k)
        B(n) = \sum_{k=0}^{n-1} C(n,k) B(k) - \sum_{i=0}^{n} n!/i!
    """

    fact = [1] * (n_max + 1)
    for i in range(1, n_max + 1):
        fact[i] = fact[i - 1] * i

    # T(n) = sum_{i=0}^n n!/i! is integral
    T = [0] * (n_max + 1)
    for n in range(n_max + 1):
        T[n] = sum(fact[n] // fact[i] for i in range(n + 1))

    A = [0] * (n_max + 1)
    B = [0] * (n_max + 1)
    A[0] = 1
    B[0] = -1

    for n in range(1, n_max + 1):
        sA = 0
        sB = 0
        for k in range(n):
            c = comb(n, k)
            sA += c * A[k]
            sB += c * B[k]
        A[n] = fact[n] + sA
        B[n] = sB - T[n]

    return A, B


def _comb_small(n: int, k: int, p: int) -> int:
    """Compute C(n,k) mod p for 0<=n<p (small n) with a multiplicative formula."""
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    num = 1
    den = 1
    for i in range(1, k + 1):
        num = (num * (n - (k - i))) % p
        den = (den * i) % p
    return (num * pow(den, -1, p)) % p


def s_mod_prime(n: int, p: int) -> int:
    """Compute S(n) = A(n)+B(n) modulo a prime p.

    Key identity over F_p in the divided-power algebra:

        exp(t)^p = exp(p t) = 1   (mod p)

    Hence E := exp(t) satisfies E^p = 1, so any rational function of E can be
    reduced to a polynomial in E of degree < p.

    The exponential generating function for S(n) is:

        S(t) = \sum_{n>=0} S(n) t^n/n! = (1 - exp(t)) / ((1 - t)(2 - exp(t)))

    Let R(E) = (1 - E)/(2 - E). In F_p with relation E^p=1,

        (2 - E)^{-1} = \sum_{i=0}^{p-1} (2^{-i}) E^i

    so R(E) = \sum_{i=0}^{p-1} r_i E^i with r_0=0 and r_i = 2^{-i} - 2^{-(i-1)}.

    Coefficient extraction in the divided-power basis gives:

        R_n = [t^n/n!] R(E) = \sum_{i=1}^{p-1} r_i i^n  (mod p)

    and since (1 - t)^{-1} = \sum_{m=0}^{p-1} t^m (because t^p=0 mod p), we get

        S(n) = \sum_{m=0}^{p-1} C(n,m) m! R_{n-m}  (mod p)

    With Lucas, for m<p: C(n,m) mod p depends only on n mod p.
    """

    n0 = n % p

    inv2 = pow(2, -1, p)

    # r_i coefficients for R(E) = (1-E)/(2-E) in the quotient with E^p=1.
    # We compute r_i via powers of inv2:
    #   r_0 = 1 - inv2^(p-1) = 0  (since inv2^(p-1)=1)
    #   r_i = inv2^i - inv2^(i-1) for i>=1
    r = [0] * p
    inv2_pow = 1  # inv2^0
    prev = 1
    for i in range(1, p):
        inv2_pow = (inv2_pow * inv2) % p
        r[i] = (inv2_pow - prev) % p
        prev = inv2_pow

    # Precompute R_n as a function of n mod (p-1): for i in F_p^*, i^(p-1)=1.
    r_exp = [0] * (p - 1)
    for e in range(p - 1):
        s = 0
        for i in range(1, p):
            s = (s + r[i] * pow(i, e, p)) % p
        r_exp[e] = s

    # Factorials up to n0 and binom(n0, m) for m<=n0.
    fact = [1] * (n0 + 1)
    for i in range(1, n0 + 1):
        fact[i] = (fact[i - 1] * i) % p

    res = 0
    for m in range(0, n0 + 1):
        c_nm = _comb_small(n0, m, p)  # Lucas: C(n,m) mod p == C(n0,m) for m<p
        e = (n - m) % (p - 1)
        res = (res + fact[m] * c_nm * r_exp[e]) % p

    return res


def crt(residues: list[int], moduli: list[int]) -> int:
    """Chinese Remainder Theorem for pairwise coprime moduli."""
    x = 0
    m = 1
    for a_i, m_i in zip(residues, moduli):
        # Solve: x + m*t ≡ a_i (mod m_i)
        t = ((a_i - x) % m_i) * pow(m % m_i, -1, m_i) % m_i
        x += m * t
        m *= m_i
    return x % m


def solve(n: int = N_TARGET) -> int:
    residues = [s_mod_prime(n, p) for p in PRIMES]
    return crt(residues, list(PRIMES))


def _run_self_tests() -> None:
    # Test values explicitly stated in the problem statement.
    A, B = compute_AB_small(10)

    # a(0)=e-1
    assert A[0] == 1 and B[0] == -1

    # a(1)=2e-3
    assert A[1] == 2 and B[1] == -3

    # a(2)=(7/2)e - 6  => (7e-12)/2!
    assert A[2] == 7 and B[2] == -12

    # a(10) = (328161643 e - 652694486)/10!
    assert A[10] == 328_161_643 and B[10] == -652_694_486


def main() -> None:
    _run_self_tests()
    print(solve(N_TARGET))


if __name__ == "__main__":
    main()
