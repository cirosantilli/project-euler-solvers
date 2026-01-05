#!/usr/bin/env python3
"""Project Euler 254: Sums of Digit Factorials

We need:
  f(n)  = sum(d! for d in digits(n))
  sf(n) = digit_sum(f(n))
  g(i)  = smallest positive n with sf(n) = i
  sg(i) = digit_sum(g(i))

Compute sum_{i=1..150} sg(i).

Key idea used here:

For any integer k, let invf(k) be the smallest n such that f(n)=k.
Then sf(invf(k)) = digit_sum(k). So:
  g(i) = min_{k : digit_sum(k)=i} invf(k)

Any k can be written k = q*9! + r with 0 <= r < 9!.
The minimal-length representation of r as a sum of digit factorials is the
factoradic representation:
  r = sum_{d=1..8} a_d * d!   with 0 <= a_d <= d.
Then invf(k) has digits: a_1 copies of '1', ..., a_8 copies of '8', and q
copies of '9'. (Digit '0' never appears in the minimal representation.)

For each i, q only needs to be checked in the range [q_min, q_min+36], where
q_min is derived from the smallest decimal integer with digit-sum i.
"""

from __future__ import annotations

from array import array
from typing import List


FACT = [1] * 10
for _d in range(2, 10):
    FACT[_d] = FACT[_d - 1] * _d

FACT9 = FACT[9]  # 9! = 362880


def digit_sum(n: int) -> int:
    """Sum of decimal digits of n (n >= 0)."""
    s = 0
    while n:
        n, r = divmod(n, 10)
        s += r
    return s


def f(n: int) -> int:
    """Sum of factorials of digits."""
    s = 0
    while n:
        n, r = divmod(n, 10)
        s += FACT[r]
    return s


def sf(n: int) -> int:
    return digit_sum(f(n))


def min_number_with_digit_sum(s: int) -> int:
    """Smallest positive integer with decimal digit sum exactly s (s>=1)."""
    assert s >= 1
    q, r = divmod(s, 9)
    if r == 0:
        return int("9" * q)
    return int(str(r) + ("9" * q))


def precompute_low_digit_sums(limit: int) -> array:
    """digit_sum for all numbers 0..limit inclusive."""
    ds = array("B", [0]) * (limit + 1)
    for n in range(1, limit + 1):
        ds[n] = ds[n // 10] + (n % 10)
    return ds


def build_remainder_buckets() -> (
    tuple[List[List[int]], List[bytearray], bytearray, array]
):
    """Precompute factoradic digit-counts for every remainder r in [0, 9!-1].

    Returns:
      buckets_by_mod9: list of 9 lists, each list sorted from best->worst
                       remainder according to the number formed by digits 1..8.
      counts: list of 9 bytearrays (index 1..8 used), counts[d][r] = a_d
      rem_len: bytearray length of remainder digit multiset
      rem_sg:  array('H') digit-sum contribution from digits 1..8
    """
    n = FACT9

    # counts[d][r] where d in 0..8; we ignore index 0.
    counts = [bytearray(n) for _ in range(9)]
    rem_len = bytearray(n)
    rem_sg = array("H", [0]) * n

    # Packed sortable items per residue: (code << 19) | r, since r < 2^19.
    packed: List[List[int]] = [[] for _ in range(9)]

    f1, f2, f3, f4, f5, f6, f7, f8 = (
        FACT[1],
        FACT[2],
        FACT[3],
        FACT[4],
        FACT[5],
        FACT[6],
        FACT[7],
        FACT[8],
    )
    # Unroll the divisions a bit for speed.
    for r in range(n):
        x = r
        a8, x = divmod(x, f8)
        a7, x = divmod(x, f7)
        a6, x = divmod(x, f6)
        a5, x = divmod(x, f5)
        a4, x = divmod(x, f4)
        a3, x = divmod(x, f3)
        a2, x = divmod(x, f2)
        a1, x = divmod(x, f1)

        counts[1][r] = a1
        counts[2][r] = a2
        counts[3][r] = a3
        counts[4][r] = a4
        counts[5][r] = a5
        counts[6][r] = a6
        counts[7][r] = a7
        counts[8][r] = a8

        ln = a1 + a2 + a3 + a4 + a5 + a6 + a7 + a8
        rem_len[r] = ln
        rem_sg[r] = (
            1 * a1 + 2 * a2 + 3 * a3 + 4 * a4 + 5 * a5 + 6 * a6 + 7 * a7 + 8 * a8
        )

        # Sort key: length ascending, then more small digits first.
        # Encode as base-9 integer: smaller code => better.
        code = ln
        code = code * 9 + (8 - a1)
        code = code * 9 + (8 - a2)
        code = code * 9 + (8 - a3)
        code = code * 9 + (8 - a4)
        code = code * 9 + (8 - a5)
        code = code * 9 + (8 - a6)
        code = code * 9 + (8 - a7)
        code = code * 9 + (8 - a8)
        packed[r % 9].append((code << 19) | r)

    buckets_by_mod9: List[List[int]] = [[] for _ in range(9)]
    mask = (1 << 19) - 1
    for m in range(9):
        arr = packed[m]
        arr.sort()
        buckets_by_mod9[m] = [p & mask for p in arr]

    return buckets_by_mod9, counts, rem_len, rem_sg


def solve(limit_i: int = 150) -> int:
    # Precompute digit sums for the low 6 digits of (base + r).
    # base % 1e6 plus r (r<9!) fits within 0..1_362_879.
    low_ds = precompute_low_digit_sums(1_000_000 + FACT9 - 1)

    buckets_by_mod9, counts, rem_len, rem_sg = build_remainder_buckets()

    total = 0
    for i in range(1, limit_i + 1):
        kmin = min_number_with_digit_sum(i)
        qmin = kmin // FACT9

        best_key = None
        best_sg = None

        residue = i % 9
        bucket = buckets_by_mod9[residue]

        # Only need to try q in [qmin, qmin+36], but we can stop early once
        # q itself is already >= best total length found so far.
        for delta in range(37):
            q = qmin + delta

            if best_key is not None and q >= best_key[0]:
                break

            base = q * FACT9

            high, low = divmod(base, 1_000_000)
            sum_high = digit_sum(high)
            sum_high1 = digit_sum(high + 1)

            need0 = i - sum_high
            need1 = i - sum_high1
            # Low 6-digit part can only sum to 0..54.
            if need0 < 0 or need0 > 54:
                need0 = -1
            if need1 < 0 or need1 > 54:
                need1 = -1

            # Scan remainders in best-first order; first match is optimal for this q.
            found_r = -1
            for r in bucket:
                t = low + r
                if t < 1_000_000:
                    if need0 >= 0 and low_ds[t] == need0:
                        found_r = r
                        break
                else:
                    if need1 >= 0 and low_ds[t - 1_000_000] == need1:
                        found_r = r
                        break

            if found_r < 0:
                continue

            r = found_r
            ln = rem_len[r]
            length_total = q + ln
            key = (
                length_total,
                -counts[1][r],
                -counts[2][r],
                -counts[3][r],
                -counts[4][r],
                -counts[5][r],
                -counts[6][r],
                -counts[7][r],
                -counts[8][r],
                -q,
            )

            if best_key is None or key < best_key:
                best_key = key
                best_sg = int(rem_sg[r]) + 9 * q

        assert best_sg is not None
        total += best_sg

    return total


def _run_self_tests() -> None:
    # Values explicitly given in the Project Euler 254 statement.
    assert f(342) == 32
    assert sf(342) == 5
    assert sf(25) == 5

    # The statement says it can be verified that g(5)=25 and g(20)=267.
    # We verify via direct computation for small i (cheap).
    def brute_g(ii: int, limit: int = 2_000_000) -> int:
        for n in range(1, limit + 1):
            if sf(n) == ii:
                return n
        raise AssertionError(f"brute_g({ii}) exceeded limit")

    assert brute_g(5, 1000) == 25
    assert digit_sum(25) == 7
    assert brute_g(20, 1_000_000) == 267
    # Sum_{i=1..20} sg(i) == 156
    s = 0
    for ii in range(1, 21):
        s += digit_sum(brute_g(ii, 2_000_000))
    assert s == 156


def main() -> None:
    _run_self_tests()
    print(solve(150))


if __name__ == "__main__":
    main()
