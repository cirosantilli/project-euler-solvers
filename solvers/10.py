from __future__ import annotations

import math
from typing import Final


def sum_primes_below(limit: int) -> int:
    """
    Returns sum of all primes p with p < limit.
    Uses an odd-only sieve of Eratosthenes.
    """
    if limit <= 2:
        return 0
    if limit <= 3:
        return 2  # only prime below 3 is 2

    # Store only odd numbers >= 3:
    # index i represents number (2*i + 3)
    size = limit // 2 - 1  # count of odd numbers in [3, limit)
    sieve = bytearray(b"\x01") * size

    r = math.isqrt(limit - 1)
    max_i = (r - 3) // 2  # largest i such that (2*i+3) <= r

    for i in range(max_i + 1):
        if sieve[i]:
            p = 2 * i + 3
            start = (p * p - 3) // 2  # index of p*p
            if start < size:
                count = ((size - start - 1) // p) + 1
                sieve[start::p] = b"\x00" * count

    total = 2
    for i, is_prime in enumerate(sieve):
        if is_prime:
            total += 2 * i + 3
    return total


def main() -> None:
    # Test case from statement
    assert sum_primes_below(10) == 17

    LIMIT: Final[int] = 2_000_000
    print(sum_primes_below(LIMIT))


if __name__ == "__main__":
    main()
