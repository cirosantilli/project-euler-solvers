from __future__ import annotations

import itertools
from typing import Iterable


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    if n % 3 == 0:
        return n == 3
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def perm_to_int(perm: Iterable[str]) -> int:
    x = 0
    for ch in perm:
        x = x * 10 + (ord(ch) - 48)
    return x


def largest_pandigital_prime() -> int:
    # Try n from 9 down to 1; skip n where digit sum is divisible by 3
    # because then every n-pandigital number is divisible by 3.
    for n in range(9, 0, -1):
        digit_sum = n * (n + 1) // 2
        if digit_sum % 3 == 0:
            continue

        digits = [str(d) for d in range(1, n + 1)]
        best = 0

        for perm in itertools.permutations(digits):
            last = perm[-1]
            # Quick composite filters:
            if last in ("2", "4", "5", "6", "8"):
                continue
            val = perm_to_int(perm)
            if val > best and is_prime(val):
                best = val

        if best != 0:
            return best

    return 0


def main() -> None:
    # Basic sanity checks for primality helper
    assert is_prime(2)
    assert is_prime(3)
    assert not is_prime(1)
    assert not is_prime(9)

    ans = largest_pandigital_prime()
    print(ans)


if __name__ == "__main__":
    main()
