#!/usr/bin/env python3
"""
Project Euler 255: Rounded Square Roots

This script computes the average number of iterations required by the
integer Heron-like procedure described in the problem statement for all
14-digit integers n with 10^13 <= n < 10^14.

No external libraries are used (standard library only).

Notes
-----
- The final numeric answer is computed at runtime and is intentionally not
  embedded anywhere as a constant.
- Self-tests (asserts) cover the example n=4321 and the 5-digit average
  given in the statement.
"""

from __future__ import annotations

import math
import os
import multiprocessing as mp
from typing import List, Tuple


def x0_for_digit_length(d: int) -> int:
    """Initial guess x0 from the problem statement for numbers with d digits."""
    if d <= 0:
        raise ValueError("digit length must be positive")
    if d % 2 == 1:
        return 2 * (10 ** ((d - 1) // 2))
    return 7 * (10 ** ((d - 2) // 2))


def step(n: int, x: int) -> int:
    """One iteration: floor((x + ceil(n/x)) / 2)."""
    return (x + (n + x - 1) // x) // 2


def rounded_sqrt_and_iterations(n: int) -> Tuple[int, int]:
    """
    Run the stated procedure for a single n.

    Returns (rounded_square_root, iterations_count).
    """
    if n <= 0:
        raise ValueError("n must be positive")
    d = len(str(n))
    x = x0_for_digit_length(d)
    it = 0
    while True:
        it += 1
        x1 = step(n, x)
        if x1 == x:
            return x, it
        x = x1


def _round_ratio_to_decimal_string(num: int, den: int, digits: int = 10) -> str:
    """
    Convert the positive rational num/den to a decimal string rounded to
    'digits' places after the decimal point (round-half-up).
    """
    if den <= 0:
        raise ValueError("den must be positive")
    if num < 0:
        raise ValueError("num must be non-negative")

    scale = 10**digits
    # round-half-up for positive rationals:
    scaled = (2 * num * scale + den) // (2 * den)
    integer_part = scaled // scale
    frac_part = scaled % scale
    return f"{integer_part}.{frac_part:0{digits}d}"


def _iters_sum_over_s_interval(mm: int, s_lo: int, s_hi: int, x0: int) -> int:
    """
    Sum of iteration counts over all n = mm + s, for integer s in [s_lo, s_hi],
    using exact interval splitting.

    The splitting is done over s because for a fixed current estimate x,
    ceil((mm+s)/x) is constant on contiguous sub-intervals of s.
    """
    if s_lo > s_hi:
        return 0

    total = 0
    segs: List[Tuple[int, int, int, int]] = [(s_lo, s_hi, x0, 0)]  # (a,b,x,k)
    while segs:
        new: List[Tuple[int, int, int, int]] = []
        for a, b, x, k in segs:
            q_lo = (mm + a + x - 1) // x
            q_hi = (mm + b + x - 1) // x
            nk = k + 1

            # q only varies a few steps because (b-a) is small compared to x.
            for q in range(q_lo, q_hi + 1):
                # s satisfying ceil((mm+s)/x) == q is:
                # (q-1)*x < mm+s <= q*x
                sa = (q - 1) * x - mm + 1
                if sa < a:
                    sa = a
                sb = q * x - mm
                if sb > b:
                    sb = b
                if sa > sb:
                    continue

                cnt = sb - sa + 1
                x1 = (x + q) // 2

                if x1 == x:
                    total += nk * cnt
                else:
                    # merge adjacent segments when possible to keep the list tiny
                    if (
                        new
                        and new[-1][2] == x1
                        and new[-1][3] == nk
                        and new[-1][1] + 1 == sa
                    ):
                        prev_a, _prev_b, _prev_x, _prev_k = new[-1]
                        new[-1] = (prev_a, sb, x1, nk)
                    else:
                        new.append((sa, sb, x1, nk))
        segs = new
    return total


def _chunk_sum_full_intervals(args: Tuple[int, int, int]) -> int:
    """
    Worker: sum iteration counts over all full rounded-root intervals I_m
    for m in [m_start, m_end], inclusive.

    For a given m, I_m corresponds to s in [-m+1, m] with n = m^2 + s.
    """
    m_start, m_end, x0 = args
    total = 0

    m = m_start
    mm = m * m
    while m <= m_end:
        total += _iters_sum_over_s_interval(mm, -m + 1, m, x0)

        # advance to (m+1)^2 without recomputing via multiplication
        mm += 2 * m + 1
        m += 1
    return total


def average_iterations_for_digit_length(d: int, processes: int | None = None) -> str:
    """
    Compute the average iteration count for all d-digit numbers, formatted
    to 10 decimal places (as required by the problem).
    """
    if d <= 0:
        raise ValueError("d must be positive")

    L = 10 ** (d - 1)
    U = 10**d - 1
    x0 = x0_for_digit_length(d)

    # Determine which rounded-root intervals I_m are fully inside [L,U].
    m_full_start = math.isqrt(L)
    while m_full_start * m_full_start - m_full_start + 1 < L:
        m_full_start += 1

    m_full_end = math.isqrt(U)
    while m_full_end * m_full_end + m_full_end > U:
        m_full_end -= 1

    total = 0

    # Lower partial interval (at most one m)
    m_low = m_full_start - 1
    if m_low > 0:
        mm = m_low * m_low
        end = mm + m_low
        if end >= L:
            s_lo = L - mm
            s_min = -m_low + 1
            if s_lo < s_min:
                s_lo = s_min
            s_hi = m_low  # since end is within I_m
            total += _iters_sum_over_s_interval(mm, s_lo, s_hi, x0)

    # Upper partial interval (at most one m)
    m_high = m_full_end + 1
    mm = m_high * m_high
    start = mm - m_high + 1
    if start <= U:
        s_lo = -m_high + 1
        s_hi = U - mm
        if s_hi > m_high:
            s_hi = m_high
        total += _iters_sum_over_s_interval(mm, s_lo, s_hi, x0)

    # Full intervals: m in [m_full_start, m_full_end]
    if m_full_start <= m_full_end:
        if processes is None:
            env = os.environ.get("PE255_PROCS", "").strip()
            if env:
                try:
                    processes = max(1, int(env))
                except ValueError:
                    processes = None
            if processes is None:
                # conservative default to avoid oversubscription in shared environments
                processes = min(8, os.cpu_count() or 1)

        # Create chunks for multiprocessing
        n_m = m_full_end - m_full_start + 1
        chunk = (n_m + processes - 1) // processes
        tasks: List[Tuple[int, int, int]] = []
        for i in range(processes):
            a = m_full_start + i * chunk
            if a > m_full_end:
                break
            b = min(m_full_end, a + chunk - 1)
            tasks.append((a, b, x0))

        if processes == 1 or len(tasks) == 1:
            for t in tasks:
                total += _chunk_sum_full_intervals(t)
        else:
            with mp.Pool(processes=processes) as pool:
                for subtotal in pool.imap_unordered(
                    _chunk_sum_full_intervals, tasks, chunksize=1
                ):
                    total += subtotal

    count = U - L + 1

    # Optional internal sanity check: counts from interval decomposition match total size.
    # (Only uses O(1) arithmetic; no extra heavy work.)
    partial_low_cnt = 0
    if m_low > 0:
        mm = m_low * m_low
        end = mm + m_low
        if end >= L:
            partial_low_cnt = m_low - (L - mm) + 1

    partial_high_cnt = 0
    mm = m_high * m_high
    start = mm - m_high + 1
    if start <= U:
        partial_high_cnt = (U - mm) - (-m_high + 1) + 1

    full_cnt = 0
    if m_full_start <= m_full_end:
        full_cnt = (m_full_start + m_full_end) * (
            m_full_end - m_full_start + 1
        )  # sum of 2m

    assert partial_low_cnt + full_cnt + partial_high_cnt == count

    return _round_ratio_to_decimal_string(total, count, digits=10)


def _self_test() -> None:
    # Example from the statement.
    root, it = rounded_sqrt_and_iterations(4321)
    assert (root, it) == (66, 2)

    # The 5-digit average from the statement (rounded to 10 decimal places).
    # This brute-force check is small (90,000 values).
    L, U = 10_000, 99_999
    total = 0
    for n in range(L, U + 1):
        total += rounded_sqrt_and_iterations(n)[1]
    got = _round_ratio_to_decimal_string(total, U - L + 1, digits=10)
    assert got == "3.2102888889"


def main() -> None:
    _self_test()
    # Required output: average for 14-digit numbers, rounded to 10 decimal places.
    print(average_iterations_for_digit_length(14))


if __name__ == "__main__":
    main()
