#!/usr/bin/env python3
"""
Project Euler 533 - Minimum Values of the Carmichael Function

We need L(n): the smallest m such that for all k >= m, λ(k) >= n.

Let X = n-1. Then L(n) = 1 + max{k : λ(k) <= X}.

Key reduction:
For any m, define N(m) as the largest integer t such that λ(t) divides m.
Then λ(t) <= m, so for X fixed:
    max{k : λ(k) <= X} = max_{1 <= m <= X} N(m)

For a fixed m, the maximizer is independent across primes:
- For odd prime p:
      λ(p^e) = (p-1)*p^(e-1)
  So p^e can be included iff (p-1)*p^(e-1) | m.
  That yields exponent e = 1 + v_p(m/(p-1)) when (p-1)|m, else 0.
- For p=2:
      λ(2)=1, λ(4)=2, λ(2^e)=2^(e-2) for e>=3
  The maximum exponent is:
      e2 = 1                     if m is odd
      e2 = v2(m) + 2             if m is even

Thus N(m) is fully determined by divisibility conditions.

We search the best m <= X by maximizing log(N(m)).
We can compute log(N(m)) for all m <= X with a sieve-like process:
For each prime p>=3 and each level step = (p-1)*p^t, add log(p) to all multiples of step.
Similarly for 2 we add the appropriate log(2) contributions to all even / power-of-two multiples.

Finally, once best m is found, compute N(m) (only modulo 1e9) by enumerating all divisors d|m
and checking whether d+1 is prime; if so, p=d+1 contributes p^(1+v_p(m/d)).

This implementation uses only the Python standard library.
"""

from __future__ import annotations

from array import array
import math


MOD = 10**9
TARGET_N = 20_000_000  # find L(TARGET_N) and output its last 9 digits


def sieve_odd_primes(n: int) -> bytearray:
    """
    Odd-only sieve up to n (inclusive).

    Returns a bytearray is_prime_odd such that:
      - odd number x is prime iff x == 2 or (x is odd and is_prime_odd[x//2] != 0)
      - index i corresponds to odd number (2*i + 1)
    """
    if n < 2:
        return bytearray(b"\x00") * (n // 2 + 1)
    size = n // 2 + 1  # odds up to n
    is_p = bytearray(b"\x01") * size
    is_p[0] = 0  # 1 is not prime

    r = int(n**0.5)
    for p in range(3, r + 1, 2):
        if is_p[p // 2]:
            start = (p * p) // 2
            step = p
            # Mark indices start, start+step, start+2*step, ... as composite
            is_p[start::step] = b"\x00" * (((size - start - 1) // step) + 1)
    return is_p


def is_prime(x: int, is_prime_odd: bytearray) -> bool:
    if x == 2:
        return True
    if x < 2 or (x & 1) == 0:
        return False
    return bool(is_prime_odd[x // 2])


def factorize_small(n: int) -> list[tuple[int, int]]:
    """Trial division factorization for n <= ~2e7 (fast enough for one n)."""
    out: list[tuple[int, int]] = []
    if n % 2 == 0:
        e = 0
        while n % 2 == 0:
            n //= 2
            e += 1
        out.append((2, e))
    p = 3
    while p * p <= n:
        if n % p == 0:
            e = 0
            while n % p == 0:
                n //= p
                e += 1
            out.append((p, e))
        p += 2
    if n > 1:
        out.append((n, 1))
    return out


def all_divisors(factors: list[tuple[int, int]]) -> list[int]:
    """Generate all divisors from prime-power factorization."""
    divs = [1]
    for p, e in factors:
        base = list(divs)
        pe = 1
        for _ in range(e):
            pe *= p
            for d in base:
                divs.append(d * pe)
    return divs


def best_m_under(limit: int) -> tuple[int, bytearray]:
    """
    Find m in [1..limit] maximizing N(m) (equivalently maximizing log(N(m))).

    Returns (best_m, is_prime_odd) where is_prime_odd covers up to limit+1.
    """
    if limit <= 1:
        # For limit 0 or 1, the best m is 1 (N(1)=2).
        return 1, sieve_odd_primes(limit + 1)

    nmax = limit + 1
    is_p = sieve_odd_primes(nmax)

    # Score array stores log(N(m)) up to an additive constant (the always-present factor 2^1).
    score = array("d", [0.0]) * (limit + 1)
    sc = score  # local alias for speed

    log = math.log
    ln2 = log(2.0)

    # Contribution of prime 2 (up to a constant):
    # exponent e2(m) = 1 (odd) or v2(m)+2 (even).
    # We can ignore the +1 constant across all m and add the rest via:
    # - +ln2 for all even m (the "+1 if even" term)
    # - +ln2 for each power-of-two divisor 2^k of m (k>=1), which sums to v2(m)*ln2
    for i in range(2, limit + 1, 2):
        sc[i] += ln2
    pow2 = 2
    while pow2 <= limit:
        for i in range(pow2, limit + 1, pow2):
            sc[i] += ln2
        pow2 <<= 1

    # For each odd prime p and each level step=(p-1)*p^t, add ln(p) to all multiples of step.
    for idx in range(1, len(is_p)):
        if is_p[idx]:
            p = (idx << 1) + 1
            lnp = log(p)
            step = p - 1
            while step <= limit:
                for m in range(step, limit + 1, step):
                    sc[m] += lnp
                step *= p

    best_m = 1
    best_s = sc[1]
    for m in range(2, limit + 1):
        s = sc[m]
        if s > best_s:
            best_s = s
            best_m = m

    # Free the big score array as early as possible.
    del score
    return best_m, is_p


def N_mod(m: int, is_p: bytearray, mod: int = MOD) -> int:
    """Compute N(m) modulo mod."""
    factors = factorize_small(m)
    divs = all_divisors(factors)

    # 2-adic exponent
    if m & 1:
        e2 = 1
    else:
        v2 = (m & -m).bit_length() - 1
        e2 = v2 + 2
    res = pow(2, e2, mod)

    for d in divs:
        p = d + 1
        if p == 2 or (p & 1) == 0:
            continue
        if is_prime(p, is_p):
            t = m // d
            e = 1
            while t % p == 0:
                t //= p
                e += 1
            res = (res * pow(p, e, mod)) % mod
    return res


def N_big(m: int, is_p: bytearray) -> int:
    """Compute N(m) exactly (Python big int). Used for small test asserts."""
    factors = factorize_small(m)
    divs = all_divisors(factors)

    if m & 1:
        e2 = 1
    else:
        v2 = (m & -m).bit_length() - 1
        e2 = v2 + 2
    res = 2**e2

    for d in divs:
        p = d + 1
        if p == 2 or (p & 1) == 0:
            continue
        if is_prime(p, is_p):
            t = m // d
            e = 1
            while t % p == 0:
                t //= p
                e += 1
            res *= p**e
    return res


def solve_exact(n: int) -> int:
    """Return L(n) exactly (works fine for the provided small test cases)."""
    if n <= 1:
        return 1
    limit = n - 1
    best_m, is_p = best_m_under(limit)
    M = N_big(best_m, is_p)
    return M + 1


def solve_last9(n: int) -> int:
    """Return the last 9 digits of L(n)."""
    if n <= 1:
        return 1
    limit = n - 1
    best_m, is_p = best_m_under(limit)
    M_mod = N_mod(best_m, is_p, MOD)
    return (M_mod + 1) % MOD


def main() -> None:
    # Asserts from the problem statement examples.
    assert solve_exact(6) == 241
    assert solve_exact(100) == 20_174_525_281

    ans = solve_last9(TARGET_N)
    print(f"{ans:09d}")


if __name__ == "__main__":
    main()
