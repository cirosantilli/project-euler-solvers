from __future__ import annotations

from math import gcd, isqrt
from typing import List


def solve(limit: int) -> int:
    """
    Counts perimeters L <= limit that can form exactly one integer-sided right triangle.
    Uses Euclid's formula for primitive Pythagorean triples and counts their multiples.
    """
    counts: List[int] = [0] * (limit + 1)

    # For primitive triples: a=m^2-n^2, b=2mn, c=m^2+n^2
    # Perimeter p0 = a+b+c = 2*m*(m+n)
    m_max = isqrt(limit // 2) + 1

    for m in range(2, m_max + 1):
        for n in range(1, m):
            # primitive conditions: gcd(m,n)=1 and m,n have opposite parity
            if ((m ^ n) & 1) == 0:
                continue
            if gcd(m, n) != 1:
                continue

            p0 = 2 * m * (m + n)
            if p0 > limit:
                break

            for p in range(p0, limit + 1, p0):
                counts[p] += 1

    return sum(1 for c in counts if c == 1)


def _self_test() -> None:
    # From the examples: L <= 50 has exactly these singular perimeters:
    # 12, 24, 30, 36, 40, 48 => 6
    assert solve(50) == 6

    # Project Euler 75 known answer:
    assert solve(1_500_000) == 161_667


if __name__ == "__main__":
    _self_test()
    result = solve(1_500_000)
    print(result)
