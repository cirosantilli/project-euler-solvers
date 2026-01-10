#!/usr/bin/env python3
"""
Project Euler 560: Coprime Nim

Coprime Nim is normal-play Nim, except a move from a pile of size m may remove
only a number r with gcd(r, m) = 1. The player who removes the last stone wins.

Let L(n, k) be the number of losing starting positions (perfect play) with k piles,
each pile size in [1, n-1].

This program prints L(10^7, 10^7) mod 1_000_000_007 and includes asserts for the
test values given in the problem statement.

No external libraries are used.
"""

from array import array
from math import isqrt

MOD = 1_000_000_007


def fwht_xor_inplace(a, mod=MOD):
    """In-place unnormalized Walsh–Hadamard transform for XOR convolution."""
    n = len(a)
    h = 1
    while h < n:
        step = h << 1
        for i in range(0, n, step):
            j = i
            end = i + h
            while j < end:
                x = a[j]
                y = a[j + h]
                s = x + y
                if s >= mod:
                    s -= mod
                d = x - y
                if d < 0:
                    d += mod
                a[j] = s
                a[j + h] = d
                j += 1
        h = step


def compute_L(n: int, k: int, mod: int = MOD) -> int:
    """
    Compute L(n, k) mod mod.

    Grundy numbers for a single pile:
      g(0)=0, g(1)=1
      if m is even: g(m)=0
      if m is odd and m>1: let p = smallest prime factor of m, then g(m)=pi(p),
        where pi(p) is the prime index (pi(2)=1, pi(3)=2, ...).

    If c[g] counts how many pile sizes in [1..n-1] have Grundy value g,
    then losing k-tuples are exactly those with XOR of Grundy values == 0.

    Using FWHT for XOR-convolution:
      Let C = FWHT(c) (unnormalized). Then
        L(n,k) = (1/M) * sum_i C[i]^k   (mod),
      where M is the transform size (power of 2).
    """
    if n <= 1:
        return 0
    N = n - 1  # maximum pile size included

    # Grundy 0 for all even pile sizes
    even_count = N // 2

    # Sieve only odds up to N to count how many numbers have each smallest odd prime factor.
    # Represent odd x as x = 2*i + 1, i = 0..(N-1)//2.
    odd_len = (N + 1) // 2  # number of odds <= N
    spf = (
        array("I", [0]) * odd_len
    )  # smallest prime factor for each odd (0 = unassigned)

    # counts[0] is a dummy for prime 2 (pi(2)=1 but never appears as spf of an odd).
    # For odd primes in increasing order, counts[j] = how many odd m<=N have spf == that prime,
    # where that prime has index (j+1) in the primes list (since counts[1] corresponds to pi=2).
    counts = array("I", [0])

    limit = isqrt(N)
    i_end = (limit - 1) // 2  # largest i with (2*i+1) <= sqrt(N)

    for i in range(1, i_end + 1):
        if spf[i] == 0:
            p = 2 * i + 1
            spf[i] = p  # mark the prime itself to avoid counting it again later
            counts.append(1)  # count the prime itself (its spf is p)

            start = (p * p - 1) // 2  # index of p^2
            step = p
            for j in range(start, odd_len, step):
                if spf[j] == 0:
                    spf[j] = p
                    counts[-1] += 1

    # Remaining unassigned odds (excluding 1) are primes > sqrt(N); each contributes count 1.
    for i in range(1, odd_len):
        if spf[i] == 0:
            counts.append(1)
            spf[i] = 2 * i + 1  # not required, but keeps the array consistent

    # P = number of primes <= N (including 2). Max Grundy value is P.
    P = len(counts)

    # FWHT length must be a power of 2 >= (P + 1).
    M = 1 << ((P + 1).bit_length())

    # Frequency vector c, padded to length M.
    a = [0] * M
    a[0] = even_count % mod
    a[1] = 1  # pile size 1 has Grundy 1
    # For prime index idx>=2 (odd primes), Grundy == idx with count counts[idx-1].
    for idx in range(2, P + 1):
        a[idx] = counts[idx - 1] % mod

    fwht_xor_inplace(a, mod)

    total = 0
    for v in a:
        total = (total + pow(v, k, mod)) % mod

    # Inverse FWHT at index 0 is average of all entries.
    total = (total * pow(M, mod - 2, mod)) % mod
    return total


def _self_test():
    # Test values from the problem statement
    assert compute_L(5, 2) == 6
    assert compute_L(10, 5) == 9964
    assert compute_L(10, 10) == 472400303
    assert compute_L(10**3, 10**3) == 954021836


def solve():
    _self_test()
    print(compute_L(10**7, 10**7))


if __name__ == "__main__":
    solve()
