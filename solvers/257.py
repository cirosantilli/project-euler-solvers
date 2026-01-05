#!/usr/bin/env python3
"""Project Euler 257: Angular Bisectors

We count integer-sided triangles ABC (a <= b <= c, with AB=c, BC=a, AC=b)
such that area(ABC) / area(AEG) is an integer, where E and G are the points
where the angle bisectors from C and B meet AB and AC respectively.

The derivation in the README shows that the condition is equivalent to

    (a + b)(a + c) / (b c) = k  is an integer.

With a <= b <= c, we have (a+b) <= 2b and (a+c) <= 2c, so k <= 4.
Thus k ∈ {2,3,4}.

After some algebra and a change of variables, solutions can be enumerated by
coprime pairs (x,y) with y/x in a narrow interval, and each such pair yields
all solutions by scaling. The counting is done by summing floor(L / perimeter)
over the primitive perimeters.
"""

from __future__ import annotations

import math


def solve(limit: int = 100_000_000) -> int:
    """Return the number of triangles with perimeter <= limit."""

    N = limit
    gcd = math.gcd
    isqrt = math.isqrt

    # Case k = 4 (t = 3): Only equilateral triangles survive the ordering constraints.
    total = N // 3

    # Case k = 2 (t = 1)
    # Parameterization uses coprime (x,y) with x < y <= floor(sqrt(2)*x).
    # Minimal scaling factor depends only on y parity:
    #   g0 = y      if y is odd
    #   g0 = y / 2  if y is even
    # (Derivation in README.)
    # A safe upper bound for x follows from perimeter growing ~ x^2.
    x_max = int(math.sqrt(N * 2 / (3 + math.sqrt(2) + 2 / math.sqrt(2)))) + 10
    for x in range(3, x_max + 1):
        y_max = isqrt(2 * x * x)
        for y in range(x + 1, y_max + 1):
            if gcd(x, y) != 1:
                continue

            if y & 1:  # odd
                g0 = y
                a = g0 * x
                b = g0 * (x + y)
                c = x * (2 * x + y)
            else:  # even
                g0 = y >> 1
                a = g0 * x
                b = g0 * (x + y)
                c = (x * (2 * x + y)) >> 1

            p = a + b + c
            if p <= N:
                total += N // p

    # Case k = 3 (t = 2)
    # Coprime (x,y) with x < y <= floor(sqrt(3)*x).
    # Minimal scaling factor g0 can be computed from parity and divisibility by 3,
    # avoiding extra gcds.
    x_max = (
        int(
            math.sqrt(
                N
                * 3
                / (1 + (1 + math.sqrt(3)) / 2 + (3 + math.sqrt(3)) / (2 * math.sqrt(3)))
            )
        )
        + 10
    )
    for x in range(2, x_max + 1):
        y_max = isqrt(3 * x * x)
        x_odd = x & 1
        for y in range(x + 1, y_max + 1):
            if gcd(x, y) != 1:
                continue

            # denom2 = (2*y) / gcd(2y, x(3x+y)) simplified.
            if x_odd == 0:
                # x even => y odd (coprime), and parity doesn't introduce a factor of 2.
                denom2 = y // 3 if (y % 3 == 0) else y
            else:
                if (y & 1) == 0:
                    denom2 = (2 * y) // 3 if (y % 3 == 0) else 2 * y
                else:
                    denom2 = y // 3 if (y % 3 == 0) else y

            # denom1 = 1 if (x+y) even else 2. g0 = lcm(denom1, denom2).
            if ((x + y) & 1) == 0:
                g0 = denom2
            else:
                g0 = denom2 if (denom2 & 1) == 0 else 2 * denom2

            a = g0 * x
            b = g0 * (x + y) // 2
            c = g0 * x * (3 * x + y) // (2 * y)
            p = a + b + c
            if p <= N:
                total += N // p

    return total


def main() -> None:
    # Lightweight self-checks (not from the original statement):
    # brute-force verified for small limits.
    assert solve(100) == 46
    assert solve(200) == 100

    print(solve(100_000_000))


if __name__ == "__main__":
    main()
