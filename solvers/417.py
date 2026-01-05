#!/usr/bin/env python3
"""
Project Euler 417 - Reciprocal cycles II

We need:
    sum_{3 <= n <= 100000000} L(n)
where L(n) is the length of the recurring cycle in the decimal expansion of 1/n.
If n has no prime factors other than 2 and/or 5 then 1/n terminates and we define
L(n) = 0.

This program prints the required sum.

No external libraries are used.
"""

from __future__ import annotations

from array import array
from bisect import bisect_right
from math import gcd, isqrt

MAX_N = 100_000_000
TEST_N = 1_000_000
TEST_SUM = 55_535_191_115


def cycle_length_naive(n: int) -> int:
    """Return L(n) directly by simulating the long division remainder cycle.

    This is only used for the tiny examples in the problem statement.
    """
    m = n
    while m % 2 == 0:
        m //= 2
    while m % 5 == 0:
        m //= 5
    if m == 1:
        return 0

    # Multiplicative order of 10 modulo m.
    r = 10 % m
    k = 1
    while r != 1:
        r = (r * 10) % m
        k += 1
    return k


# --- Asserts for values explicitly stated / implied by the statement ---
# 1/6 = 0.1(6) has a 1-digit recurring cycle
assert cycle_length_naive(6) == 1
# 1/7 has a 6-digit recurring cycle
assert cycle_length_naive(7) == 6
# Denominators with only factors 2 and/or 5 have cycle length 0
assert cycle_length_naive(2) == 0
assert cycle_length_naive(4) == 0
assert cycle_length_naive(5) == 0
assert cycle_length_naive(8) == 0
assert cycle_length_naive(10) == 0


def gen_two_five_products(limit: int) -> list[int]:
    """Return sorted list of all numbers of the form 2^a * 5^b <= limit."""
    res = []
    p2 = 1
    while p2 <= limit:
        p5 = 1
        while p2 * p5 <= limit:
            res.append(p2 * p5)
            p5 *= 5
        p2 *= 2
    # size is small (~few hundred), so set() is fine
    return sorted(set(res))


def build_spf_odd(limit: int) -> array:
    """Build smallest-prime-factor table for odd numbers up to limit.

    spf[i] stores smallest prime factor of n = 2*i+1, or 0 if n is prime.
    (We never need even numbers because reduced denominators are coprime to 10.)
    """
    spf = array("I", [0]) * (limit // 2 + 1)
    root = isqrt(limit)
    for p in range(3, root + 1, 2):
        if spf[p // 2] == 0:  # prime
            step = p * 2
            start = p * p
            for x in range(start, limit + 1, step):
                idx = x // 2
                if spf[idx] == 0:
                    spf[idx] = p
    return spf


def multiplicative_order_prime(p: int, spf: array) -> int:
    """Compute ord_p(10) for prime p (p != 2,5)."""
    n = p - 1

    # collect distinct prime factors of (p-1)
    factors = [2]
    while (n & 1) == 0:
        n //= 2
    while n > 1:
        q = spf[n // 2]
        if q == 0:
            q = n
        factors.append(q)
        while n % q == 0:
            n //= q

    order = p - 1
    for q in factors:
        while order % q == 0 and pow(10, order // q, p) == 1:
            order //= q
    return order


def solve(max_n: int = MAX_N, test_n: int = TEST_N, test_sum: int = TEST_SUM) -> int:
    """Compute sum_{3<=n<=max_n} L(n), asserting test checksum along the way."""

    # Precompute products 2^a*5^b for both limits
    products_big = gen_two_five_products(max_n)
    products_test = gen_two_five_products(test_n)

    cache_big: dict[int, int] = {}
    cache_test: dict[int, int] = {}

    def g_big(x: int) -> int:
        v = cache_big.get(x)
        if v is None:
            v = bisect_right(products_big, x)
            cache_big[x] = v
        return v

    def g_test(x: int) -> int:
        v = cache_test.get(x)
        if v is None:
            v = bisect_right(products_test, x)
            cache_test[x] = v
        return v

    # Build SPF for odd numbers
    spf = build_spf_odd(max_n)

    # order[n//2] stores ord_n(10) for odd n not divisible by 5; unused entries stay 0
    order = array("I", [0]) * (max_n // 2 + 1)
    order[0] = 1  # for n=1

    # Cache for orders of prime powers p^e (only needed for small p)
    ppow_cache: dict[int, list[int]] = {}

    s_big = 0
    s_test_sum = 0

    for n in range(3, max_n + 1, 2):
        if n % 5 == 0:
            continue
        idx = n // 2
        p = spf[idx]

        if p == 0:
            # n is prime
            o = multiplicative_order_prime(n, spf)
        else:
            # n is composite; split n = p^e * rest with gcd(p,rest)=1
            m = n
            e = 0
            while m % p == 0:
                m //= p
                e += 1
            rest = m

            a = order[rest // 2] if rest > 1 else 1

            if e == 1:
                b = order[p // 2]
            else:
                lst = ppow_cache.get(p)
                if lst is None:
                    # compute max exponent such that p^k <= max_n
                    t = p
                    maxe = 0
                    while t <= max_n:
                        maxe += 1
                        t *= p

                    lst = [0] * (maxe + 1)
                    ord_p = order[p // 2]
                    lst[1] = ord_p
                    ordk = ord_p
                    mod = p
                    for k in range(2, maxe + 1):
                        mod *= p
                        if pow(10, ordk, mod) != 1:
                            ordk *= p
                        lst[k] = ordk
                    ppow_cache[p] = lst

                b = ppow_cache[p][e]

            o = a // gcd(a, b) * b

        order[idx] = o

        # Contribution to sum for max_n
        s_big += o * g_big(max_n // n)

        # Contribution to sum for test_n (only while n <= test_n)
        if n <= test_n:
            s_test_sum += o * g_test(test_n // n)

    # Verify the given checksum from the statement
    assert s_test_sum == test_sum, (s_test_sum, test_sum)

    return s_big


def main() -> None:
    print(solve())


if __name__ == "__main__":
    main()
