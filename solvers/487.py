#!/usr/bin/env python3
"""
Project Euler 487 - Sums of Power Sums

Compute:
    sum( S_10000(10^12) mod p )
over primes p in [2*10^9, 2*10^9 + 2000].

No external libraries are used.
"""

import math


def power_sum_exact(k: int, n: int) -> int:
    """f_k(n) exactly, for small n (used only in asserts)."""
    return sum(i**k for i in range(1, n + 1))


def S_exact(k: int, n: int) -> int:
    """S_k(n) exactly, for small n (used only in asserts)."""
    fk = 0
    s = 0
    for i in range(1, n + 1):
        fk += i**k
        s += fk
    return s


def sieve_primes(limit: int) -> list[int]:
    """Return all primes <= limit."""
    if limit < 2:
        return []
    is_p = bytearray(b"\x01") * (limit + 1)
    is_p[0:2] = b"\x00\x00"
    for i in range(2, math.isqrt(limit) + 1):
        if is_p[i]:
            start = i * i
            step = i
            is_p[start : limit + 1 : step] = b"\x00" * (((limit - start) // step) + 1)
    return [i for i in range(limit + 1) if is_p[i]]


def primes_in_interval(L: int, R: int) -> list[int]:
    """List primes in [L, R] via trial division using primes up to sqrt(R)."""
    small = sieve_primes(math.isqrt(R) + 1)
    out = []
    for x in range(L, R + 1):
        if x < 2:
            continue
        is_prime = True
        for p in small:
            if p * p > x:
                break
            if x % p == 0:
                is_prime = x == p
                break
        if is_prime:
            out.append(x)
    return out


def inv_factorials_up_to(max_d: int, p: int) -> list[int]:
    """
    Compute inv_fact[i] = (i!)^{-1} mod p for i=0..max_d.
    Requires p to be prime and p > max_d (true for this problem).
    """
    fact = [1] * (max_d + 1)
    for i in range(1, max_d + 1):
        fact[i] = (fact[i - 1] * i) % p

    inv_fact = [1] * (max_d + 1)
    inv_fact[max_d] = pow(fact[max_d], p - 2, p)  # Fermat inverse
    for i in range(max_d, 0, -1):
        inv_fact[i - 1] = (inv_fact[i] * i) % p
    return inv_fact


def lagrange_eval_0_to_d(
    y: list[int], n: int, d: int, p: int, inv_fact: list[int]
) -> int:
    """
    Evaluate polynomial P at n modulo p, given y[i]=P(i) for i=0..d.

    Uses O(d) Lagrange interpolation specialized to x = 0,1,2,...,d:
        denom(i) = i! * (-1)^(d-i) * (d-i)!
    """
    if n <= d:
        return y[n]

    pre = [1] * (d + 2)
    for i in range(d + 1):
        pre[i + 1] = (pre[i] * (n - i)) % p

    suf = [1] * (d + 2)
    for i in range(d, -1, -1):
        suf[i] = (suf[i + 1] * (n - i)) % p

    res = 0
    for i in range(d + 1):
        num = (pre[i] * suf[i + 1]) % p  # product_{j!=i} (n - j)
        term = (y[i] * num) % p
        term = (term * inv_fact[i]) % p
        term = (term * inv_fact[d - i]) % p
        if (d - i) & 1:
            res -= term
        else:
            res += term
    return res % p


def prefix_power_sums_for_fk_and_fk1(
    k: int, d1: int, d2: int, p: int
) -> tuple[list[int], list[int]]:
    """
    Build:
      yk[i]  = f_k(i)     for i=0..d1
      yk1[i] = f_{k+1}(i) for i=0..d2

    Computed in one pass up to d2 using one pow() per i.
    """
    yk = [0] * (d1 + 1)
    yk1 = [0] * (d2 + 1)
    s0 = 0
    s1 = 0
    for i in range(1, d2 + 1):
        pk = pow(i, k, p)  # i^k mod p
        s0 = (s0 + pk) % p
        if i <= d1:
            yk[i] = s0  # f_k(i)
        s1 = (s1 + (pk * i) % p) % p  # add i^(k+1)
        yk1[i] = s1  # f_{k+1}(i)
    return yk, yk1


def S_k_mod_prime(k: int, n: int, p: int) -> int:
    """
    Compute S_k(n) mod p for prime p.
    Uses:
        S_k(n) = (n+1) * f_k(n) - f_{k+1}(n)
    and Lagrange interpolation for f_k and f_{k+1}.
    """
    d1 = k + 1  # degree of f_k
    d2 = k + 2  # degree of f_{k+1}
    n0 = n % p  # element of field F_p

    inv_fact = inv_factorials_up_to(d2, p)
    yk, yk1 = prefix_power_sums_for_fk_and_fk1(k, d1, d2, p)

    fk = lagrange_eval_0_to_d(yk, n0, d1, p, inv_fact)
    fk1 = lagrange_eval_0_to_d(yk1, n0, d2, p, inv_fact)

    return (((n + 1) % p) * fk - fk1) % p


def solve() -> int:
    # Asserts from the problem statement:
    assert power_sum_exact(2, 10) == 385
    assert S_exact(4, 100) == 35375333830

    L = 2_000_000_000
    R = L + 2000
    n = 10**12
    k = 10000

    primes = primes_in_interval(L, R)
    total = 0
    for p in primes:
        total += S_k_mod_prime(k, n, p)
    return total


if __name__ == "__main__":
    print(solve())
