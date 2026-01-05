#!/usr/bin/env python3
"""
Project Euler 426 - Box-Ball System

We are given an initial configuration described by alternating run lengths of
occupied (1) and empty (0) boxes, starting with occupied boxes.

A classical result for the (capacity-1) Box-Ball System is that it eventually
decomposes into solitons; the multiset of soliton sizes equals the "final state"
(consecutive occupied block sizes once the system has stabilized).

Takahashi & Satsuma gave an algorithm to identify solitons directly from the
initial word without simulating time steps. This program implements that
algorithm in O(number_of_runs) time using a stack and run-length encoding.

Answer required: sum of squares of the final state's elements.
"""

from __future__ import annotations


def _ts_soliton_sum_squares_from_runs(
    runs, start_with_one: bool = True, collect: bool = False
):
    """
    Takahashi–Satsuma soliton identification algorithm on a run-length encoded word.

    runs:
        Iterable of positive integers giving alternating run lengths.
    start_with_one:
        True if the first run is occupied (1), else empty (0).
    collect:
        If True, also returns the sorted list of soliton sizes (the final state).
        Intended only for small test cases.

    Returns:
        (sum_sq, final_state_sorted) if collect else sum_sq
    """
    # Represent the doubly-infinite word by adding a huge leading 0-run (never removed)
    # and a sufficiently large trailing 0-run (added after total balls is known).
    stack_sym = [0]  # 0/1 symbols
    stack_len = [10**18]  # "infinite" leading zeros (record)
    solitons = [] if collect else None

    sum_sq = 0
    total_balls = 0
    cur_sym = 1 if start_with_one else 0

    def record(k: int) -> None:
        nonlocal sum_sq
        sum_sq += k * k
        if solitons is not None:
            solitons.append(k)

    # Stream runs and apply the TS reduction whenever the last run is >= its predecessor.
    for L in runs:
        if cur_sym == 1:
            total_balls += L

        # Push/merge the incoming run.
        if stack_sym[-1] == cur_sym:
            stack_len[-1] += L
        else:
            stack_sym.append(cur_sym)
            stack_len.append(L)

        # Reduce: whenever current run length >= previous run length, extract a soliton of size prev.
        while len(stack_len) >= 2 and stack_len[-1] >= stack_len[-2]:
            k = stack_len[-2]
            record(k)

            cur_s = stack_sym[-1]
            cur_l = stack_len[-1] - k

            # Remove the previous run (size k) and the first k symbols of current run.
            stack_sym.pop()
            stack_len.pop()
            stack_sym.pop()
            stack_len.pop()

            # Reinsert the remainder of current run, merging if needed.
            if cur_l > 0:
                if stack_sym[-1] == cur_s:
                    stack_len[-1] += cur_l
                else:
                    stack_sym.append(cur_s)
                    stack_len.append(cur_l)

        cur_sym ^= 1  # alternate 1/0 for next run

    # Add trailing zeros long enough to play the role of "infinite zeros to the right".
    # A length >= total number of balls is sufficient; we add a small cushion.
    trailing_zeros = total_balls + 100
    if stack_sym[-1] == 0:
        stack_len[-1] += trailing_zeros
    else:
        stack_sym.append(0)
        stack_len.append(trailing_zeros)

    while len(stack_len) >= 2 and stack_len[-1] >= stack_len[-2]:
        k = stack_len[-2]
        record(k)

        cur_s = stack_sym[-1]
        cur_l = stack_len[-1] - k

        stack_sym.pop()
        stack_len.pop()
        stack_sym.pop()
        stack_len.pop()

        if cur_l > 0:
            if stack_sym[-1] == cur_s:
                stack_len[-1] += cur_l
            else:
                stack_sym.append(cur_s)
                stack_len.append(cur_l)

    if solitons is not None:
        solitons.sort()
        return sum_sq, solitons
    return sum_sq


def _t_sequence_runs(n: int):
    """
    Generate t_0..t_n inclusive (n+1 values), as specified in the problem.
    """
    s = 290797
    for _ in range(n + 1):
        yield (s % 64) + 1
        s = (s * s) % 50515093


def solve(n: int = 10_000_000) -> int:
    """
    Compute the Project Euler 426 answer for runs (t_0, t_1, ..., t_n).
    """
    return _ts_soliton_sum_squares_from_runs(
        _t_sequence_runs(n), start_with_one=True, collect=False
    )


def _run_tests() -> None:
    # Example in statement: (2, 2, 2, 1, 2) -> final state [1, 2, 3], answer 14.
    ssq, fs = _ts_soliton_sum_squares_from_runs(
        [2, 2, 2, 1, 2], start_with_one=True, collect=True
    )
    assert fs == [1, 2, 3]
    assert ssq == 14

    # Example in statement: starting from (t0..t10) final state is [1, 3, 10, 24, 51, 75].
    ssq2, fs2 = _ts_soliton_sum_squares_from_runs(
        _t_sequence_runs(10), start_with_one=True, collect=True
    )
    assert fs2 == [1, 3, 10, 24, 51, 75]
    assert ssq2 == sum(x * x for x in fs2)


if __name__ == "__main__":
    _run_tests()
    print(solve())
