from __future__ import annotations

from typing import List
import math


def sieve_primes(n: int) -> List[int]:
    """Return list of primes <= n."""
    if n < 2:
        return []
    is_prime = bytearray(b"\x01") * (n + 1)
    is_prime[0:2] = b"\x00\x00"
    limit = int(math.isqrt(n))
    for p in range(2, limit + 1):
        if is_prime[p]:
            step = p
            start = p * p
            is_prime[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i in range(2, n + 1) if is_prime[i]]


def count_prime_power_triples(limit: int) -> int:
    """
    Count numbers < limit expressible as p^2 + q^3 + r^4 with p,q,r prime.
    """
    if limit <= 0:
        return 0

    # Need primes up to sqrt(limit) to cover all squares.
    primes = sieve_primes(int(math.isqrt(limit)) + 1)

    squares: List[int] = []
    cubes: List[int] = []
    fourths: List[int] = []

    for p in primes:
        p2 = p * p
        if p2 < limit:
            squares.append(p2)
        p3 = p2 * p
        if p3 < limit:
            cubes.append(p3)
        p4 = p2 * p2
        if p4 < limit:
            fourths.append(p4)

    squares.sort()
    cubes.sort()
    fourths.sort()

    representable = set()

    for f in fourths:
        for c in cubes:
            fc = f + c
            if fc >= limit:
                break
            for s in squares:
                total = fc + s
                if total >= limit:
                    break
                representable.add(total)

    return len(representable)


def main() -> None:
    # From the problem statement: exactly four numbers below 50 are representable.
    assert count_prime_power_triples(50) == 4

    ans = count_prime_power_triples(50_000_000)
    print(ans)


if __name__ == "__main__":
    main()
