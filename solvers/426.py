#!/usr/bin/env python3
"""
Project Euler 426 - Box-Ball System

We use the Takahashi–Satsuma (TS) soliton identification algorithm in its
"data stream" form:

Start with an infinite run of zeros to the left. Read the configuration
(left to right), appending symbols. Whenever the last two runs have equal
length, those 2*len symbols annihilate; this annihilation corresponds to
one soliton of that length. The multiset of soliton lengths is invariant
under the BBS dynamics, and in the long-time regime the occupied blocks
are exactly these solitons (sorted increasingly from left to right).
Therefore the required answer is the sum of squares of all annihilated
run lengths.

The initial configuration is given in run-length encoding (t0,t1,...),
alternating 1-runs and 0-runs, starting with 1. We process these runs
without expanding to individual boxes by maintaining a stack of run
lengths that always strictly decreases from left to right. Appending a
new run can trigger a cascade of annihilations, which we handle with a
small loop that consumes the appended run length in chunks.
"""

from __future__ import annotations


def ts_sum_squares_from_rle(lengths, start_with_one: bool = True, want_final_state: bool = False):
    """
    lengths: iterable of positive ints describing alternating run lengths.
             If start_with_one=True, the first run is occupied (1s), then empty (0s), etc.
    want_final_state: if True, also return the sorted list of soliton sizes (final state's occupied blocks).

    Returns:
        (sum_squares, final_state_list?) where final_state_list is increasing.
    """
    # Stack of [symbol, length] representing the current alternating suffix.
    # Invariant: run lengths strictly decrease from bottom to top of stack.
    stack = []
    sum_sq = 0
    solitons = [] if want_final_state else None

    def record(k: int) -> None:
        nonlocal sum_sq
        sum_sq += k * k
        if solitons is not None:
            solitons.append(k)

    def process_run(sym: int, L: int) -> None:
        # Processes a run of L copies of sym (0 or 1) using chunked updates.
        nonlocal stack
        remaining = L
        while remaining > 0:
            if not stack:
                stack.append([sym, remaining])
                return

            last_sym, last_len = stack[-1]

            if last_sym == sym:
                # Extend existing last run.
                if len(stack) == 1:
                    stack[-1][1] = last_len + remaining
                    return

                prev_len = stack[-2][1]
                # We cannot let the last run reach or exceed prev_len without annihilating at equality.
                if last_len + remaining < prev_len:
                    stack[-1][1] = last_len + remaining
                    return

                # Consume exactly enough to reach equality, then annihilate the last two runs.
                consumed = prev_len - last_len
                remaining -= consumed
                stack.pop()
                stack.pop()
                record(prev_len)
                # Continue with any leftover symbols of the same sym.
            else:
                # Create a new run (sym, ?). It will annihilate with the current last run
                # as soon as its length reaches last_len.
                if remaining < last_len:
                    stack.append([sym, remaining])
                    return

                remaining -= last_len
                stack.pop()
                record(last_len)
                # Continue with leftover of sym, which will now match the new last symbol (if any).

    # Stream the alternating runs
    sym = 1 if start_with_one else 0
    balls = 0
    for L in lengths:
        if sym == 1:
            balls += L
        process_run(sym, L)
        sym ^= 1

    # The real configuration has infinitely many empty boxes to the right.
    # Appending sufficiently many zeros completes all remaining annihilations.
    # Adding (balls + 64) zeros is safely more than enough.
    process_run(0, balls + 64)

    if solitons is not None:
        solitons.sort()
        return sum_sq, solitons
    return sum_sq


def generate_t_values(n: int):
    """Yield t_0, t_1, ..., t_n as defined in the problem."""
    s = 290797
    for _ in range(n + 1):
        yield (s % 64) + 1
        s = (s * s) % 50515093


def solve(n: int = 10_000_000) -> int:
    """Compute the required sum of squares for (t_0, ..., t_n)."""
    return ts_sum_squares_from_rle(generate_t_values(n))


def _tests() -> None:
    # Example from the statement: (2,2,2,1,2) -> final state [1,2,3] -> 14
    ssq, final_state = ts_sum_squares_from_rle([2, 2, 2, 1, 2], want_final_state=True)
    assert final_state == [1, 2, 3]
    assert ssq == 14

    # Example using (t_0,...,t_10) -> [1,3,10,24,51,75]
    t0_10 = list(generate_t_values(10))
    ssq2, final_state2 = ts_sum_squares_from_rle(t0_10, want_final_state=True)
    assert final_state2 == [1, 3, 10, 24, 51, 75]
    # Optional: verify the sum of squares of that list
    assert ssq2 == sum(x * x for x in final_state2)


def main() -> None:
    _tests()
    print(solve(10_000_000))


if __name__ == "__main__":
    main()
