from __future__ import annotations

from typing import List


def primes_up_to_needed() -> List[int]:
    # For limit 1e6 we only need small primes (product grows fast),
    # but generate a modest list safely.
    primes: List[int] = []
    candidate = 2
    while len(primes) < 1000:  # far more than needed
        is_p = True
        for p in primes:
            if p * p > candidate:
                break
            if candidate % p == 0:
                is_p = False
                break
        if is_p:
            primes.append(candidate)
        candidate += 1 if candidate == 2 else 2  # after 2, only odd
    return primes


def totient_max_n(limit: int) -> int:
    """
    Returns n <= limit maximizing n/phi(n).
    The maximum is achieved by multiplying consecutive smallest primes
    until the product would exceed limit.
    """
    n = 1
    for p in primes_up_to_needed():
        if n * p > limit:
            break
        n *= p
    return n


def main() -> None:
    # Given example: for n <= 10, maximum n/phi(n) occurs at n = 6
    assert totient_max_n(10) == 6

    limit = 1_000_000
    ans = totient_max_n(limit)
    print(ans)


if __name__ == "__main__":
    main()
