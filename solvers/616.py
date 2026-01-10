#!/usr/bin/env python3
"""
Project Euler 616 - Creative numbers

Key result used:
Creative numbers <= 1e12 are all perfect powers <= 1e12 except:
  (1) numbers of the form p^q with p prime and q prime
  (2) the number 16

So answer = sum(perfect_powers) - sum(prime^prime) - 16
"""

LIMIT = 10**12


def isqrt(n: int) -> int:
    """Integer square root without math.isqrt (no external libs)."""
    x = int(n**0.5)
    while (x + 1) * (x + 1) <= n:
        x += 1
    while x * x > n:
        x -= 1
    return x


def sieve(n: int):
    """Simple sieve of Eratosthenes returning list of primes <= n."""
    if n < 2:
        return []
    bs = bytearray(b"\x01") * (n + 1)
    bs[0:2] = b"\x00\x00"
    p = 2
    while p * p <= n:
        if bs[p]:
            step = p
            start = p * p
            bs[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
        p += 1
    return [i for i in range(n + 1) if bs[i]]


def all_perfect_powers_sum(limit: int) -> int:
    """
    Sum of all perfect powers <= limit, counted once.
    Perfect powers are n = a^b with a>=2, b>=2.
    """
    seen = set()
    # Max exponent: 2^40 > 1e12, so exponent up to 40 is enough.
    for exp in range(2, 41):
        # crude exp-root:
        base = int(limit ** (1.0 / exp))
        while (base + 1) ** exp <= limit:
            base += 1
        while base**exp > limit:
            base -= 1

        for a in range(2, base + 1):
            seen.add(a**exp)

    return sum(seen)


def prime_power_prime_power_sum(limit: int) -> int:
    """
    Sum of all numbers <= limit of the form p^q where p and q are prime.
    Counted once.
    """
    seen = set()
    primes_base = sieve(isqrt(limit))  # bases only need up to 1e6
    prime_exps = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]

    for q in prime_exps:
        maxb = int(limit ** (1.0 / q))
        while (maxb + 1) ** q <= limit:
            maxb += 1
        while maxb**q > limit:
            maxb -= 1

        for p in primes_base:
            if p > maxb:
                break
            seen.add(p**q)

    return sum(seen)


def solve():
    total_pp = all_perfect_powers_sum(LIMIT)
    total_primeprime = prime_power_prime_power_sum(LIMIT)
    return total_pp - total_primeprime - 16


if __name__ == "__main__":
    print(solve())
