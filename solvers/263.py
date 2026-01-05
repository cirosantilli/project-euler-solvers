#!/usr/bin/env python3
"""Project Euler 263: An Engineers' Dream Come True.

Compute and print the sum of the first four *engineers' paradises*.

Main ideas:
  * Generate primes in increasing order with an odd-only segmented sieve.
  * A triple sexy-pair corresponds to four consecutive primes with gaps 6.
  * Practical numbers are tested using the Stewart–Sierpiński theorem:
    n = \prod p_i^{a_i} (p_1 < p_2 < ...) is practical iff p_1 = 2 and
    p_i <= 1 + \sigma(\prod_{j<i} p_j^{a_j}) for all i>1.
"""

from __future__ import annotations

from math import isqrt
from typing import Dict, Generator, List, Tuple


def simple_sieve(limit: int) -> List[int]:
    """Return all primes <= limit using an odd-only sieve."""
    if limit < 2:
        return []
    if limit == 2:
        return [2]

    # index i represents odd number (2*i + 3)
    size = (limit - 1) // 2
    sieve = bytearray(b"\x01") * size
    max_i = (isqrt(limit) - 3) // 2

    for i in range(max_i + 1):
        if sieve[i]:
            p = 2 * i + 3
            start = (p * p - 3) // 2
            sieve[start::p] = b"\x00" * (((size - start - 1) // p) + 1)

    primes = [2]
    primes.extend(2 * i + 3 for i, v in enumerate(sieve) if v)
    return primes


class PrimeCache:
    """Caches primes up to some bound; can be expanded if needed."""

    def __init__(self, limit: int = 200_000):
        self.limit = 0
        self.primes: List[int] = []
        self.ensure(limit)

    def ensure(self, limit: int) -> None:
        if limit <= self.limit:
            return
        new_limit = max(limit, int(self.limit * 1.5) + 1, 10)
        self.limit = new_limit
        self.primes = simple_sieve(self.limit)


def segmented_primes(
    pc: PrimeCache, segment_span: int = 20_000_000
) -> Generator[int, None, None]:
    """Infinite prime generator using a segmented sieve.

    segment_span is the width of each segment in integers.
    """
    yield 2
    low = 3

    while True:
        high = low + segment_span
        pc.ensure(isqrt(high) + 1)

        if low % 2 == 0:
            low += 1
        size = (high - low) // 2  # odds only
        sieve = bytearray(b"\x01") * size

        for p in pc.primes[1:]:  # skip 2
            pp = p * p
            if pp >= high:
                break
            start = pp if pp > low else ((low + p - 1) // p) * p
            if start % 2 == 0:
                start += p
            idx = (start - low) // 2
            step = p
            sieve[idx::step] = b"\x00" * (((size - idx - 1) // step) + 1)

        for i, v in enumerate(sieve):
            if v:
                yield low + 2 * i

        low = high


def factorize(n: int, primes: List[int]) -> List[Tuple[int, int]]:
    """Return prime factorization of n as (prime, exponent) pairs."""
    x = n
    out: List[Tuple[int, int]] = []
    for p in primes:
        if p * p > x:
            break
        if x % p == 0:
            e = 1
            x //= p
            while x % p == 0:
                x //= p
                e += 1
            out.append((p, e))
    if x > 1:
        out.append((x, 1))
    return out


def is_practical(n: int, pc: PrimeCache, cache: Dict[int, bool]) -> bool:
    """Check if n is practical via the Stewart–Sierpiński characterization."""
    if n in cache:
        return cache[n]

    if n == 1:
        cache[n] = True
        return True
    if n < 1 or (n & 1):
        cache[n] = False
        return False

    pc.ensure(isqrt(n) + 1)
    fac = factorize(n, pc.primes)
    if not fac or fac[0][0] != 2:
        cache[n] = False
        return False

    # sigma of the prefix product
    a2 = fac[0][1]
    sigma_prefix = (1 << (a2 + 1)) - 1  # 1 + 2 + ... + 2^a

    for p, a in fac[1:]:
        if p > sigma_prefix + 1:
            cache[n] = False
            return False
        sigma_prefix *= (pow(p, a + 1) - 1) // (p - 1)

    cache[n] = True
    return True


def is_engineers_paradise(
    n: int, pc: PrimeCache, practical_cache: Dict[int, bool]
) -> bool:
    """Check the practical-number condition for an engineers' paradise."""
    # Fast necessary condition: in this problem's setting, n must be divisible by 4.
    if n & 3:
        return False
    for x in (n - 8, n - 4, n, n + 4, n + 8):
        if not is_practical(x, pc, practical_cache):
            return False
    return True


def find_first_paradises(k: int = 4) -> List[int]:
    """Find the first k engineers' paradises."""
    pc = PrimeCache(200_000)
    practical_cache: Dict[int, bool] = {}

    last: List[int] = []
    paradises: List[int] = []

    for p in segmented_primes(pc):
        last.append(p)
        if len(last) > 4:
            last.pop(0)
        if (
            len(last) == 4
            and (last[1] - last[0] == 6)
            and (last[2] - last[1] == 6)
            and (last[3] - last[2] == 6)
        ):
            n = last[1] + 3
            if is_engineers_paradise(n, pc, practical_cache):
                paradises.append(n)
                if len(paradises) == k:
                    break

    return paradises


def _self_test() -> None:
    """Asserts for explicit values mentioned in the problem statement."""
    pc = PrimeCache(200)
    practical_cache: Dict[int, bool] = {}

    # From the statement: 6 is practical.
    assert is_practical(6, pc, practical_cache)

    # From the statement: the first *consecutive* sexy prime pair is (23, 29).
    pc2 = PrimeCache(200)
    prev = None
    for p in segmented_primes(pc2, segment_span=500):
        if prev is not None and p - prev == 6:
            assert (prev, p) == (23, 29)
            break
        prev = p


def solve() -> int:
    paradises = find_first_paradises(4)
    return sum(paradises)


def main() -> None:
    print(solve())


if __name__ == "__main__":
    _self_test()
    main()
