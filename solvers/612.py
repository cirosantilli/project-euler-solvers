#!/usr/bin/env python3
"""
Project Euler 612: Friend numbers

Two numbers are "friend numbers" if their base-10 representations share at least one common digit.

Let f(n) be the number of pairs (p, q) with 1 <= p < q < n such that p and q are friend numbers.
Given: f(100) = 1539
Find:  f(10^18) mod 1000267129
"""

MOD = 1000267129
DIGITS = 10
MASKS = 1 << DIGITS  # 1024


def count_digit_masks_upto(m: int) -> list[int]:
    """
    Count, for each digit-mask, how many integers x satisfy 1 <= x <= m,
    where the mask has bit d set iff digit d appears in x.
    """
    if m <= 0:
        return [0] * MASKS

    digits = [ord(c) - 48 for c in str(m)]  # faster than int(c) in tight loops

    # DP state: (mask, started, tight) -> count
    # started=False means we are still in leading zeros (no digit chosen yet).
    dp = {(0, 0, 1): 1}  # use ints for started/tight for speed

    for lim_digit in digits:
        nxt = {}
        for (mask, started, tight), cnt in dp.items():
            lim = lim_digit if tight else 9
            for d in range(lim + 1):
                ntight = 1 if (tight and d == lim) else 0
                if not started and d == 0:
                    # still leading zeros, digit-mask stays empty
                    key = (0, 0, ntight)
                else:
                    nmask = (mask if started else 0) | (1 << d)
                    key = (nmask, 1, ntight)
                nxt[key] = nxt.get(key, 0) + cnt
        dp = nxt

    counts = [0] * MASKS
    for (mask, started, _tight), cnt in dp.items():
        if started:
            counts[mask] += cnt
    return counts


def f(n: int) -> int:
    """
    Compute f(n) exactly as an integer (no modulus), for n >= 1.
    """
    m = n - 1  # we count numbers 1..m
    if m <= 1:
        return 0

    counts = count_digit_masks_upto(m)

    # Total unordered pairs among {1..m}
    total_pairs = m * (m - 1) // 2

    # Count unordered pairs whose digit-sets are disjoint (no common digit).
    # Friend pairs = total_pairs - disjoint_pairs
    disjoint_pairs = 0
    for a in range(1, MASKS):
        ca = counts[a]
        if ca == 0:
            continue
        for b in range(a + 1, MASKS):
            if (a & b) == 0:
                disjoint_pairs += ca * counts[b]

    return total_pairs - disjoint_pairs


def solve() -> int:
    # Test value from the problem statement
    assert f(100) == 1539

    return f(10**18) % MOD


if __name__ == "__main__":
    print(solve())
