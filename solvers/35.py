from __future__ import annotations

from math import isqrt
from typing import List


def prime_sieve(n: int) -> bytearray:
    """Return is_prime[0..n-1] as a bytearray of 0/1."""
    if n <= 0:
        return bytearray()
    is_prime = bytearray(b"\x01") * n
    if n > 0:
        is_prime[0] = 0
    if n > 1:
        is_prime[1] = 0

    limit = isqrt(n - 1)
    for p in range(2, limit + 1):
        if is_prime[p]:
            start = p * p
            step = p
            count = ((n - 1 - start) // step) + 1
            is_prime[start:n:step] = b"\x00" * count
    return is_prime


def rotations_of(n: int) -> List[int]:
    s = str(n)
    k = len(s)
    if k == 1:
        return [n]
    pow10 = 10 ** (k - 1)
    rots = [n]
    x = n
    for _ in range(k - 1):
        x = (x % pow10) * 10 + (x // pow10)
        rots.append(x)
    return rots


def is_circular_prime(n: int, is_prime: bytearray) -> bool:
    return all(is_prime[r] for r in rotations_of(n))


def circular_prime_count(limit: int) -> int:
    """
    Count circular primes < limit.
    For correctness with arbitrary limit, sieve up to 10^d where d = digits(limit-1),
    since any rotation keeps the same digit count and is < 10^d.
    """
    if limit <= 2:
        return 0

    d = len(str(limit - 1))
    sieve_n = max(limit, 10**d)
    is_prime = prime_sieve(sieve_n)

    processed = bytearray(
        limit
    )  # only need to mark numbers we may iterate over (< limit)

    allowed_digits = (
        "1379"  # for multi-digit circular primes (2 and 5 are handled separately)
    )

    count = 0
    for p in range(2, limit):
        if not is_prime[p] or processed[p]:
            continue

        processed[p] = 1

        if p < 10:
            # single-digit primes: 2,3,5,7 are circular primes
            count += 1
            continue

        s = str(p)
        if any(ch not in allowed_digits for ch in s):
            continue

        rots = rotations_of(p)

        # Mark all in-cycle rotations that are < limit so we don't process them again
        for r in rots:
            if r < limit:
                processed[r] = 1

        if all(is_prime[r] for r in rots):
            uniq = set(rots)
            count += sum(1 for r in uniq if r < limit)

    return count


def main() -> None:
    # Given in statement: 13 circular primes below 100
    assert circular_prime_count(100) == 13

    # Example: 197 is a circular prime (197, 971, 719 are prime)
    assert is_circular_prime(197, prime_sieve(1000))

    ans = circular_prime_count(1_000_000)
    print(ans)


if __name__ == "__main__":
    main()
