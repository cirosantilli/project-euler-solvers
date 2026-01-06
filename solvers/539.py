#!/usr/bin/env python3
"""
Project Euler 539: Odd Elimination

We define P(n) as the last number remaining after repeatedly eliminating every other
number, alternating directions each pass (left-to-right, then right-to-left, ...),
starting from the list [1, 2, ..., n].

We need S(n) = sum_{k=1..n} P(k), and the problem asks for:
S(10^18) mod 987654321

No external libraries are used.
"""

from functools import lru_cache

MOD = 987654321


@lru_cache(maxsize=None)
def P(n: int) -> int:
    """Last remaining number for list 1..n (Elimination Game), exact integer."""
    if n == 1:
        return 1
    # After a left-to-right pass, remaining numbers are 2,4,6,...,2*(n//2)
    # Rescale by 2 and transform the next (right-to-left) elimination:
    # P(n) = 2 * (1 + n//2 - P(n//2))
    return 2 * (1 + n // 2 - P(n // 2))


@lru_cache(maxsize=None)
def S(n: int) -> int:
    """Return S(n) mod MOD, where S(n) = sum_{k=1..n} P(k). Supports n>=0."""
    if n <= 0:
        return 0
    if n == 1:
        return 1

    if n & 1:
        # n = 2q + 1
        q = n // 2
        # P(2m) = P(2m+1) for m>=1, and:
        # P(2m) = 2*(m+1 - P(m))
        # Using that, one can derive:
        # S(2q+1) = 1 + 2*q*(q+3) - 4*S(q)
        return (1 + (2 * q * (q + 3)) - 4 * S(q)) % MOD
    else:
        # n = 2q
        q = n // 2
        # S(2q) = 2*q^2 + 4*q - 1 - 4*S(q-1) - 2*P(q)
        return (2 * q * q + 4 * q - 1 - 4 * S(q - 1) - 2 * (P(q) % MOD)) % MOD


def solve() -> int:
    return S(10**18) % MOD


def _self_test() -> None:
    # Given test values from the problem statement
    assert P(1) == 1
    assert P(9) == 6
    assert P(1000) == 510
    assert S(1000) % MOD == 268271


if __name__ == "__main__":
    _self_test()
    print(solve())
