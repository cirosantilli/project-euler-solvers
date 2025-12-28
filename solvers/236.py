# Project Euler 236: Luxury Hampers
#
# We have 5 products. Supplier A supplied A_i units, supplier B supplied B_i units.
# Let a_i, b_i be the numbers spoiled (integers).
#
# Per-product spoilage rates: (b_i/B_i) = m * (a_i/A_i) for all i, for some m>1.
# Overall spoilage rates: (sum a_i / sum A_i) = m * (sum b_i / sum B_i).
#
# The task: find the largest possible m, in lowest terms, and print as "u/v".
#
# The problem statement also states:
#   - there are exactly 35 possible m>1
#   - the smallest is 1476/1475
#
# This program asserts those facts and then prints the largest m.

from __future__ import annotations

from math import gcd
from typing import Set, Tuple


A = [5248, 1312, 2624, 5760, 3936]
B = [640, 1888, 3776, 3776, 5664]
SA = sum(A)
SB = sum(B)

A1, A2, A3, A4, A5 = A
B1, B2, B3, B4, B5 = B


def _reduce_fraction(num: int, den: int) -> Tuple[int, int]:
    g = gcd(num, den)
    return num // g, den // g


def compute_all_m() -> Set[Tuple[int, int]]:
    """
    Returns the set of all possible m values as reduced integer pairs (num, den).

    Key idea:
    Products 2,3,5 have A_i/B_i = 41/59, hence m = (41*b_i)/(59*a_i).
    Therefore b_i/a_i shares a common reduced ratio r/s across i=2,3,5:
        (a2,b2) = (s*t2, r*t2), etc.

    Enforcing the same m on products 1 and 4 gives proportionality constraints:
        59*s*b1 = 5*r*a1
        90*s*b4 = 41*r*a4
    which again imply (a1,b1) and (a4,b4) are multiples of base pairs derived from gcds.

    The overall condition becomes linear in T = t2+t3+t5, letting us solve for T
    directly for each choice of multipliers t1 and t4.
    """
    m_values: Set[Tuple[int, int]] = set()

    # Enumerate reduced ratio k = r/s = b2/a2.
    # Since m = (41*r)/(59*s) and m>1, require r/s > 59/41.
    for s in range(1, A2 + 1):  # s <= 1312
        r_start = (59 * s) // 41 + 1
        if r_start > B2:
            continue

        for r in range(r_start, B2 + 1):  # r <= 1888
            if gcd(r, s) != 1:
                continue

            # Products 2,3,5: (a,b)=(s*t, r*t)
            t2_max = min(A2 // s, B2 // r)
            t3_max = min(A3 // s, B3 // r)
            t5_max = min(A5 // s, B5 // r)
            if t2_max < 1 or t3_max < 1 or t5_max < 1:
                continue
            T_max = t2_max + t3_max + t5_max  # sums [3..T_max] are all achievable

            # Product 1: 59*s*b1 = 5*r*a1
            d1 = gcd(59 * s, 5 * r)
            a1_base = (59 * s) // d1
            b1_base = (5 * r) // d1
            t1_max = min(A1 // a1_base, B1 // b1_base)
            if t1_max < 1:
                continue

            # Product 4: 90*s*b4 = 41*r*a4
            d4 = gcd(90 * s, 41 * r)
            a4_base = (90 * s) // d4
            b4_base = (41 * r) // d4
            t4_max = min(A4 // a4_base, B4 // b4_base)
            if t4_max < 1:
                continue

            # Overall condition:
            # (sum a)/SA = m*(sum b)/SB with m = (41*r)/(59*s)
            # Cross-multiply: (sum a)*SB*(59*s) = (sum b)*SA*(41*r)
            L = SB * 59 * s
            R = SA * 41 * r

            # Sa = a1_base*t1 + s*T + a4_base*t4
            # Sb = b1_base*t1 + r*T + b4_base*t4
            # Solve for T from (Sa)*L = (Sb)*R.
            denom = s * L - r * R  # SB*59*s^2 - SA*41*r^2
            if denom == 0:
                continue

            c1 = b1_base * R - a1_base * L
            c4 = b4_base * R - a4_base * L

            found = False
            for t1 in range(1, t1_max + 1):
                base = c1 * t1
                for t4 in range(1, t4_max + 1):
                    num = base + c4 * t4
                    if num % denom != 0:
                        continue
                    T = num // denom
                    if 3 <= T <= T_max:
                        mn, md = _reduce_fraction(41 * r, 59 * s)
                        m_values.add((mn, md))
                        found = True
                        break
                if found:
                    break

    return m_values


def solve() -> str:
    m_values = compute_all_m()

    # Asserts from the problem statement
    assert len(m_values) == 35, f"Expected 35 m values, got {len(m_values)}"
    assert (1476, 1475) in m_values, "Expected 1476/1475 to be a valid m"

    # Exact maximum by cross multiplication
    it = iter(m_values)
    max_num, max_den = next(it)
    for num, den in it:
        if num * max_den > max_num * den:
            max_num, max_den = num, den

    return f"{max_num}/{max_den}"


if __name__ == "__main__":
    print(solve())
