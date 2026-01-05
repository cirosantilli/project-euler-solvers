#!/usr/bin/env python3
"""
Project Euler 195: Inscribed circles of triangles with one angle of 60 degrees.

We count integer-sided triangles with exactly one 60° angle whose inradius r <= N.
Given in the problem statement:
T(100) = 1234, T(1000) = 22767, T(10000) = 359912.
We need T(1053779).
"""

from math import gcd, isqrt


def T(N: int) -> int:
    """
    Count 60-degree integer-sided triangles with inradius r <= N.
    """
    N2 = N * N

    # For type-1 primitives: r0 = (sqrt(3)/2) * (m*n)
    # k_max = floor( sqrt(4N^2 / (3*(m*n)^2)) )
    # Need m*n <= floor(2N/sqrt(3)) to have k_max>=1.
    p1_max = isqrt((4 * N2) // 3)

    # For type-2 primitives: r0 = (sqrt(3)/6) * ((m-n)(m+2n)) = (sqrt(3)/6) * p2
    # k_max = floor( sqrt(12N^2 / p2^2) )
    # Need p2 <= floor(2*sqrt(3)*N) = floor(sqrt(12)*N) to have k_max>=1.
    p2_max = isqrt(12 * N2)

    num1 = 4 * N2
    num2 = 12 * N2
    total = 0

    # ---- Type 1 ----
    # Primitive parametrization (m>n, gcd(m,n)=1, (m-n) not divisible by 3).
    # Inradius for primitive: r0 = (sqrt3/2) * m*n
    for m in range(2, p1_max + 1):
        n_lim = p1_max // m
        if n_lim >= m:
            n_lim = m - 1
        for n in range(1, n_lim + 1):
            if (m - n) % 3 == 0:
                continue
            if gcd(m, n) != 1:
                continue
            p = m * n
            total += isqrt(num1 // (3 * p * p))

    # ---- Type 2 ----
    # Using d = m-n (so n = m-d), with gcd(m,d)=1 and d not divisible by 3.
    # p2 = (m-n)(m+2n) = d*(3m-2d)
    #
    # For each fixed m, solve d*(3m-2d) <= p2_max.
    # This quadratic is concave; solutions are outside the roots when discriminant > 0.
    m_max2 = (p2_max + 2) // 3  # from minimal p2 at d=1: 3m-2 <= p2_max
    for m in range(2, m_max2 + 1):
        # Roots of -2d^2 + 3m d - p2_max = 0 => D = 9m^2 - 8p2_max
        D = 9 * m * m - 8 * p2_max
        if D <= 0:
            ranges = [(1, m - 1)]
        else:
            s = isqrt(D)
            r1 = (3 * m - s) // 4  # floor of smaller root
            r2 = (3 * m + s + 3) // 4  # ceil of larger root

            # If there's no "gap" where p2 > p2_max, everything is valid.
            if r2 <= r1 + 1:
                ranges = [(1, m - 1)]
            else:
                ranges = []
                if r1 >= 1:
                    ranges.append((1, min(r1, m - 1)))
                if r2 <= m - 1:
                    ranges.append((r2, m - 1))

        for lo, hi in ranges:
            for d in range(lo, hi + 1):
                if d % 3 == 0:
                    continue
                if gcd(m, d) != 1:
                    continue
                p = d * (3 * m - 2 * d)
                total += isqrt(num2 // (p * p))

    return total


def main() -> None:
    # Tests from the problem statement
    assert T(100) == 1234
    assert T(1000) == 22767
    assert T(10000) == 359912

    print(T(1053779))


if __name__ == "__main__":
    main()
