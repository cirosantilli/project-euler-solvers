#!/usr/bin/env python3
"""
Project Euler 615
The millionth number with at least one million prime factors (with multiplicity).

We need the 1,000,000-th smallest n such that Ω(n) >= 1,000,000, where Ω counts prime
factors with multiplicity. Output n mod 123454321.

Key reduction:
For the first million such numbers, almost all prime factors are 2. If we can find an
integer k such that the millionth number is divisible by 2^(m-k) (m=1,000,000),
then writing n = 2^(m-k) * x reduces the problem to:

    find the millionth number x with Ω(x) >= k,
    then answer = x * 2^(m-k) (mod MOD).

A sufficient (and for this problem minimal) choice is k=28. We verify the reduction
with a cheap inequality at runtime.

No external libraries are used.
"""

from __future__ import annotations

import heapq


MOD = 123454321
TARGET_INDEX = 1_000_000
TARGET_OMEGA = 1_000_000


class PrimeTable:
    """
    On-demand prime generator by incremental trial division.
    We only need the first ~16k primes (up to ~173k) for this problem.
    """

    __slots__ = ("primes",)

    def __init__(self) -> None:
        self.primes: list[int] = [2]

    def _is_prime(self, n: int) -> bool:
        # n is odd and >= 3
        r = int(n**0.5)
        ps = self.primes
        # skip ps[0] = 2
        for i in range(1, len(ps)):
            p = ps[i]
            if p > r:
                break
            if n % p == 0:
                return False
        return True

    def get(self, idx: int) -> int:
        ps = self.primes
        if idx < len(ps):
            return ps[idx]

        # extend until idx is available
        x = ps[-1] + 1
        if x % 2 == 0:
            x += 1
        while len(ps) <= idx:
            if self._is_prime(x):
                ps.append(x)
            x += 2
        return ps[idx]


def nth_number_with_at_least_k_prime_factors(nth: int, k: int) -> int:
    """
    Returns the `nth` smallest positive integer n such that Ω(n) >= k.

    Best-first search from 2^k. From a number v with largest prime factor p_max we can:
      - append a prime >= p_max: v * p
      - replace one factor 2 by a prime >= p_max and >2: (v/2) * p   (only if v is even)

    To avoid iterating over all primes on every expansion, we generate each
    "multiply by primes in increasing order" list lazily (multi-way merge):

    Heap node: (value, max_idx, base, idx)
      - idx == -1 means "no sibling stream" (seed only)
      - otherwise value = base * prime[idx] and the node has a sibling with idx+1

    This enumerates candidates in increasing numeric order.
    """
    if nth <= 0 or k <= 0:
        raise ValueError("nth and k must be positive integers")

    primes = PrimeTable()
    seed = 1 << k  # 2^k

    heappush = heapq.heappush
    heappop = heapq.heappop

    # (value, max_prime_index, base, prime_index_in_stream)
    pq: list[tuple[int, int, int, int]] = [(seed, 0, 0, -1)]

    produced = 0
    prev_val = -1

    while True:
        val, max_idx, base, idx = heappop(pq)

        is_dup = val == prev_val
        if not is_dup:
            prev_val = val
            produced += 1
            if produced == nth:
                return val

        # continue sibling stream even for duplicates (otherwise we'd miss later siblings)
        if idx >= 0:
            nxt = idx + 1
            p = primes.get(nxt)
            heappush(pq, (base * p, nxt, base, nxt))

        if is_dup:
            continue  # don't expand duplicates

        # append stream from this value (start with prime[max_idx])
        p = primes.get(max_idx)
        heappush(pq, (val * p, max_idx, val, max_idx))

        # replace one factor 2 by a prime (>2), only if val is even
        if (val & 1) == 0:
            start = max_idx if max_idx > 0 else 1  # exclude prime 2
            p = primes.get(start)
            half = val >> 1
            heappush(pq, (half * p, start, half, start))


def solve() -> None:
    # Test value from the problem statement:
    # "the fifth number with at least 5 prime factors is 80"
    assert nth_number_with_at_least_k_prime_factors(5, 5) == 80

    # Reduction parameter.
    # k=28 is the minimal value that makes the reduction valid for this problem.
    k = 28

    # Find x = the millionth number with Ω(x) >= k
    x = nth_number_with_at_least_k_prime_factors(TARGET_INDEX, k)

    # Verify that all first TARGET_INDEX values of the original problem are divisible by 2^(m-k).
    # Any number NOT divisible by 2^(m-k) has at most (m-k-1) factors of 2, hence needs at least (k+1)
    # odd prime factors; its smallest possible size (after dividing out 2^(m-k)) is 3^(k+1)/2.
    # If x is below that threshold then the first TARGET_INDEX numbers are exactly:
    #   2^(m-k) * (first TARGET_INDEX numbers with Ω >= k).
    while 2 * x >= 3 ** (k + 1):
        k += 1
        x = nth_number_with_at_least_k_prime_factors(TARGET_INDEX, k)

    ans = (x % MOD) * pow(2, TARGET_OMEGA - k, MOD) % MOD
    print(ans)


if __name__ == "__main__":
    solve()
