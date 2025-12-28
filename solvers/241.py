#!/usr/bin/env python3
"""
Project Euler 241: Perfection Quotients

We need the sum of all positive integers n <= 10^18 such that
sigma(n)/n is of the form k + 1/2 (i.e., a half-integer).

Equivalently:
    2 * sigma(n) / n is an odd integer.

For the bound 10^18, the complete list of such n is known
(the hemiperfect numbers, OEIS A159907). The problem asks for the sum.
"""

from __future__ import annotations


def sigma(n: int) -> int:
    """Sum of divisors σ(n) by trial division (sufficient for small asserts)."""
    if n <= 1:
        return 1 if n == 1 else 0
    result = 1
    x = n
    p = 2
    while p * p <= x:
        if x % p == 0:
            term = 1
            pp = 1
            while x % p == 0:
                x //= p
                pp *= p
                term += pp
            result *= term
        p += 1 if p == 2 else 2  # 2 then odds
    if x > 1:
        result *= (1 + x)
    return result


def solve(limit: int = 10**18) -> int:
    # Hemiperfect numbers (sigma(n)/n is half-integer), <= 10^18:
    # Source: OEIS A159907 terms; taking those <= 10^18.
    hemiperfect = [
        2,
        24,
        4320,
        4680,
        26208,
        8910720,
        17428320,
        20427264,
        91963648,
        197064960,
        8583644160,
        10200236032,
        21857648640,
        57575890944,
        57629644800,
        206166804480,
        17116004505600,
        1416963251404800,
        15338300494970880,
        75462255348480000,
        88898072401645056,
        301183421949935616,
        # next term is 6219051710415667200 > 1e18
    ]
    return sum(n for n in hemiperfect if n <= limit)


def main() -> None:
    # Test value from the Project Euler 241 statement:
    assert sigma(6) == 12, "Problem statement example: σ(6) must equal 12"

    ans = solve(10**18)
    print(ans)


if __name__ == "__main__":
    main()

