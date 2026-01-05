#!/usr/bin/env python3
"""
Project Euler 437: Fibonacci primitive roots

A number g is a Fibonacci primitive root modulo a prime p iff:
  1) g is a primitive root mod p (order p-1), and
  2) g^2 ≡ g + 1 (mod p)

We must sum all primes p < 100,000,000 that admit at least one such g.

No external libraries are used.
"""

from __future__ import annotations

import math
import sys


# ---------------------------
# Basic number theory helpers
# ---------------------------


def is_prime_miller_rabin_32(n: int) -> bool:
    """Deterministic Miller-Rabin for n < 2^32 (we only need up to 1e8)."""
    if n < 2:
        return False
    small_primes = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return n == p

    # write n-1 = d * 2^s with d odd
    d = n - 1
    s = 0
    while (d & 1) == 0:
        d >>= 1
        s += 1

    # Deterministic bases for 32-bit range
    for a in (2, 3, 5, 7, 11):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def tonelli_shanks(n: int, p: int) -> int:
    """
    Return r such that r^2 ≡ n (mod p), where p is an odd prime and n is a quadratic residue mod p.
    (Tonelli–Shanks algorithm)

    For p % 4 == 3 a faster shortcut is used.
    """
    n %= p
    if n == 0:
        return 0
    if p == 2:
        return n
    if p % 4 == 3:
        return pow(n, (p + 1) // 4, p)

    # Factor p-1 = q * 2^s with q odd
    q = p - 1
    s = 0
    while (q & 1) == 0:
        q >>= 1
        s += 1

    # Find z a quadratic non-residue
    z = 2
    # pow(z, (p-1)//2, p) == p-1 means non-residue
    while pow(z, (p - 1) // 2, p) != p - 1:
        z += 1

    c = pow(z, q, p)
    r = pow(n, (q + 1) // 2, p)
    t = pow(n, q, p)
    m = s

    while t != 1:
        # Find least i (0 < i < m) with t^(2^i) == 1
        i = 1
        t2i = (t * t) % p
        while t2i != 1:
            t2i = (t2i * t2i) % p
            i += 1
        b = pow(c, 1 << (m - i - 1), p)
        rb = (r * b) % p
        bb = (b * b) % p
        t = (t * bb) % p
        c = bb
        r = rb
        m = i

    return r


def is_primitive_root(g: int, p: int, prime_factors_p_minus_1: list[int]) -> bool:
    """Check if g is a primitive root modulo prime p using prime factors of p-1."""
    pm1 = p - 1
    for q in prime_factors_p_minus_1:
        if pow(g, pm1 // q, p) == 1:
            return False
    return True


def is_fibonacci_primitive_root(
    g: int, p: int, prime_factors_p_minus_1: list[int]
) -> bool:
    """Full check: g^2 ≡ g+1 and g is a primitive root mod p."""
    return ((g * g - g - 1) % p == 0) and is_primitive_root(
        g, p, prime_factors_p_minus_1
    )


# ---------------------------
# Prime generation
# ---------------------------


def simple_sieve(limit: int) -> list[int]:
    """Return list of primes <= limit using an odd-only sieve (fast enough for limit ~ 1e5)."""
    if limit < 2:
        return []
    if limit == 2:
        return [2]
    size = (limit // 2) + 1  # indices represent odd numbers: 2*i+1
    sieve = bytearray(b"\x01") * size
    sieve[0] = 0  # 1 is not prime
    r = int(math.isqrt(limit))
    for odd in range(3, r + 1, 2):
        if sieve[odd // 2]:
            start = (odd * odd) // 2
            step = odd
            count = ((size - 1 - start) // step) + 1
            sieve[start::step] = b"\x00" * count
    primes = [2]
    primes.extend(2 * i + 1 for i in range(1, size) if sieve[i])
    return primes


def iter_primes_below(n: int, base_primes: list[int], segment_odd_count: int = 1 << 20):
    """
    Yield all primes < n using a segmented odd-only sieve.

    base_primes must include all primes up to sqrt(n).
    """
    if n <= 2:
        return
    yield 2
    # segments over odd numbers [low, high)
    span = (
        2 * segment_odd_count
    )  # covers this many integers, but we store only odds => segment_odd_count bytes
    low = 3
    while low < n:
        high = low + span
        if high > n:
            high = n
        seg_len = (high - low + 1) // 2  # number of odd values in [low, high)
        seg = bytearray(b"\x01") * seg_len

        for p in base_primes[1:]:  # skip 2
            pp = p * p
            if pp >= high:
                break
            # find first multiple of p in [low, high)
            start = pp if pp >= low else ((low + p - 1) // p) * p
            if (start & 1) == 0:
                start += p
            idx = (start - low) // 2
            step = p
            if idx < seg_len:
                count = ((seg_len - 1 - idx) // step) + 1
                seg[idx::step] = b"\x00" * count

        i = seg.find(1)
        while i != -1:
            yield low + 2 * i
            i = seg.find(1, i + 1)

        low = high if (high & 1) else (high + 1)


# ---------------------------
# Factoring p-1 (distinct prime factors)
# ---------------------------


def distinct_prime_factors(
    n: int, primes_up_to_1e4: list[int], idx_after_97: int
) -> list[int]:
    """
    Return distinct prime factors of n (n <= 1e8 here).
    Uses a small amount of trial division, plus Miller-Rabin to stop early if the remaining cofactor is prime.
    """
    factors: list[int] = []

    if (n & 1) == 0:
        factors.append(2)
        while (n & 1) == 0:
            n //= 2
    if n == 1:
        return factors

    # First, strip very small odd primes up to 97
    for p in primes_up_to_1e4[1:idx_after_97]:  # skip 2, stop before first prime > 97
        if p * p > n:
            break
        if n % p == 0:
            factors.append(p)
            while n % p == 0:
                n //= p
            if n == 1:
                return factors

    if n == 1:
        return factors

    # If what's left is prime, we're done (common when p-1 = 2*q with q prime)
    if n > 97 * 97 and is_prime_miller_rabin_32(n):
        factors.append(n)
        return factors

    # Continue trial division as needed
    for p in primes_up_to_1e4[idx_after_97:]:
        if p * p > n:
            break
        if n % p == 0:
            factors.append(p)
            while n % p == 0:
                n //= p
            if n == 1:
                return factors
            if n > p * p and is_prime_miller_rabin_32(n):
                factors.append(n)
                return factors

    if n > 1:
        factors.append(n)
    return factors


# ---------------------------
# Core problem logic
# ---------------------------


def has_fib_primitive_root(
    p: int, primes_up_to_1e4: list[int], idx_after_97: int
) -> bool:
    """
    True iff prime p has at least one Fibonacci primitive root.

    For p != 5:
      - Must have 5 as a quadratic residue (p ≡ ±1 mod 5)
      - Let s = sqrt(5) mod p; roots are (1±s)/2. Check if either is a primitive root.
    """
    if p == 5:
        return True
    # (5/p) = (p/5) since 5 ≡ 1 (mod 4). Quadratic residues mod 5 are 1 and 4.
    if p % 5 not in (1, 4):
        return False

    # sqrt(5) mod p
    if p % 4 == 3:
        s = pow(5, (p + 1) // 4, p)
    else:
        s = tonelli_shanks(5, p)

    inv2 = (p + 1) // 2  # modular inverse of 2 mod p for odd p
    g1 = ((1 + s) * inv2) % p
    g2 = ((1 - s) * inv2) % p

    # factor p-1 once; use for both candidates
    factors = distinct_prime_factors(p - 1, primes_up_to_1e4, idx_after_97)

    # Both candidates satisfy g^2 ≡ g+1; we only need primitiveness
    if is_primitive_root(g1, p, factors):
        return True
    if is_primitive_root(g2, p, factors):
        return True
    return False


def solve(limit_exclusive: int = 100_000_000) -> tuple[int, int]:
    """
    Return (sum_of_primes, count_of_primes) for primes p < limit_exclusive that have a Fibonacci primitive root.
    """
    if limit_exclusive <= 2:
        return (0, 0)

    # base primes up to sqrt(limit) for segmented sieve and for factoring
    base_limit = int(math.isqrt(limit_exclusive - 1)) + 1
    base_primes = simple_sieve(base_limit)

    # For factoring p-1 we only ever need primes up to 10,000 (since sqrt(1e8)=1e4)
    primes_1e4 = base_primes if base_limit >= 10_000 else simple_sieve(10_000)
    # precompute split point after 97 to speed up factorization loop bounds
    idx_after_97 = 0
    while idx_after_97 < len(primes_1e4) and primes_1e4[idx_after_97] <= 97:
        idx_after_97 += 1

    total = 0
    count = 0

    # include 5 if in range
    if 5 < limit_exclusive:
        total += 5
        count += 1

    for p in iter_primes_below(limit_exclusive, base_primes):
        if p == 2 or p == 5:
            continue
        if p % 5 not in (1, 4):
            continue
        if has_fib_primitive_root(p, primes_1e4, idx_after_97):
            total += p
            count += 1

    return total, count


# ---------------------------
# Self-tests (from the problem statement)
# ---------------------------


def _self_test() -> None:
    # 8 is shown to be a Fibonacci primitive root of 11 in the statement.
    base_primes = simple_sieve(10_000)
    idx_after_97 = 0
    while idx_after_97 < len(base_primes) and base_primes[idx_after_97] <= 97:
        idx_after_97 += 1
    factors_10 = distinct_prime_factors(11 - 1, base_primes, idx_after_97)
    assert is_fibonacci_primitive_root(8, 11, factors_10)

    # "There are 323 primes less than 10000 ... sum is 1480491."
    s, c = solve(10_000)
    assert c == 323, c
    assert s == 1_480_491, s


def _parse_limit(argv: list[str]) -> int:
    """Return the first integer-looking CLI argument, or the default limit."""
    for a in argv[1:]:
        try:
            # allow things like "100000000" or "10_000"
            return int(a.replace("_", ""))
        except Exception:
            continue
    return 100_000_000


def main() -> None:
    _self_test()
    limit = _parse_limit(sys.argv)
    ans, _ = solve(limit)
    print(ans)


if __name__ == "__main__":
    main()
