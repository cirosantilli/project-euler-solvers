"""Project Euler #269: Polynomials with at Least One Integer Root.

We define P_n(x) as the polynomial whose coefficients are the digits of n.
We must compute Z(10^16): how many positive integers n <= 10^16 have P_n
with at least one integer root.

Key observations used in this solution:

* For x > 0, P_n(x) > 0 because all coefficients are non-negative and the
  leading digit is positive. So the only non-negative integer root possible is
  x = 0.
* By the Rational Root Theorem, any integer root r must divide the constant
  term (the last digit). Therefore, for n not ending in 0 the only possible
  integer roots are negative integers -k where 1 <= k <= 9.
* For a fixed k, the condition P_n(-k) = 0 can be counted via a small
  "carry" dynamic program over digits (least-significant to most-significant):

    Let S_i = sum_{j=0}^{i-1} d_j (-k)^j be the value contributed by the first
    i digits (from the units place upward). Maintain an integer carry c_i such
    that S_i = c_i (-k)^i.

    Adding digit d_i yields S_{i+1} = (c_i + d_i) (-k)^i, so we need
    (c_i + d_i) to be divisible by k and then
        c_{i+1} = -(c_i + d_i) / k.

    Start with c_0 = 0 and require c_L = 0 after L digits.

* To count numbers having *any* negative root, we apply inclusion-exclusion
  over k in {1..9}. Because we separate out the disjoint case "last digit = 0",
  we only need inclusion-exclusion over negative roots.

The input bound is 10^16, so n <= 10^16-1 covers all numbers with at most 16
digits. The remaining number 10^16 itself ends with 0 and is included.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Tuple


def _count_for_subset_and_length(ks: Tuple[int, ...], length: int) -> int:
    """Count length-digit numbers (leading digit nonzero, last digit nonzero)
    whose digit polynomial has roots at -k for every k in ks.

    Digits are processed from least significant (position 0) to most significant
    (position length-1).
    """

    m = len(ks)
    if m == 0:
        return 0

    def digits_for_pos(i: int) -> range:
        # last digit (i=0) must be nonzero to avoid the separate root-0 case
        # leading digit (i=length-1) must be nonzero as well
        if length == 1:
            return range(1, 10)
        if i == 0 or i == length - 1:
            return range(1, 10)
        return range(10)

    start_state = (0,) * m
    dp: Dict[Tuple[int, ...], int] = {start_state: 1}

    for i in range(length):
        ndp: Dict[Tuple[int, ...], int] = defaultdict(int)
        for state, ways in dp.items():
            for d in digits_for_pos(i):
                new_state: List[int] = []
                ok = True
                for c, k in zip(state, ks):
                    s = c + d
                    if s % k != 0:
                        ok = False
                        break
                    new_state.append(-(s // k))
                if ok:
                    ndp[tuple(new_state)] += ways
        dp = ndp
        if not dp:
            return 0

    return dp.get(start_state, 0)


def solve() -> int:
    """Compute Z(10^16)."""

    # Disjoint case: root 0 <=> last digit is 0.
    # Count of positive integers n <= 10^16 with last digit 0 is exactly 10^15.
    root0_count = 10**15

    # Count numbers with last digit nonzero that have at least one negative root.
    # For n <= 10^16-1, these are exactly the numbers with 1..16 digits.
    max_len = 16
    union_count = 0

    # Precompute counts for all nonempty subsets of {1..9} and lengths 1..16.
    # Use inclusion-exclusion to count "at least one" root.
    for mask in range(1, 1 << 9):
        ks = tuple(i + 1 for i in range(9) if (mask >> i) & 1)
        sign = 1 if (len(ks) % 2 == 1) else -1
        subset_total = 0
        for L in range(1, max_len + 1):
            subset_total += _count_for_subset_and_length(ks, L)
        union_count += sign * subset_total

    return root0_count + union_count


def _has_integer_root_bruteforce(n: int) -> bool:
    """Brute check for whether P_n has an integer root.

    Uses the fact that any integer root must be 0 or a divisor of the constant
    term (last digit). Since the constant term is a digit, possible nonzero
    integer roots are among {-1, ..., -9}.
    """

    digits = [int(ch) for ch in str(n)]
    last = digits[-1]

    # Root 0
    if last == 0:
        return True

    # Possible negative roots: -d for d | last
    for d in range(1, last + 1):
        if last % d != 0:
            continue
        r = -d
        val = 0
        for dig in digits:
            val = val * r + dig
        if val == 0:
            return True
    return False


def _Z_bruteforce(k: int) -> int:
    return sum(1 for n in range(1, k + 1) if _has_integer_root_bruteforce(n))


def main() -> None:
    # Test value from the problem statement.
    assert _Z_bruteforce(100_000) == 14_696

    print(solve())


if __name__ == "__main__":
    main()
