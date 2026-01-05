from __future__ import annotations

import math
from typing import Dict


def factorize(n: int) -> Dict[int, int]:
    """Return prime factorization of n as {prime: exponent}."""
    factors: Dict[int, int] = {}
    if n <= 1:
        return factors

    # Factor 2
    while (n & 1) == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2

    # Factor 3
    while n % 3 == 0:
        factors[3] = factors.get(3, 0) + 1
        n //= 3

    # Factor remaining using 6k ± 1
    f = 5
    step = 2
    while f * f <= n:
        while n % f == 0:
            factors[f] = factors.get(f, 0) + 1
            n //= f
        f += step
        step = 6 - step  # alternates +2, +4

    if n > 1:
        factors[n] = factors.get(n, 0) + 1

    return factors


def euler_phi(n: int, factors: Dict[int, int]) -> int:
    """Compute Euler's totient using prime factors."""
    result = n
    for p in factors:
        result = result // p * (p - 1)
    return result


def count_ways(N: int) -> int:
    """
    Number of ways a laser can enter at vertex C, bounce off N surfaces,
    and exit through vertex C again.
    """
    if N % 2 == 0:
        return 0

    M = (N + 3) // 2
    if M % 3 == 0:
        return 0

    fac = factorize(M)
    phi_M = euler_phi(M, fac)

    has_prime_1_mod_3 = any((p % 3) == 1 for p in fac)
    if not has_prime_1_mod_3:
        G = 1 if (M % 3) == 1 else -1  # since M%3 is 1 or 2 here
        omega = len(fac)  # number of distinct prime factors
        g = G * (1 << omega)  # G * 2^omega
        phi_M -= g

    return phi_M // 3


def main() -> None:
    # Tests from the problem statement
    assert count_ways(11) == 2
    assert count_ways(1_000_001) == 80_840

    print(count_ways(12_017_639_147))


if __name__ == "__main__":
    main()
