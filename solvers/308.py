#!/usr/bin/env python3
"""
Project Euler 308: An amazing prime-generating automaton (Conway's FRACTRAN PRIMEGAME)

We must count how many FRACTRAN iterations are required (starting from n=2)
until the program first produces 2^(p_10001), where p_10001 is the 10001st prime.

Key insight:
Conway's PRIMEGAME reaches special "macro states" of the form 2^n * 7^m,
and it advances n -> n+1 each macro-iteration while updating m based on the
largest proper divisor of (n+1). The expensive part is counting how many raw
FRACTRAN steps each macro-iteration costs. This can be computed with a formula
involving floor-division sums, giving an O(p * sqrt(p)) solution that is fast
for p ~= 1e5.
"""

from __future__ import annotations

import math


# ----------------------------
# Problem statement asserts
# ----------------------------

FRACTRAN_PROGRAM = [
    (17, 91),
    (78, 85),
    (19, 51),
    (23, 38),
    (29, 33),
    (77, 29),
    (95, 23),
    (77, 19),
    (1, 17),
    (11, 13),
    (13, 11),
    (15, 2),
    (1, 7),
    (55, 1),
]


def _fractran_step(n: int) -> int:
    for num, den in FRACTRAN_PROGRAM:
        if (n * num) % den == 0:
            return (n * num) // den
    raise RuntimeError("Program halted unexpectedly (should not happen here).")


def _self_tests_from_statement() -> None:
    # The statement shows: starting from 2, the sequence begins:
    # 15, 825, 725, 1925, 2275, 425, ...
    n = 2
    first_terms = []
    for _ in range(6):
        n = _fractran_step(n)
        first_terms.append(n)
    assert first_terms == [15, 825, 725, 1925, 2275, 425]

    # The statement also says the powers of 2 that appear are:
    # 2^2, 2^3, 2^5, ...
    # So the first three powers of 2 after the seed 2^1 are: 4, 8, 32.
    n = 2
    powers = []
    for _ in range(1000):  # plenty for the first few powers
        n = _fractran_step(n)
        if n != 2 and (n & (n - 1)) == 0:
            powers.append(n)
            if len(powers) == 3:
                break
    assert powers == [4, 8, 32]


_self_tests_from_statement()


# ----------------------------
# Math utilities
# ----------------------------


def sieve_smallest_prime_factor(limit: int) -> list[int]:
    """Return SPF array where spf[x] is smallest prime factor of x (spf[p]=p for prime p)."""
    spf = list(range(limit + 1))
    if limit >= 1:
        spf[1] = 1
    r = int(limit**0.5)
    for i in range(2, r + 1):
        if spf[i] == i:  # prime
            step = i
            start = i * i
            for j in range(start, limit + 1, step):
                if spf[j] == j:
                    spf[j] = i
    return spf


def nth_prime(n: int) -> int:
    """Return the nth prime using a simple sieve with a safe upper bound."""
    if n < 6:
        limit = 15
    else:
        limit = int(n * (math.log(n) + math.log(math.log(n)))) + 50

    while True:
        is_prime = bytearray(b"\x01") * (limit + 1)
        is_prime[0:2] = b"\x00\x00"
        r = int(limit**0.5)
        for p in range(2, r + 1):
            if is_prime[p]:
                step = p
                start = p * p
                is_prime[start : limit + 1 : step] = b"\x00" * (
                    ((limit - start) // step) + 1
                )
        primes = [i for i, v in enumerate(is_prime) if v]
        if len(primes) >= n:
            return primes[n - 1]
        limit *= 2


def sum_floor_division_range(n: int, lo: int, hi: int) -> int:
    """
    Compute sum_{d=lo..hi} floor(n/d) in O(sqrt(n)) by grouping equal quotients.
    Assumes 1 <= lo <= hi.
    """
    s = 0
    d = lo
    while d <= hi:
        q = n // d
        dmax = n // q
        if dmax > hi:
            dmax = hi
        s += q * (dmax - d + 1)
        d = dmax + 1
    return s


# ----------------------------
# Core solution
# ----------------------------


def steps_until_power_of_two_exponent(p: int) -> int:
    """
    Total FRACTRAN steps until the PRIMEGAME first reaches 2^p (p prime).
    Uses the known cost formula per macro-iteration N=2..p.
    """
    spf = sieve_smallest_prime_factor(p)

    def largest_proper_divisor(n: int) -> int:
        if n < 2:
            return 0
        return n // spf[n] if spf[n] != n else 1

    steps = 0
    prev_b = 0  # b_{N-1}

    for N in range(2, p + 1):
        bN = largest_proper_divisor(N)

        # Original PRIMEGAME differs from the common "variant" cost by + (b_{N-1}-1)
        extra = 0 if N == 2 else (prev_b - 1)

        # Variant cost for checking N:
        # (N-1) + (6N+2)(N-b) + 2 * sum_{d=b..N-1} floor(N/d)
        s = sum_floor_division_range(N, bN, N - 1)
        cost = (N - 1) + (6 * N + 2) * (N - bN) + 2 * s + extra

        steps += cost
        prev_b = bN

    return steps


def solve() -> int:
    p = nth_prime(10001)  # 10001st prime
    return steps_until_power_of_two_exponent(p)


if __name__ == "__main__":
    print(solve())
