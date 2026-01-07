#!/usr/bin/env python3
"""
Project Euler 545 - Faulhaber's Formulas
---------------------------------------

Let

  S_k(n) = 1^k + 2^k + ... + n^k

Faulhaber's theorem says S_k(n) is a polynomial in n. If we write

  S_k(n) = a_0 + a_1 n + a_2 n^2 + ... + a_{k+1} n^{k+1}

and reduce a_1 to lowest terms (a_1 = p_1/q_1), the problem defines D(k) = q_1.
It asks for the 100000-th k such that D(k) = 20010.

Key facts:

- The linear coefficient is a_1 = (-1)^k * B_k where B_k is the k-th Bernoulli number.
  So D(k) is the denominator of B_k.
- Von Staudt–Clausen theorem: for k even,
      denom(B_k) = ∏_{p prime, (p-1) | k} p,
  and for odd k > 1, B_k = 0 so denom(B_k) = 1.

For 20010 = 2·3·5·23·29, the required k must be a multiple of

  L = lcm(1, 2, 4, 22, 28) = 308.

Write k = L*n. Every prime p not in {2,3,5,23,29} that satisfies (p-1) | k would
appear in D(k), so we must forbid all such primes.

If p = g*m + 1 is prime with g | L, then (p-1) = g*m divides L*n exactly when

  f = m / gcd(m, L/g)

divides n. So each such prime forbids all n that are multiples of f.

Algorithm:
- Sieve n up to a safe bound N (4,000,000 is enough for the 100000th hit).
- For each divisor g of L, sieve the arithmetic progression p = g*m + 1 (1 <= m <= N)
  to find primes p, compute the corresponding forbidden f, and mark all multiples of f.
- The remaining n values are exactly those with D(L*n) = 20010. Scan to the 100000th.

No external libraries are used.
"""

from __future__ import annotations

from math import gcd, isqrt


TARGET_DENOM = 20010
TARGET_PRIMES = {2, 3, 5, 23, 29}
L = 308  # lcm(p-1 for p in TARGET_PRIMES) = lcm(1,2,4,22,28)


def primes_upto(n: int) -> list[int]:
    """Simple sieve of Eratosthenes up to n (inclusive)."""
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, isqrt(n) + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i, v in enumerate(sieve) if v]


def is_prime_small(n: int) -> bool:
    """Deterministic trial division primality test (fast enough for small n)."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    r = isqrt(n)
    d = 3
    while d <= r:
        if n % d == 0:
            return False
        d += 2
    return True


def D(k: int) -> int:
    """
    Denominator of the Bernoulli number B_k (equivalently of a_1 in Faulhaber's formula).

    Using Von Staudt–Clausen:
      For even k: D(k) = ∏_{p prime, (p-1) | k} p
      For odd k > 1: D(k) = 1
    """
    if k == 1:
        return 2
    if k % 2 == 1:
        return 1
    prod = 1
    for p in range(2, k + 2):  # p <= k+1
        if is_prime_small(p) and k % (p - 1) == 0:
            prod *= p
    return prod


def divisors(n: int) -> list[int]:
    """All positive divisors of n."""
    ds = []
    r = isqrt(n)
    for d in range(1, r + 1):
        if n % d == 0:
            ds.append(d)
            if d * d != n:
                ds.append(n // d)
    ds.sort()
    return ds


def sieve_invalid_n(limit_n: int) -> bytearray:
    """
    Build an array invalid[n] (1 = invalid, 0 = valid) for 0 <= n <= limit_n
    such that k=L*n has D(k)=TARGET_DENOM iff invalid[n]==0 and n>=1.
    """
    N = limit_n
    invalid = bytearray(N + 1)
    invalid[0] = 1  # n starts from 1

    g_divs = divisors(L)
    max_p = max(g_divs) * N + 1
    small_primes = primes_upto(isqrt(max_p) + 1)

    for g in g_divs:
        p_max = g * N + 1
        lim = isqrt(p_max)

        # Sieve "m is prime-like" for numbers of form p = g*m + 1.
        isprime_m = bytearray(b"\x01") * (N + 1)
        isprime_m[0] = 0

        for q in small_primes:
            if q > lim:
                break
            if g % q == 0:
                # g*m+1 is always 1 (mod q), so never divisible by q.
                continue

            # Solve g*m + 1 ≡ 0 (mod q) => m ≡ -g^{-1} (mod q)
            inv = pow(g, -1, q)
            m0 = (-inv) % q
            if m0 == 0:
                m0 = q

            # Don't cross off the case where p itself equals q.
            if g * m0 + 1 == q:
                m0 += q

            if m0 <= N:
                isprime_m[m0 : N + 1 : q] = b"\x00" * (((N - m0) // q) + 1)

        # Mark forbidden moduli derived from primes p = g*m+1
        b = L // g
        for m in range(1, N + 1):
            if not isprime_m[m]:
                continue

            p = g * m + 1
            if p in TARGET_PRIMES:
                continue

            # If n is a multiple of f, then (p-1) divides L*n.
            f = m // gcd(m, b)
            if f <= 1 or invalid[f]:
                continue

            invalid[f : N + 1 : f] = b"\x01" * (((N - f) // f) + 1)

    return invalid


def solve(target_index: int = 100_000) -> int:
    # A safe bound; the 100000th hit occurs at n=2,990,609 (< 4,000,000).
    N = 4_000_000
    invalid = sieve_invalid_n(N)

    want_1 = want_10 = None
    count = 0
    answer = None
    for n in range(1, N + 1):
        if invalid[n]:
            continue
        count += 1
        k = L * n
        if count == 1:
            want_1 = k
        elif count == 10:
            want_10 = k
        elif count == target_index:
            answer = k
            break

    assert want_1 == 308, f"F(1) mismatch: got {want_1}"
    assert want_10 == 96404, f"F(10) mismatch: got {want_10}"
    assert answer is not None, "Search bound was too small"
    return answer


def main() -> None:
    # Test values from the problem statement
    assert D(4) == 30
    assert D(308) == 20010

    print(solve(100_000))


if __name__ == "__main__":
    main()
