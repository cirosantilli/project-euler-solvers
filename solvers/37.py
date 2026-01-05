from __future__ import annotations

from typing import List


def sieve(limit: int) -> bytearray:
    """
    Returns a bytearray is_prime where is_prime[n] is 1 if n is prime else 0,
    for 0 <= n <= limit.
    """
    if limit < 1:
        return bytearray(b"\x00") * (limit + 1)

    is_prime = bytearray(b"\x01") * (limit + 1)
    is_prime[0:2] = b"\x00\x00"
    # Even numbers > 2 are not prime
    for i in range(4, limit + 1, 2):
        is_prime[i] = 0

    p = 3
    while p * p <= limit:
        if is_prime[p]:
            step = 2 * p
            start = p * p
            for x in range(start, limit + 1, step):
                is_prime[x] = 0
        p += 2
    return is_prime


def is_truncatable_prime(n: int, is_prime: bytearray) -> bool:
    # Single-digit primes are explicitly excluded
    if n < 10:
        return False
    s = str(n)
    # Truncate from left and from right; all intermediates must be prime
    for i in range(1, len(s)):
        if not is_prime[int(s[i:])]:
            return False
        if not is_prime[int(s[: len(s) - i])]:
            return False
    return True


def solve() -> int:
    # Known to be < 1,000,000; 739397 is the largest truncatable prime.
    LIMIT = 1_000_000
    is_prime = sieve(LIMIT)

    # Basic sanity checks from the statement
    assert is_prime[3797] == 1
    assert is_truncatable_prime(3797, is_prime)
    assert not is_truncatable_prime(2, is_prime)
    assert not is_truncatable_prime(3, is_prime)
    assert not is_truncatable_prime(5, is_prime)
    assert not is_truncatable_prime(7, is_prime)

    truncatable: List[int] = []
    for n in range(11, LIMIT + 1, 2):  # only odd candidates >= 11
        if is_prime[n] and is_truncatable_prime(n, is_prime):
            truncatable.append(n)
            if len(truncatable) == 11:
                break

    assert (
        len(truncatable) == 11
    ), "Increase LIMIT; did not find all 11 truncatable primes."
    result = sum(truncatable)
    return result


def main() -> None:
    print(solve())


if __name__ == "__main__":
    main()
