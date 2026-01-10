#!/usr/bin/env python3
"""
Project Euler 570

We are given closed forms for A(n), B(n) and a simplification:

    G(n) = gcd(A(n), B(n)) = 6 * gcd( 2*4^(n-2) - 3^(n-2), 7n+3 )

Further, for n not divisible by 3 we can cancel 3^(n-2) modulo (7n+3),
reducing to a single modular exponentiation.

This program computes:
    sum_{n=3}^{10^7} G(n)

No external libraries are used.
"""

from __future__ import annotations

import sys
import math


def A(n: int) -> int:
    """Closed form from the analysis (used only for problem-statement asserts)."""
    return 3 * pow(4, n - 1) - 2 * pow(3, n - 1)


def B(n: int) -> int:
    """Closed form from the analysis (used only for problem-statement asserts)."""
    p4 = pow(4, n - 2)
    p3 = pow(3, n - 1)
    return (-138 * p4) + (18 * n * p4) + (26 * p3) + (4 * n * p3)


def G(n: int) -> int:
    """
    Compute G(n) = 6 * gcd(2*4^(n-2) - 3^(n-2), 7n+3).

    Uses a faster path when n % 3 != 0:
      Let m = 7n+3. Then gcd(3, m)=1, so 3^(n-2) is invertible mod m and we can cancel it.
      Define b = 4 * inv3 (mod m). Then
          2*4^(n-2) - 3^(n-2) ≡ 3^(n-2) * (2*b^(n-2) - 1) (mod m)
      Hence gcd(2*4^(n-2) - 3^(n-2), m) = gcd(2*b^(n-2) - 1, m).
    """
    if n < 3:
        return 0
    m = 7 * n + 3

    if n % 3:
        # Compute inv3 modulo m in O(1) using m mod 3:
        # If m = 3k+1, inv3 = 2k+1 = (2m+1)/3
        # If m = 3k+2, inv3 = k+1  = (m+1)/3
        if m % 3 == 1:
            inv3 = (2 * m + 1) // 3
        else:  # m % 3 == 2
            inv3 = (m + 1) // 3

        b = (4 * inv3) % m
        t = pow(b, n - 2, m)
        x = (2 * t - 1) % m
        return 6 * math.gcd(x, m)

    # n divisible by 3: cannot cancel 3^(n-2) modulo m, so do it directly.
    x = (2 * pow(4, n - 2, m) - pow(3, n - 2, m)) % m
    return 6 * math.gcd(x, m)


def sum_G(N: int) -> int:
    """
    Compute S(N) = sum_{n=3..N} G(n) efficiently.

    We split by n mod 3 to avoid a branch inside the hot loop:
      - n ≡ 1 (mod 3): m ≡ 1 (mod 3) so inv3 = (2m+1)//3
      - n ≡ 2 (mod 3): m ≡ 2 (mod 3) so inv3 = (m+1)//3
      - n ≡ 0 (mod 3): use the direct two-exponent path
    """
    if N < 3:
        return 0

    gcd = math.gcd
    total_d = 0  # accumulate d(n) = gcd(...), then multiply by 6 at the end

    # n ≡ 1 (mod 3): n = 4, 7, 10, ...
    for n in range(4, N + 1, 3):
        m = 7 * n + 3
        inv3 = (2 * m + 1) // 3  # since m % 3 == 1
        b = (4 * inv3) % m
        t = pow(b, n - 2, m)
        total_d += gcd((2 * t - 1) % m, m)

    # n ≡ 2 (mod 3): n = 5, 8, 11, ...
    for n in range(5, N + 1, 3):
        m = 7 * n + 3
        inv3 = (m + 1) // 3  # since m % 3 == 2
        b = (4 * inv3) % m
        t = pow(b, n - 2, m)
        total_d += gcd((2 * t - 1) % m, m)

    # n ≡ 0 (mod 3): n = 3, 6, 9, ...
    for n in range(3, N + 1, 3):
        m = 7 * n + 3
        x = (2 * pow(4, n - 2, m) - pow(3, n - 2, m)) % m
        total_d += gcd(x, m)

    return 6 * total_d


def _self_test() -> None:
    # Problem statement checks
    assert A(3) == 30
    assert B(3) == 6
    assert math.gcd(A(3), B(3)) == 6
    assert G(3) == 6

    assert A(11) == 3027630
    assert B(11) == 19862070
    assert math.gcd(A(11), B(11)) == 30
    assert G(11) == 30

    assert G(500) == 186
    assert sum_G(500) == 5124


def main(argv: list[str]) -> None:
    _self_test()

    N = 10_000_000
    if len(argv) >= 2:
        N = int(argv[1])

    print(sum_G(N))


if __name__ == "__main__":
    main(sys.argv)
