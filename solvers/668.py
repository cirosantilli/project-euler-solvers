#!/usr/bin/env python3
"""
Project Euler 668: Square root smooth numbers

A positive integer is called square root smooth if all of its prime factors are
strictly less than its square root.

Including the number 1, there are 29 square root smooth numbers not exceeding 100.

How many square root smooth numbers are there not exceeding 10,000,000,000?

This solution uses only the Python standard library.
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple


def sieve_primes_upto(n: int) -> List[int]:
    """Return list of all primes <= n."""
    if n < 2:
        return []
    is_prime = bytearray(b"\x01") * (n + 1)
    is_prime[:2] = b"\x00\x00"
    r = int(n**0.5)
    for p in range(2, r + 1):
        if is_prime[p]:
            step = p
            start = p * p
            is_prime[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i in range(2, n + 1) if is_prime[i]]


def build_pi_table(n: int) -> Tuple[int, int, Dict[int, int], List[int], List[int]]:
    """
    Build a prime-counting table for π(x) on the specific set of values needed here.

    Returns (root, small_max, pos, vals, pi_vals).

    Query π(x):
      - if x <= 1: π(x) = 0
      - elif x <= small_max: π(x) = pi_vals[offset + (small_max - x)]
      - else: π(x) = pi_vals[pos[x]]
    """
    root = math.isqrt(n)
    primes = sieve_primes_upto(root)

    # Distinct values of floor(n / i) for i=1..root (descending).
    large: List[int] = []
    last = -1
    for i in range(1, root + 1):
        v = n // i
        if v != last:
            large.append(v)
            last = v

    # Include all small integers down to 1, without duplicating `root` if it already appears in `large`.
    small_max = root if large[-1] != root else root - 1
    vals = large + list(range(small_max, 0, -1))
    offset = len(large)

    pos: Dict[int, int] = {v: i for i, v in enumerate(large)}
    pi_vals = [v - 1 for v in vals]

    end = len(vals)
    for p in primes:
        p2 = p * p
        if p2 > vals[0]:
            break
        while end and vals[end - 1] < p2:
            end -= 1

        # π(p-1) is in the small tail.
        pi_p_minus_1 = pi_vals[offset + (small_max - (p - 1))]

        for j in range(end):
            v = vals[j]
            x = v // p
            if x <= small_max:
                pi_vals[j] -= pi_vals[offset + (small_max - x)] - pi_p_minus_1
            else:
                pi_vals[j] -= pi_vals[pos[x]] - pi_p_minus_1

    return root, small_max, pos, vals, pi_vals


def count_square_root_smooth(N: int) -> int:
    """
    Count square root smooth numbers <= N.

    Non-smooth numbers correspond bijectively to pairs (p, m) with p prime and
    1 <= m <= min(p, floor(N/p)). Thus:

      non_smooth(N) = sum_{p <= r} p  +  sum_{p > r} floor(N/p),  where r=floor(sqrt(N))
      smooth(N)     = N - non_smooth(N)
    """
    if N <= 0:
        return 0
    if N == 1:
        return 1

    r, small_max, pos, vals, pi_vals = build_pi_table(N)
    primes_up_to_r = sieve_primes_upto(r)
    sum_small_primes = sum(primes_up_to_r)

    # small tail is exactly [small_max, ..., 1] of length small_max
    offset = len(vals) - small_max

    def pi(x: int) -> int:
        if x <= 1:
            return 0
        if x <= small_max:
            return pi_vals[offset + (small_max - x)]
        return pi_vals[pos[x]]

    qmax = N // (r + 1)
    sum_large = 0
    for q in range(1, qmax + 1):
        hi = N // q
        lo = N // (q + 1)
        cnt = pi(hi) - pi(lo)
        sum_large += q * cnt

    non_smooth = sum_small_primes + sum_large
    return N - non_smooth


def main() -> None:
    # Test value given in the problem statement
    assert count_square_root_smooth(100) == 29
    print(count_square_root_smooth(10_000_000_000))


if __name__ == "__main__":
    main()
