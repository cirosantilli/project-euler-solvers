from __future__ import annotations

from typing import Final


def largest_prime_factor(n: int) -> int:
    """Return the largest prime factor of n (n >= 2)."""
    largest = 1

    # Factor out 2s
    while n % 2 == 0:
        largest = 2
        n //= 2

    # Factor out odd primes
    f = 3
    while f * f <= n:
        while n % f == 0:
            largest = f
            n //= f
        f += 2

    # If n is now > 1, it's prime and larger than any factor found
    if n > 1:
        largest = n

    return largest


def main() -> None:
    # Test case from the prompt
    assert largest_prime_factor(13195) == 29

    target: Final[int] = 600851475143
    ans = largest_prime_factor(target)
    print(ans)


if __name__ == "__main__":
    main()
