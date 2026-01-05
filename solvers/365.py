#!/usr/bin/env python3
"""
Project Euler 365 - A huge binomial coefficient

We need:
    sum_{1000<p<q<r<5000, primes}  M(10^18, 10^9, p*q*r)
where M(n,k,m) = C(n,k) mod m.

Key ideas:
- For each prime p, compute C(N,K) mod p using Lucas' theorem.
- For each triple (p,q,r), reconstruct C(N,K) mod (p*q*r) using CRT.
"""

from array import array
from math import isqrt


N = 10**18
K = 10**9


def primes_between(lo: int, hi: int) -> list[int]:
    """Return primes p with lo < p < hi (hi is exclusive)."""
    if hi <= 2:
        return []
    sieve = bytearray(b"\x01") * hi
    sieve[:2] = b"\x00\x00"
    for i in range(2, isqrt(hi - 1) + 1):
        if sieve[i]:
            step = i
            start = i * i
            sieve[start:hi:step] = b"\x00" * (((hi - 1 - start) // step) + 1)
    return [p for p in range(lo + 1, hi) if sieve[p]]


def binom_mod_prime_lucas(n: int, k: int, p: int) -> int:
    """
    Compute C(n,k) mod prime p using Lucas' theorem.
    Precomputes factorials modulo p for digits < p.
    """
    # factorials modulo p, for values 0..p-1
    fact = [1] * p
    for i in range(1, p):
        fact[i] = (fact[i - 1] * i) % p

    invfact = [1] * p
    invfact[p - 1] = pow(fact[p - 1], p - 2, p)
    for i in range(p - 1, 0, -1):
        invfact[i - 1] = (invfact[i] * i) % p

    def comb_small(nn: int, kk: int) -> int:
        return fact[nn] * invfact[kk] % p * invfact[nn - kk] % p

    res = 1
    while k or n:
        ni = n % p
        ki = k % p
        if ki > ni:
            return 0
        res = (res * comb_small(ni, ki)) % p
        n //= p
        k //= p
    return res


def precompute_inverses(primes: list[int]) -> list[array]:
    """
    For each i, store inverses of primes[i] modulo primes[j] for all j>i.
    inv_rows[i][j-i-1] = (primes[i])^{-1} mod primes[j].
    Stored as array('H') because values < 5000.
    """
    L = len(primes)
    inv_rows: list[array] = [array("H") for _ in range(L)]
    for i, p in enumerate(primes):
        row = inv_rows[i]
        for j in range(i + 1, L):
            q = primes[j]
            row.append(pow(p, q - 2, q))
    return inv_rows


def solve() -> int:
    primes = primes_between(1000, 5000)  # 1000 < p < 5000
    # No sample test values are provided in the original problem statement.

    residues = [binom_mod_prime_lucas(N, K, p) for p in primes]
    inv_rows = precompute_inverses(primes)

    L = len(primes)
    total = 0

    # Localize for speed in Python's tight loops.
    primes_list = primes
    residues_list = residues
    inv_list = inv_rows

    # CRT / Garner-style reconstruction:
    #  x1 = a (mod p), x1 = b (mod q)  ->  x1 in [0, p*q)
    #  x  = x1 (mod p*q), x = c (mod r) -> x in [0, p*q*r)
    for i in range(L - 2):
        p = primes_list[i]
        a = residues_list[i]
        inv_i = inv_list[i]  # inverses of p mod later primes

        for j in range(i + 1, L - 1):
            q = primes_list[j]
            b = residues_list[j]

            inv_p_mod_q = inv_i[j - i - 1]
            t1 = ((b - a) % q) * inv_p_mod_q % q
            x1 = a + p * t1  # unique modulo p*q, and 0 <= x1 < p*q
            pq = p * q

            inv_j = inv_list[j]  # inverses of q mod later primes

            for k in range(j + 1, L):
                r = primes_list[k]
                c = residues_list[k]

                inv_p_mod_r = inv_i[k - i - 1]
                inv_q_mod_r = inv_j[k - j - 1]
                inv_pq_mod_r = (inv_p_mod_r * inv_q_mod_r) % r  # (p*q)^{-1} mod r

                t2 = ((c - x1) % r) * inv_pq_mod_r % r
                total += x1 + pq * t2

    return total


def main() -> None:
    print(solve())


if __name__ == "__main__":
    main()
