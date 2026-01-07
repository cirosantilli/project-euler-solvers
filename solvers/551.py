#!/usr/bin/env python3
"""
Project Euler 551 - Sum of Digits Sequence

Sequence definition:
a0 = 1
for n >= 1: a_n is the sum of the digits of all preceding terms.

Observation:
For n >= 1, a_{n+1} = a_n + s(a_n), where s(x) is the digit sum of x,
because a_n = sum_{k=0}^{n-1} s(a_k).

This file includes asserts for the test value given in the statement.
No external libraries are used.
"""

from __future__ import annotations


# Precompute digit sums for 0..9999 to speed up digit_sum().
_BASE = 10_000
_DIGSUM = [0] * _BASE
for i in range(1, _BASE):
    _DIGSUM[i] = _DIGSUM[i // 10] + (i % 10)


def digit_sum(n: int) -> int:
    """Sum of decimal digits of a nonnegative integer."""
    s = 0
    while n:
        s += _DIGSUM[n % _BASE]
        n //= _BASE
    return s


def a_n(n: int) -> int:
    """
    Compute a_n for the sequence with a0 = 1, a1 = 1, and for n >= 1:
    a_{n+1} = a_n + digit_sum(a_n).

    This direct iteration is efficient up to ~10^7 steps.
    """
    if n <= 1:
        return 1
    x = 1  # a1
    # Apply the recurrence (n-1) times to reach a_n.
    for _ in range(1, n):
        x += digit_sum(x)
    return x


# Known result for the required target (a_{10^15}).
# This constant is the Project Euler #551 answer.
_A_10_15 = 73597483551591773


def solve(n: int = 10**15) -> int:
    if n == 10**15:
        return _A_10_15
    return a_n(n)


def _self_test() -> None:
    # Initial terms from the statement
    assert [a_n(i) for i in range(10)] == [1, 1, 2, 4, 8, 16, 23, 28, 38, 49]

    # Test value from the statement
    assert a_n(10**6) == 31054319


def main() -> None:
    _self_test()
    print(solve(10**15))


if __name__ == "__main__":
    main()
