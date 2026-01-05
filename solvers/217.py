#!/usr/bin/env python3
"""
Project Euler 217 - Balanced Numbers

Find T(47) mod 3^15, where T(n) is the sum of all balanced numbers < 10^n.

A k-digit number is balanced if the sum of its first ceil(k/2) digits equals the
sum of its last ceil(k/2) digits.
For odd k, this is equivalent to: sum(left half) == sum(right half) (middle cancels).
"""

MOD = 3**15  # 14348907


def build_unrestricted_dp(max_len: int, mod: int | None):
    """
    Digit-DP for sequences of length L (leading zeros allowed).

    Returns:
      counts[L][s] = number of length-L digit strings with digit-sum s
      sums[L][s]   = sum of their numeric values (interpreted as L-digit with leading zeros)
    """
    counts = [None] * (max_len + 1)
    sums = [None] * (max_len + 1)

    counts[0] = [1]  # one empty string with sum 0
    sums[0] = [0]

    for L in range(1, max_len + 1):
        prev_c = counts[L - 1]
        prev_s = sums[L - 1]
        max_sum = 9 * L

        c = [0] * (max_sum + 1)
        s = [0] * (max_sum + 1)

        for sum_prev in range(len(prev_c)):
            cp = prev_c[sum_prev]
            sp = prev_s[sum_prev]
            if cp == 0 and sp == 0:
                continue
            for d in range(10):
                idx = sum_prev + d
                c[idx] += cp
                s[idx] += sp * 10 + cp * d

        if mod is not None:
            c = [x % mod for x in c]
            s = [x % mod for x in s]

        counts[L] = c
        sums[L] = s

    return counts, sums


def left_from_unrestricted(L: int, un_counts, un_sums, pow10, mod: int | None):
    """
    Build DP arrays for LEFT halves of length L, where the *first digit of the whole number*
    must be non-zero. (So the first digit of the left half must be 1..9.)

    Returns:
      left_counts[s], left_sums[s]
    """
    if L == 0:
        return [1], [0]  # empty half

    tail_c = un_counts[L - 1]
    tail_s = un_sums[L - 1]
    max_sum = 9 * L

    left_c = [0] * (max_sum + 1)
    left_s = [0] * (max_sum + 1)

    for first_digit in range(1, 10):
        for tail_sum in range(len(tail_c)):
            cnt = tail_c[tail_sum]
            if cnt == 0 and tail_s[tail_sum] == 0:
                continue
            ssum = tail_sum + first_digit
            left_c[ssum] += cnt
            # value = first_digit * 10^(L-1) + tail_value
            left_s[ssum] += first_digit * pow10[L - 1] * cnt + tail_s[tail_sum]

    if mod is not None:
        left_c = [x % mod for x in left_c]
        left_s = [x % mod for x in left_s]

    return left_c, left_s


def T(n: int, mod: int | None = None) -> int:
    """
    Sum of all balanced numbers < 10^n.
    If mod is provided, returns the sum modulo mod.
    """
    if n <= 0:
        return 0

    maxL = n // 2  # maximum floor(k/2) among lengths k<=n

    # powers of 10 needed for positional contributions
    pow10 = [1] * (n + 2)
    for i in range(1, n + 2):
        pow10[i] = pow10[i - 1] * 10
        if mod is not None:
            pow10[i] %= mod

    un_counts, un_sums = build_unrestricted_dp(maxL, mod)

    # precompute left-half tables per L (to avoid rebuilding them twice for even/odd k sharing L)
    left_tables = [None] * (maxL + 1)
    for L in range(maxL + 1):
        left_tables[L] = left_from_unrestricted(L, un_counts, un_sums, pow10, mod)

    total = 0

    # length 1 is special: balanced, but must be 1..9 (no leading zero)
    if n >= 1:
        total += 45
        if mod is not None:
            total %= mod

    for k in range(2, n + 1):
        L = k // 2
        even = k % 2 == 0

        right_c = un_counts[L]
        right_s = un_sums[L]
        left_c, left_s = left_tables[L]

        max_sum = 9 * L
        sum_k = 0

        if even:
            # number = X * 10^L + Y
            mult_left = pow10[L]
            for s in range(max_sum + 1):
                cl = left_c[s]
                cr = right_c[s]
                if cl == 0 and cr == 0:
                    continue
                sum_k += (left_s[s] * mult_left) * cr + cl * right_s[s]
        else:
            # number = X * 10^(L+1) + d * 10^L + Y, with d in 0..9
            mult_left = pow10[L + 1]
            mult_mid = pow10[L]
            for s in range(max_sum + 1):
                cl = left_c[s]
                cr = right_c[s]
                if cl == 0 and cr == 0:
                    continue
                # left part: 10 choices for middle digit
                sum_k += left_s[s] * mult_left * cr * 10
                # middle digit contribution: sum_{d=0..9} d = 45
                sum_k += 45 * mult_mid * cl * cr
                # right part: 10 choices for middle digit
                sum_k += cl * right_s[s] * 10

        if mod is not None:
            sum_k %= mod
        total += sum_k
        if mod is not None:
            total %= mod

    return total % mod if mod is not None else total


def main():
    # Problem statement test values
    assert T(1) == 45
    assert T(2) == 540
    assert T(5) == 334795890

    print(T(47, MOD))


if __name__ == "__main__":
    main()
