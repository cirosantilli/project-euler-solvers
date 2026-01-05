#!/usr/bin/env python3
"""
Project Euler 368: A Kempner-like Series

We sum 1/n over all positive integers n whose decimal representation does NOT
contain 3 or more equal consecutive digits.

The series converges; print the value rounded to 10 digits after the decimal.
"""

from __future__ import annotations

import math


# ----------------------------
# Helpers / tests from statement
# ----------------------------


def has_3_equal_consecutive_digits(n: int) -> bool:
    """Return True iff decimal representation of n contains a run of >= 3 identical digits."""
    last = -1
    run = 0
    while n > 0:
        d = n % 10
        n //= 10
        if d == last:
            run += 1
            if run >= 3:
                return True
        else:
            last = d
            run = 1
    return False


def kempner_no_digit_9_sum() -> float:
    """
    Kempner series: sum_{n>=1, n has no digit '9'} 1/n.
    The problem statement says it converges to approximately 22.9206766193.

    We compute it using a length-DP with a binomial-series expansion.
    This is only used as a correctness assert (not needed for Euler 368 itself).
    """
    # Truncation parameters chosen to comfortably reach ~1e-9 accuracy.
    K = 180  # highest power used in the expansion
    MAX_LEN = 450  # enough because the count grows like 9^L

    pow10inv = [0.0] * (K + 1)
    for j in range(1, K + 1):
        pow10inv[j] = 10.0 ** (-j)

    # comb[j][i] = C(j+i-1, i)  (with i >= 0)
    comb = [[0.0] * (K + 1) for _ in range(K + 1)]
    for j in range(1, K + 1):
        for i in range(0, K - j + 1):
            comb[j][i] = math.comb(j + i - 1, i)

    # Sd[i] = sum_{d=0..8} (-d/10)^i
    Sd = [0.0] * (K + 1)
    Sd[0] = 9.0
    for i in range(1, K + 1):
        s = 0.0
        for d in range(9):
            s += (-d / 10.0) ** i
        Sd[i] = s

    # G[j] for current length = sum_{allowed length} 1/n^j
    prev = [0.0] * (K + 1)
    for j in range(1, K + 1):
        prev[j] = sum((1.0 / d) ** j for d in range(1, 9))  # length=1: digits 1..8

    total = prev[1]
    for _length in range(2, MAX_LEN + 1):
        nxt = [0.0] * (K + 1)
        for j in range(1, K + 1):
            base = pow10inv[j]
            s = 0.0
            # 1/(10y+d)^j = 10^-j * sum_i C(j+i-1,i) * (-d/10)^i * 1/y^{j+i}
            for i in range(0, K - j + 1):
                s += comb[j][i] * Sd[i] * prev[i + j]
            nxt[j] = base * s
        total += nxt[1]
        prev = nxt

    return total


def run_statement_asserts() -> None:
    # Statement: out of the first 1200 terms, exactly 20 are omitted; list given.
    expected_omitted = [
        111,
        222,
        333,
        444,
        555,
        666,
        777,
        888,
        999,
        1000,
        1110,
        1111,
        1112,
        1113,
        1114,
        1115,
        1116,
        1117,
        1118,
        1119,
    ]
    omitted = [n for n in range(1, 1201) if has_3_equal_consecutive_digits(n)]
    assert omitted == expected_omitted, (len(omitted), omitted[:5], omitted[-5:])

    # Statement: the classic Kempner series (omit denominators containing '9') converges to ~22.9206766193.
    k = kempner_no_digit_9_sum()
    assert abs(k - 22.9206766193) < 5e-9, k


# ----------------------------
# Euler 368 solver
# ----------------------------


def solve() -> float:
    """
    Compute S = sum_{n>=1, n has no run of >=3 equal consecutive digits} 1/n.

    Technique:
    Track, for each length L and last digit d, whether the final run length is 1 (f1)
    or 2 (f2). For each such bucket we store sums of 1/n^j for j=1..K, and advance
    length using the binomial-series expansion:
        1/(10y + d)^j = 10^-j * sum_{i>=0} C(j+i-1,i) * (-d/10)^i * 1/y^{j+i}.
    """
    K = 20
    TAIL_TOL = 5e-13
    MAX_LEN = 10000
    R_BOUND = 0.991  # safe upper bound on the eventual geometric ratio of per-length contributions

    pow10inv = [0.0] * (K + 1)
    for j in range(1, K + 1):
        pow10inv[j] = 10.0 ** (-j)

    # comb[j][i] = C(j+i-1, i) for i>=0
    comb = [[0.0] * (K + 1) for _ in range(K + 1)]
    for j in range(1, K + 1):
        for i in range(0, K - j + 1):
            comb[j][i] = math.comb(j + i - 1, i)

    # f1[d][j] = sum_{x in S1(length,d)} 1/x^j  (final run length 1)
    # f2[d][j] = sum_{x in S2(length,d)} 1/x^j  (final run length 2)
    f1 = [[0.0] * (K + 1) for _ in range(10)]
    f2 = [[0.0] * (K + 1) for _ in range(10)]

    # Base: length=3, enumerate 100..999 excluding 111..999 with all 3 digits equal.
    for d in range(10):
        f1d = f1[d]
        f2d = f2[d]
        for pre in range(10, 100):
            a, b = divmod(pre, 10)
            if a == b == d:
                continue
            x = pre * 10 + d
            inv = 1.0 / x
            p = inv
            if b == d:
                dest = f2d
            else:
                dest = f1d
            for j in range(1, K + 1):
                dest[j] += p
                p *= inv

    # Include all 1- and 2-digit numbers (1..99), all of which are valid.
    ans = 0.0
    for n in range(1, 100):
        ans += 1.0 / n

    # Add length=3 contribution
    delta = 0.0
    for d in range(10):
        delta += f1[d][1] + f2[d][1]
    ans += delta

    # Grow length
    for _length in range(4, MAX_LEN + 1):
        # total[p] = sum_{all valid (length-1)-digit numbers} 1/n^p
        total = [0.0] * (K + 1)
        for p in range(1, K + 1):
            s = 0.0
            for d in range(10):
                s += f1[d][p] + f2[d][p]
            total[p] = s

        nf1 = [[0.0] * (K + 1) for _ in range(10)]
        nf2 = [[0.0] * (K + 1) for _ in range(10)]

        for d in range(10):
            md = -d / 10.0
            f1d = f1[d]
            f2d = f2[d]
            nf1d = nf1[d]
            nf2d = nf2[d]
            for j in range(1, K + 1):
                base = pow10inv[j]
                pre_pow = 1.0  # (-d/10)^i
                for i in range(0, K - j + 1):
                    c = comb[j][i] * pre_pow * base
                    pwr = i + j

                    # S2: append digit d to a prefix ending with a *single* d
                    f1dp = f1d[pwr]
                    nf2d[j] += c * f1dp

                    # S1: append digit d to a prefix ending with digit != d
                    excl = f1dp + f2d[pwr]  # sums for prefixes ending with digit d
                    nf1d[j] += c * (total[pwr] - excl)

                    pre_pow *= md

        f1, f2 = nf1, nf2

        delta = 0.0
        for d in range(10):
            delta += f1[d][1] + f2[d][1]
        ans += delta

        # Tail estimate: after a modest length, contributions decay ~geometrically.
        tail_bound = delta * (R_BOUND / (1.0 - R_BOUND))
        if tail_bound < TAIL_TOL:
            break

    return ans


def main() -> None:
    run_statement_asserts()
    value = solve()
    print(f"{value:.10f}")


if __name__ == "__main__":
    main()
