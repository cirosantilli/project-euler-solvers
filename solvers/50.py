from __future__ import annotations

from math import isqrt
from typing import List, Tuple


def sieve_is_prime(limit: int) -> bytearray:
    """
    Returns is_prime array for [0..limit], where is_prime[x]=1 iff x is prime.
    """
    if limit < 1:
        return bytearray(b"\x00") * (limit + 1)
    is_prime = bytearray(b"\x01") * (limit + 1)
    is_prime[0] = 0
    if limit >= 1:
        is_prime[1] = 0

    for p in range(2, isqrt(limit) + 1):
        if is_prime[p]:
            start = p * p
            step = p
            for m in range(start, limit + 1, step):
                is_prime[m] = 0
    return is_prime


def longest_consecutive_prime_sum(limit: int) -> Tuple[int, int]:
    """
    Returns (best_prime_sum, number_of_terms) for primes < limit.
    """
    if limit <= 2:
        return (0, 0)

    is_prime = sieve_is_prime(limit - 1)
    primes: List[int] = [i for i in range(2, limit) if is_prime[i]]

    prefix: List[int] = [0]
    s = 0
    for p in primes:
        s += p
        prefix.append(s)

    # Maximum possible length starting from 2 (monotone increasing prefix sums)
    max_len = 0
    while max_len + 1 < len(prefix) and prefix[max_len + 1] < limit:
        max_len += 1

    # Try lengths from largest to smallest; first hit is optimal.
    n = len(primes)
    for length in range(max_len, 0, -1):
        for i in range(0, n - length + 1):
            val = prefix[i + length] - prefix[i]
            if val >= limit:
                break  # further i only increases the sum for fixed length
            if is_prime[val]:
                return (val, length)

    return (0, 0)


def main() -> None:
    # Problem statement checks
    assert longest_consecutive_prime_sum(100) == (41, 6)
    assert longest_consecutive_prime_sum(1000) == (953, 21)

    ans, _terms = longest_consecutive_prime_sum(1_000_000)
    print(ans)


if __name__ == "__main__":
    main()
