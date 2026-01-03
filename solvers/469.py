#!/usr/bin/env python3
"""
Project Euler 469: Empty Chairs

We have N chairs on a circle. Knights sit one-by-one, each time choosing uniformly among
currently "available" chairs, where available means empty and not adjacent to an already
occupied chair. The process stops at a maximal independent set; C is the fraction of
empty chairs at the end, and E(N) is the expected value of C.

For the huge input N = 10^18, the expected empty fraction is (1 + e^-2)/2, which is the
exact jamming-limit value for 1D random sequential adsorption with nearest-neighbor
exclusion (equivalently, a random greedy maximal independent set on a long cycle).
Finite-size corrections are O(1/N), so they are far below 10^-14 when N = 10^18.

We still implement the standard recurrence for E(n) to verify the sample values:
E(4) = 1/2 and E(6) = 5/9.

No external libraries are used (only Python standard library).
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, getcontext
from fractions import Fraction


def expected_fraction_exact(n: int) -> Fraction:
    """
    Exact E(n) as a rational number for small n, using the recurrence:

        E(1) = 0
        E(2) = 1/2
        E(3) = 2/3
        E(n) = ((n-1)(n-4) / (n(n-3))) * E(n-1) + (2(n-2) / (n(n-3))) * E(n-2)   for n>=4

    This is only used for assertions/tests (it is O(n)).
    """
    if n < 1:
        raise ValueError("n must be >= 1")

    if n == 1:
        return Fraction(0, 1)
    if n == 2:
        return Fraction(1, 2)
    if n == 3:
        return Fraction(2, 3)

    e_nm2 = Fraction(1, 2)  # E(2)
    e_nm1 = Fraction(2, 3)  # E(3)

    for k in range(4, n + 1):
        a = Fraction((k - 1) * (k - 4), k * (k - 3))
        b = Fraction(2 * (k - 2), k * (k - 3))
        e_n = a * e_nm1 + b * e_nm2
        e_nm2, e_nm1 = e_nm1, e_n

    return e_nm1


def solve(n: int = 10**18) -> str:
    # Sample checks from the problem statement
    assert expected_fraction_exact(4) == Fraction(1, 2)
    assert expected_fraction_exact(6) == Fraction(5, 9)

    # High precision so rounding to 14 decimals is unambiguous
    getcontext().prec = 80

    # E(n) for n=10^18 is indistinguishable (to 14 dp) from the infinite-lattice value:
    # E = (1 + e^-2) / 2
    ans = (Decimal(1) + (-Decimal(2)).exp()) / 2

    # Round to exactly 14 digits after the decimal point
    q = Decimal("0." + "0" * 14)
    ans = ans.quantize(q, rounding=ROUND_HALF_UP)
    return str(ans)


if __name__ == "__main__":
    print(solve())
