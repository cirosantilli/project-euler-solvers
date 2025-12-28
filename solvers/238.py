#!/usr/bin/env python3
"""Project Euler 238: Infinite string tour.

We generate one full period of the digit stream, build a bitset of all prefix-sum
residues, and then determine p(k) for k=1..T (T = digit-sum of one period) by
covering all sums with the earliest starting positions.

The required answer is:
    sum_{k=1}^{2*10^15} p(k)

The problem statement provides a check:
    sum_{k=1}^{1000} p(k) = 4742
"""

from __future__ import annotations

import math
from typing import Dict, List, Tuple


# --- Problem constants ---
S0 = 14025256
MOD = 20300713
TARGET_K = 2_000_000_000_000_000  # 2*10^15


# --- Small-number utilities (everything here is <= ~2e7) ---
def _factorize(n: int) -> Dict[int, int]:
    """Prime factorization by trial division (fast enough for our sizes)."""
    res: Dict[int, int] = {}
    while n % 2 == 0:
        res[2] = res.get(2, 0) + 1
        n //= 2
    f = 3
    # f*f <= n
    while f * f <= n:
        while n % f == 0:
            res[f] = res.get(f, 0) + 1
            n //= f
        f += 2
    if n > 1:
        res[n] = res.get(n, 0) + 1
    return res


def _totient_from_factorization(factors: Dict[int, int]) -> int:
    """Euler's totient from a prime factorization."""
    n = 1
    for p, e in factors.items():
        n *= p**e
    phi = n
    for p in factors:
        phi = phi // p * (p - 1)
    return phi


def _multiplicative_order(a: int, mod: int, group_order: int) -> int:
    """Return ord_mod(a) given that it divides group_order and gcd(a,mod)=1."""
    if math.gcd(a, mod) != 1:
        raise ValueError("a and mod must be coprime")
    order = group_order
    for p in _factorize(group_order).keys():
        while order % p == 0 and pow(a, order // p, mod) == 1:
            order //= p
    return order


def _bbs_period() -> int:
    """Compute the period (in s_n terms) of the BBS recurrence for this seed."""
    # MOD factors quickly by trial division.
    # MOD = p*q (Blum integer).
    p = q = 0
    tmp = MOD
    d = 2
    while d * d <= tmp:
        if tmp % d == 0:
            p = d
            q = tmp // d
            break
        d += 1 if d == 2 else 2
    if p == 0:
        raise RuntimeError("Failed to factor modulus")

    lam = (p - 1) * (q - 1) // math.gcd(p - 1, q - 1)  # Carmichael for p*q (lcm)
    ord_s0 = _multiplicative_order(S0, MOD, lam)
    # s_n = s0^(2^n) (mod MOD); period is ord_{ord_s0}(2)
    phi_ord_s0 = _totient_from_factorization(_factorize(ord_s0))
    return _multiplicative_order(2, ord_s0, phi_ord_s0)


# --- Core bitset logic ---
def _set_bit(bits: bytearray, idx: int) -> None:
    bits[idx >> 3] |= 1 << (idx & 7)


def _build_period_digits(period_terms: int) -> Tuple[bytearray, int]:
    """Return (digits_as_ascii_bytes, total_digit_sum) for one full period."""
    s = S0
    digits = bytearray()
    total = 0
    for _ in range(period_terms):
        bs = str(s).encode()  # ASCII digits
        digits.extend(bs)
        # digit sum = sum(byte_values) - 48*len
        total += sum(bs) - 48 * len(bs)
        s = (s * s) % MOD
    return digits, total


def _build_prefix_residue_bitset(digits_ascii: bytearray, T: int) -> int:
    """Bit i is 1 iff residue i (mod T) occurs among prefix sums in the period."""
    bits = bytearray((T + 7) // 8)
    _set_bit(bits, 0)
    s = 0
    for b in digits_ascii:
        s += b - 48
        # within one period s is in [0, T], so s%T is either s or 0
        idx = 0 if s == T else s
        _set_bit(bits, idx)
    return int.from_bytes(bits, "little")


def _compute_sums(
    digits_ascii: bytearray, present: int, T: int, prefix_limits: List[int]
) -> Tuple[int, Dict[int, int], int]:
    """Compute sum_{k=1..T} p(k) and sum_{k=1..r} p(k) for r in prefix_limits.

    We represent sums k in [1..T] as residues in [0..T-1] where residue 0 means k=T.

    Returns (sum_all, {r: sum_{k=1..r} p(k)}, starts_processed).
    """
    mask = (1 << T) - 1

    # Unknown sums for the full [1..T] range.
    unknown = mask

    # For each r (<T): track bits 1..r (exclude bit 0 because it represents k=T).
    prefix_masks: Dict[int, int] = {}
    prefix_sums: Dict[int, int] = {r: 0 for r in prefix_limits}
    for r in prefix_limits:
        if r <= 0:
            prefix_masks[r] = 0
        else:
            # bits 0..r set then clear bit 0 => bits 1..r
            prefix_masks[r] = ((1 << (r + 1)) - 1) ^ 1

    total_all = 0
    rot = present  # circular right shift by current prefix sum (starts at 0)

    for i, b in enumerate(digits_ascii):
        new = unknown & rot
        if new:
            cnt = new.bit_count()
            w = i + 1  # starting position is 1-indexed
            total_all += w * cnt
            for r in prefix_limits:
                pm = prefix_masks[r]
                if pm:
                    c2 = (new & pm).bit_count()
                    if c2:
                        prefix_sums[r] += w * c2

            unknown ^= new
            if unknown == 0:
                return total_all, prefix_sums, w

        d = b - 48
        if d:
            # rot = circular_right_shift(rot, d)
            rot = ((rot >> d) | (rot << (T - d))) & mask

    raise RuntimeError("Did not cover all sums within one period")


def solve() -> int:
    # 1) Period of the BBS sequence (in s_n terms)
    period_terms = _bbs_period()

    # 2) Build one period of the digit stream and its total digit sum T
    digits_ascii, T = _build_period_digits(period_terms)

    # 3) Prefix-sum residue bitset (mod T)
    present = _build_prefix_residue_bitset(digits_ascii, T)

    # 4) Use periodicity of p(k): p(k) depends only on k mod T (with 0 -> T)
    q, rem = divmod(TARGET_K, T)

    # Compute:
    #   sum_{k=1..T} p(k)
    #   sum_{k=1..1000} p(k)  (assert)
    #   sum_{k=1..rem} p(k)
    sum_all, prefix_sums, _ = _compute_sums(digits_ascii, present, T, [1000, rem])

    # Problem statement check
    assert prefix_sums[1000] == 4742

    ans = q * sum_all + prefix_sums[rem]
    return ans


def main() -> None:
    print(solve())


if __name__ == "__main__":
    main()
