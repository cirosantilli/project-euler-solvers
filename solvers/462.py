#!/usr/bin/env python3
"""
Project Euler 462: Permutation of 3-smooth Numbers

A 3-smooth number has no prime factor larger than 3, i.e. it is of the form 2^a * 3^b.
Let S(N) be the set of 3-smooth numbers <= N.
F(N) is the number of permutations of S(N) where every number appears after all of its proper divisors.

Key fact:
S(N) corresponds to exponent pairs (a,b) with 2^a * 3^b <= N, ordered by componentwise <=.
That poset is exactly the Young-diagram/Ferrers-diagram poset, so F(N) equals the number of
standard Young tableaux of that shape, given by the hook-length formula:
    F = n! / Π hook(cell)
where n is the number of cells (i.e. |S(N)|).

This program computes F(10^18) and prints it in scientific notation rounded to 10 decimals.
"""

from __future__ import annotations


def partition_3smooth(N: int) -> list[int]:
    """
    Build the Young diagram shape as a partition (row lengths), where each cell corresponds
    to a pair (a,b) with 2^a * 3^b <= N.

    For each b >= 0 with 3^b <= N, the allowed a are 0..floor(log2(N/3^b)).
    The row length therefore equals floor(log2(N/3^b)) + 1, which is bit_length(N//3^b).
    """
    if N < 1:
        return []
    rows: list[int] = []
    pow3 = 1
    while pow3 <= N:
        limit = N // pow3
        rows.append(limit.bit_length())  # = floor(log2(limit)) + 1
        pow3 *= 3

    # Should be a partition: non-increasing row lengths.
    for i in range(1, len(rows)):
        assert rows[i] <= rows[i - 1]
    return rows


def hook_product(part: list[int]) -> int:
    """
    Compute the product of hook lengths for all cells in a Ferrers diagram of shape `part`.
    `part[i]` is the length of row i (0-indexed) and is non-increasing.
    """
    if not part:
        return 1

    r = len(part)
    max_len = part[0]

    # Column heights: for each column j, count rows with length > j.
    col_heights: list[int] = []
    h = r
    for j in range(max_len):
        while h > 0 and part[h - 1] <= j:
            h -= 1
        col_heights.append(h)

    prod = 1
    for i, row_len in enumerate(part):
        for j in range(row_len):
            # hook = (cells to the right) + (cells below) + 1
            #      = (row_len - j - 1) + (col_heights[j] - i - 1) + 1
            hook = row_len - j + col_heights[j] - i - 1
            prod *= hook
    return prod


def factorial(n: int) -> int:
    """Simple big-integer factorial (n is small here: ~1100 for N=10^18)."""
    res = 1
    for k in range(2, n + 1):
        res *= k
    return res


def F(N: int) -> int:
    """Compute F(N) exactly as an integer using the hook-length formula."""
    part = partition_3smooth(N)
    n = sum(part)
    denom = hook_product(part)
    num = factorial(n)
    return num // denom


def to_sci_10(x: int) -> str:
    """
    Format a positive integer in scientific notation with 10 digits after the decimal,
    rounded half-up, using a lowercase 'e' (as required by the problem).
    Example: 112233... -> 1.1223344557e17
    """
    assert x > 0
    s = str(x)
    exp = len(s) - 1
    decimals = 10
    sig = 1 + decimals  # total significant digits to keep (before rounding)

    if len(s) <= sig:
        mant = s[0] + "." + s[1:].ljust(decimals, "0")
        return f"{mant}e{exp}"

    head = s[:sig]  # first 11 digits
    next_digit = ord(s[sig]) - 48  # 12th digit as int
    rounded = int(head) + (1 if next_digit >= 5 else 0)

    if rounded == 10**sig:
        # Carry overflow, e.g. 9.999... rounds to 1.000...e(exp+1)
        exp += 1
        mant = "1." + "0" * decimals
        return f"{mant}e{exp}"

    d = str(rounded).rjust(sig, "0")
    mant = d[0] + "." + d[1:]
    return f"{mant}e{exp}"


def solve() -> str:
    return to_sci_10(F(10**18))


def _self_test() -> None:
    # Test values given in the problem statement
    assert F(6) == 5
    assert F(8) == 9
    assert F(20) == 450
    assert to_sci_10(F(1000)) == "8.8521816557e21"


if __name__ == "__main__":
    _self_test()
    print(solve())
