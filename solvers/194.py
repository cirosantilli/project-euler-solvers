#!/usr/bin/env python3
import math

MOD = 10**8


def SA(c: int) -> int:
    return c**5 - 9 * c**4 + 34 * c**3 - 69 * c**2 + 77 * c - 38


def SB(c: int) -> int:
    return c**5 - 8 * c**4 + 27 * c**3 - 50 * c**2 + 52 * c - 24


def N(a: int, b: int, c: int, mod=None) -> int:
    n = a + b
    comb = math.comb(n, a)
    val = comb * c * (c - 1) * (SA(c) ** a) * (SB(c) ** b)
    return val if mod is None else val % mod


def solve():
    return N(25, 75, 1984, MOD)


if __name__ == "__main__":
    assert N(1, 0, 3) == 24
    assert N(0, 2, 4) == 92928
    assert N(2, 2, 3) == 20736
    print(f"{solve():08d}")
