from __future__ import annotations

from math import isqrt
from typing import List


def is_prime_with_list(n: int, primes: List[int]) -> bool:
    if n < 2:
        return False
    for p in primes:
        if p * p > n:
            break
        if n % p == 0:
            return False
    return True


def ensure_primes_up_to(n: int, primes: List[int]) -> None:
    """Ensure primes contains all primes up to at least n."""
    if primes[-1] >= n:
        return
    candidate = primes[-1] + 2
    while primes[-1] < n:
        if is_prime_with_list(candidate, primes):
            primes.append(candidate)
        candidate += 2


def can_be_written_as_prime_plus_twice_square(n: int, primes: List[int]) -> bool:
    """
    Check if n can be written as p + 2*s^2 for some prime p and integer s>=1.
    (s=0 would give n prime, but we only call this for odd composites anyway.)
    """
    ensure_primes_up_to(n, primes)
    for p in primes:
        if p >= n:
            break
        rem = n - p
        if rem % 2 != 0:
            continue
        t = rem // 2
        s = isqrt(t)
        if s * s == t:
            return True
    return False


def smallest_counterexample() -> int:
    primes: List[int] = [2, 3]
    n = 9
    while True:
        ensure_primes_up_to(n, primes)
        if not is_prime_with_list(n, primes):  # odd composite
            if not can_be_written_as_prime_plus_twice_square(n, primes):
                return n
        n += 2


def _self_test() -> None:
    primes: List[int] = [2, 3]
    # Examples given in the statement should all be representable.
    for x in [9, 15, 21, 25, 27, 33]:
        assert can_be_written_as_prime_plus_twice_square(x, primes), x


def main() -> None:
    _self_test()
    ans = smallest_counterexample()
    print(ans)


if __name__ == "__main__":
    main()
