#!/usr/bin/env python3
"""
Project Euler 581: 47-smooth triangular numbers

A number is p-smooth if it has no prime factors larger than p.
Let T(n) = n(n+1)/2 be the nth triangular number.
We need the sum of all indices n such that T(n) is 47-smooth.

Key observation:
    gcd(n, n+1) = 1
So T(n) is 47-smooth  <=>  n and n+1 are both 47-smooth.
Therefore, the task becomes:
    Sum all n for which (n, n+1) is a consecutive pair of 47-smooth numbers.

Størmer's theorem implies there are only finitely many consecutive pairs of P-smooth numbers
for any finite prime set P containing 2. For P = primes <= 47, the largest number appearing
in any consecutive pair is 1109496723126 (OEIS A117581, 15th term).
So it's sufficient to generate all 47-smooth numbers up to that limit and look for neighbors
that differ by 1.

Implementation:
    Generate all P-smooth numbers up to LIMIT in increasing order using a generalized
    Hamming-number ("ugly number") multi-pointer method (no heap, no external libraries).
    While generating, whenever the current smooth number is exactly 1 greater than the
    previous smooth number, add the previous one to the answer.
"""

from array import array


PRIMES_UP_TO_47 = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]

# Proven upper bound for the *larger* number in any consecutive pair of 47-smooth numbers.
# Source: OEIS A117581 (the 15th term corresponds to prime 47).
LIMIT_LARGER_IN_PAIR_47 = 1109496723126


def sum_indices_with_smooth_triangular(primes: list[int], max_larger_in_pair: int) -> int:
    """
    Return sum of all n such that n(n+1)/2 is smooth w.r.t. the given prime set.

    Because gcd(n, n+1) = 1, this is equivalent to summing all n where both n and n+1
    are smooth, i.e. where n and n+1 appear as consecutive items in the sorted list of
    smooth numbers.
    """
    # Generate smooth numbers in increasing order.
    smooth = array("Q", [1])

    k = len(primes)
    idx = [0] * k
    next_vals = [p for p in primes]  # p * smooth[0]

    prev = 1
    ans = 0

    # Multi-pointer generation:
    # next smooth is min(next_vals); advance every pointer that matches this minimum.
    while True:
        m = min(next_vals)
        if m > max_larger_in_pair:
            break

        smooth.append(m)

        # If prev and m are consecutive smooth numbers, then prev is an index n such that
        # T(n) is smooth (because prev and prev+1 are both smooth).
        if m == prev + 1:
            ans += prev
        prev = m

        for j in range(k):
            if next_vals[j] == m:
                idx[j] += 1
                next_vals[j] = primes[j] * smooth[idx[j]]

    return ans


def solve() -> int:
    return sum_indices_with_smooth_triangular(PRIMES_UP_TO_47, LIMIT_LARGER_IN_PAIR_47)


def _self_test() -> None:
    # Sanity checks on smaller prime sets, using known bounds for the largest number in
    # any consecutive pair (OEIS A117581):
    # primes {2} -> max larger is 2; consecutive pair (1,2) => sum indices = 1
    assert sum_indices_with_smooth_triangular([2], 2) == 1
    # primes {2,3} -> max larger is 9; indices are 1,2,3,8 => sum = 14
    assert sum_indices_with_smooth_triangular([2, 3], 9) == 14
    # primes {2,3,5} -> max larger is 81; indices are 1,2,3,4,5,8,9,15,24,80 => sum = 151
    assert sum_indices_with_smooth_triangular([2, 3, 5], 81) == 151


if __name__ == "__main__":
    _self_test()
    print(solve())
