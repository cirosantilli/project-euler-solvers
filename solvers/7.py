from __future__ import annotations

import math
from typing import Optional


def nth_prime(n: int) -> int:
    assert n >= 1
    if n == 1:
        return 2

    # Upper bound for nth prime (n >= 6): n (ln n + ln ln n)
    # We'll use it as a starting limit and grow if needed.
    if n < 6:
        limit = 15
    else:
        limit = int(n * (math.log(n) + math.log(math.log(n)))) + 10

    while True:
        # Sieve odds only: index i represents number (2*i + 1)
        size = (limit // 2) + 1
        is_prime = bytearray(b"\x01") * size
        is_prime[0] = 0  # 1 is not prime

        root = int(math.isqrt(limit))
        # i corresponds to p = 2*i + 1
        max_i = root // 2
        for i in range(1, max_i + 1):
            if is_prime[i]:
                p = 2 * i + 1
                start = (p * p) // 2
                step = p
                count = ((size - 1 - start) // step) + 1
                is_prime[start::step] = b"\x00" * count

        # Count primes and stop at the nth
        count_primes = 1  # prime = 2
        for i in range(1, size):
            if is_prime[i]:
                count_primes += 1
                if count_primes == n:
                    return 2 * i + 1

        # Not enough primes; increase limit and retry
        limit *= 2


def main() -> None:
    # Tests from statement / basic sanity checks
    assert nth_prime(1) == 2
    assert nth_prime(6) == 13

    ans = nth_prime(10001)

    print(ans)


if __name__ == "__main__":
    main()
