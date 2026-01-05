#!/usr/bin/env python3
"""
Project Euler 423: Consecutive Die Throws

We count sequences of n throws of a fair 6-sided die.
Let c be the number of equal consecutive pairs.
We need C(n): #sequences with c <= pi(n), where pi(n) is the prime-counting function.
Finally S(L) = sum_{n=1..L} C(n) (mod 1_000_000_007) for L = 50_000_000.

This solution avoids any external libraries (standard library only).
"""

from array import array
import math

MOD = 1_000_000_007


def sieve_odd_primes_upto(n: int) -> bytearray:
    """
    Odd-only sieve.
    Index i corresponds to odd number (2*i + 1) == (i << 1) + 1.
    We also use the convenient mapping idx = odd // 2.
    Returns a bytearray s where s[odd//2] is 1 iff odd is prime (odd >= 3).
    Note: s[0] corresponds to 1 and is set to 0.
    """
    size = n // 2 + 1
    s = bytearray(b"\x01") * size
    if size:
        s[0] = 0  # 1 is not prime

    limit = int(math.isqrt(n))
    for p in range(3, limit + 1, 2):
        if s[p >> 1]:
            start = (p * p) >> 1
            step = p
            # count of items to zero out in the slice
            cnt = ((size - start - 1) // step) + 1
            s[start::step] = b"\x00" * cnt
    return s


def pi_small(n: int) -> int:
    """Prime-counting function for small n (used only in asserts)."""
    if n < 2:
        return 0
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for p in range(2, int(n**0.5) + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start : n + 1 : step] = [False] * (((n - start) // step) + 1)
    return sum(1 for i in range(2, n + 1) if sieve[i])


def C_exact_small(n: int) -> int:
    """
    Exact C(n) for small n (used only in asserts).
    Uses the closed form:
      f(n,c) = 6 * 5^(n-c-1) * binom(n-1,c)  for exact c matches
      C(n)   = sum_{c=0..pi(n)} f(n,c)
    """
    from math import comb  # standard library

    k = pi_small(n)
    top = min(k, n - 1)
    total = 0
    for c in range(top + 1):
        total += 6 * (5 ** (n - c - 1)) * comb(n - 1, c)
    return total


def solve(L: int = 50_000_000) -> int:
    """
    Returns S(L) mod MOD.
    Core idea:
      Let k = pi(n), and let b(n) be the number of sequences of length n with exactly k matches.
      Then we can update C(n) and b(n) in O(1) per n, with a special case when n+1 is prime.
    To speed up, we process two steps at once (even n -> odd n+1 -> even n+2),
    because even numbers > 2 are never prime.
    """
    if L <= 0:
        return 0

    # Sieve primes up to L (odd-only)
    odd_prime = sieve_odd_primes_upto(L)

    # pi(L) = 1 (for prime 2) + count of odd primes <= L
    pi_L = (1 if L >= 2 else 0) + odd_prime.count(1)
    d_L = L - pi_L  # d(n) = n - pi(n), and d(L) is the maximum denominator we need.

    # We need inverses up to max(d_L, pi_L+1)
    max_needed = max(d_L, pi_L + 1) + 2

    inv = array("I", [0]) * (max_needed + 1)
    inv[1] = 1
    mod = MOD
    inv_local = inv
    for i in range(2, max_needed + 1):
        inv_local[i] = mod - (mod // i) * inv_local[mod % i] % mod

    inv5 = pow(5, mod - 2, mod)

    # State at n=1
    C = 6  # C(1)
    b = 6  # sequences with exactly pi(1)=0 matches
    k = 0  # pi(1)
    d = 1  # d = n - k
    S = C % mod

    if L == 1:
        return S

    # Step to n=2 (prime)
    # extra term A_1(1) is 0 because n-1-k = 0
    C = 36  # all sequences allowed
    b = 6  # exactly 1 match at n=2: both throws equal
    k = 1  # pi(2)
    d = 1  # 2 - 1
    S = (S + C) % mod

    if L == 2:
        return S

    # Main loop: process from even n to n+1 (odd), then to n+2 (even).
    n = 2
    odd = odd_prime
    inv_arr = inv_local

    while n <= L - 2:
        # Step 1: n (even) -> m = n+1 (odd)
        m = n + 1

        if odd[m >> 1]:  # m is an odd prime
            # extra = A_n(k+1) = b/5 * (d-1)/(k+1)
            extra = (b * inv5) % mod
            extra = (extra * (d - 1)) % mod
            extra = (extra * inv_arr[k + 1]) % mod

            C1 = (6 * C + 5 * extra) % mod
            b1 = (b + 5 * extra) % mod
            k1 = k + 1
            d1 = d  # unchanged when moving to a prime (k increments too)
        else:
            # composite: k unchanged, d increases by 1
            C1 = (6 * C - b) % mod
            b1 = (b * 5) % mod
            b1 = (b1 * n) % mod
            b1 = (b1 * inv_arr[d]) % mod
            k1 = k
            d1 = d + 1

        S = (S + C1) % mod

        # Step 2: m (odd) -> m2 = m+1 (even, composite for m2>2)
        # Here k1 is unchanged, so always the "composite step" formula.
        C2 = (6 * C1 - b1) % mod
        b2 = (b1 * 5) % mod
        b2 = (b2 * m) % mod
        b2 = (b2 * inv_arr[d1]) % mod
        S = (S + C2) % mod

        # Advance state to n = m2 (even)
        C, b, k, d = C2, b2, k1, d1 + 1
        n = m + 1

    # If L is odd, there is one final step (n=L-1 -> L). For L=50,000,000 it's even.
    if n == L - 1:
        m = L
        if m == 2:
            pass
        elif (m & 1) == 0:
            # even composite
            C = (6 * C - b) % mod
            b = (b * 5) % mod
            b = (b * (L - 1)) % mod
            b = (b * inv_arr[d]) % mod
            S = (S + C) % mod
        else:
            # odd: prime or composite
            if odd[m >> 1]:
                extra = (b * inv5) % mod
                extra = (extra * (d - 1)) % mod
                extra = (extra * inv_arr[k + 1]) % mod
                C = (6 * C + 5 * extra) % mod
                b = (b + 5 * extra) % mod
                k += 1
            else:
                C = (6 * C - b) % mod
                b = (b * 5) % mod
                b = (b * (L - 1)) % mod
                b = (b * inv_arr[d]) % mod
                d += 1
            S = (S + C) % mod

    return S


def _run_asserts() -> None:
    # Test values from the problem statement
    assert C_exact_small(3) == 216
    assert C_exact_small(4) == 1290
    assert C_exact_small(11) == 361_912_500
    assert C_exact_small(24) == 4_727_547_363_281_250_000
    assert solve(50) == 832_833_871


if __name__ == "__main__":
    _run_asserts()
    print(solve())
