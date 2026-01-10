#!/usr/bin/env python3
"""
Project Euler 635 - Subset Sums

Compute (S_2(10^8) + S_3(10^8)) mod 1_000_000_009.

No external libraries used.
"""

from __future__ import annotations

import sys
import math
from array import array

MOD = 1_000_000_009
INV2 = (MOD + 1) // 2
K9 = (9 * INV2) % MOD  # 9/2 mod MOD


def sieve_odd(limit: int) -> bytearray:
    """
    Odd-only sieve.

    Index i represents odd number 2*i + 1.
    Returns bytearray of length limit//2 + 1 where entry is 1 if prime (for that odd), else 0.
    """
    if limit < 1:
        return bytearray()

    size = limit // 2 + 1
    is_prime = bytearray(b"\x01") * size
    is_prime[0] = 0  # 1 is not prime

    r = int(math.isqrt(limit))
    for p in range(3, r + 1, 2):
        if is_prime[p // 2]:
            start = (p * p) // 2
            step = p
            is_prime[start::step] = b"\x00" * (((size - start - 1) // step) + 1)
    return is_prime


def fill_inverse_consecutive(out: array, max_n: int, block: int) -> None:
    """
    Fill out[x] = x^{-1} (mod MOD) for x = 1..max_n, using blockwise batch inversion.

    out must be an array('I') of length >= max_n+1.
    out[0] is unused.
    """
    mod = MOD
    pow_ = pow

    # prefix products for one block, reused
    pref = array("I", [0]) * (block + 1)

    s = 1
    while s <= max_n:
        cnt = min(block, max_n - s + 1)

        pref[0] = 1
        x = s
        # forward prefix products
        for i in range(cnt):
            pref[i + 1] = (pref[i] * x) % mod
            x += 1

        inv_total = pow_(pref[cnt], mod - 2, mod)

        # reverse to recover each inverse
        x = s + cnt - 1
        for i in range(cnt - 1, -1, -1):
            out[x] = (pref[i] * inv_total) % mod
            inv_total = (inv_total * x) % mod
            x -= 1

        s += cnt


def fill_inverse_odds(inv_odd: array, max_odd: int, block: int) -> None:
    """
    Fill inv_odd[i] = (2*i+1)^{-1} (mod MOD) for i = 0..max_odd//2, using blockwise batch inversion.

    inv_odd must be array('I') of length >= max_odd//2 + 1.
    """
    mod = MOD
    pow_ = pow

    pref = array("I", [0]) * (block + 1)

    count = max_odd // 2 + 1
    idx = 0
    while idx < count:
        cnt = min(block, count - idx)

        pref[0] = 1
        x = 2 * idx + 1
        for i in range(cnt):
            pref[i + 1] = (pref[i] * x) % mod
            x += 2

        inv_total = pow_(pref[cnt], mod - 2, mod)

        x = 2 * (idx + cnt - 1) + 1
        for i in range(cnt - 1, -1, -1):
            inv_odd[idx + i] = (pref[i] * inv_total) % mod
            inv_total = (inv_total * x) % mod
            x -= 2

        idx += cnt


def compute_S2_S3(L: int, inv_block: int = 1_000_000) -> tuple[int, int]:
    """
    Compute S_2(L) and S_3(L) modulo MOD.

    Uses:
    - odd-only prime sieve up to L
    - recurrence for C(2n,n) and C(3n,n) over odd n
    - precomputed modular inverses:
        * inv_half[x] = x^{-1} for x <= (L+1)//2
        * inv_odd[i]  = (2*i+1)^{-1} for odd numbers up to 2L+3

    inv_block controls the block size used in batch-inversion precomputation.
    """
    if L < 2:
        return 0, 0

    is_prime = sieve_odd(L)

    # inverses needed for inv((n+1)/2) where n is odd <= L
    max_half = (L + 1) // 2
    inv_half = array("I", [0]) * (max_half + 1)
    fill_inverse_consecutive(inv_half, max_half, inv_block)

    # inverses needed for any odd up to 2L+3 (covers n, n+2, 2n+1, 2n+3)
    max_odd = 2 * L + 3
    inv_odd = array("I", [0]) * (max_odd // 2 + 1)
    fill_inverse_odds(inv_odd, max_odd, inv_block)

    # prime p=2 is exceptional (the roots-of-unity simplification used later assumes odd p)
    # A_2(2)=2, A_3(2)=6
    S2 = 2 if L >= 2 else 0
    S3 = 6 if L >= 2 else 0

    # Iterate odd n = 2*i+1, i=0..(L-1)//2
    max_i = (L - 1) // 2

    # Values for n=1 (i=0):
    C = 2  # C(2*1, 1)
    D = 3  # C(3*1, 1)

    # For current i (n=2*i+1):
    a1 = 3  # 2n+1 = 4*i+3
    a3 = 5  # 2n+3 = 4*i+5
    idx_a1 = 1  # (2n+1)//2 = 2*i+1
    idx_a3 = 2  # (2n+3)//2 = 2*i+2

    t1 = 2  # (3n+1)//2 = 3*i+2
    t2 = 5  # 3n+2 = 6*i+5
    t3 = 7  # 3n+4 = 6*i+7
    t4 = 4  # (3n+5)//2 = 3*i+4

    mod = MOD
    k9 = K9
    inv_odd_local = inv_odd
    inv_half_local = inv_half
    is_prime_local = is_prime

    i = 0
    while i <= max_i:
        if i >= 1 and is_prime_local[i]:
            invp = inv_odd_local[i]
            # n-1 = 2*i
            S2 = (S2 + (C + 4 * i) * invp) % mod
            S3 = (S3 + (D + 6 * i) * invp) % mod

        # Update to the next odd n (i -> i+1)
        invh = inv_half_local[i + 1]  # inverse of (n+1)//2
        invn2 = inv_odd_local[i + 1]  # inverse of (n+2) since n+2 = 2*(i+1)+1

        # C(2(n+2), n+2) from C(2n, n) for odd n:
        # C <- C * 2*(2n+1)*(2n+3) / (((n+1)/2)*(n+2))
        C = (C * a1) % mod
        C = (C * a3) % mod
        C = (C * invh) % mod
        C = (C * invn2) % mod
        C = (C * 2) % mod

        # D(3(n+2), n+2) from D(3n, n) for odd n (after cancelling factors of 2):
        # D <- D * (9/2) * ((3n+1)/2)*(3n+2)*(3n+4)*((3n+5)/2)
        #          / (((n+1)/2)*(n+2)*(2n+1)*(2n+3))
        D = (D * k9) % mod
        D = (D * t1) % mod
        D = (D * t2) % mod
        D = (D * t3) % mod
        D = (D * t4) % mod
        D = (D * invh) % mod
        D = (D * invn2) % mod
        D = (D * inv_odd_local[idx_a1]) % mod
        D = (D * inv_odd_local[idx_a3]) % mod

        i += 1
        a1 += 4
        a3 += 4
        idx_a1 += 2
        idx_a3 += 2
        t1 += 3
        t2 += 6
        t3 += 6
        t4 += 3

    return S2 % mod, S3 % mod


def solve(L: int = 100_000_000) -> int:
    s2, s3 = compute_S2_S3(L)
    return (s2 + s3) % MOD


def _self_tests() -> None:
    # Test values given in the problem statement
    # A_2(5)=52, A_3(5)=603
    assert (math.comb(10, 5) + 2 * 4) // 5 == 52
    assert (math.comb(15, 5) + 3 * 4) // 5 == 603

    # S_2(10)=554
    s2_10, _ = compute_S2_S3(10, inv_block=64)
    assert s2_10 == 554

    # S_2(100) mod MOD = 100433628
    # S_3(100) mod MOD = 855618282
    s2_100, s3_100 = compute_S2_S3(100, inv_block=64)
    assert s2_100 == 100_433_628
    assert s3_100 == 855_618_282


def main() -> None:
    _self_tests()
    L = 100_000_000
    if len(sys.argv) >= 2:
        L = int(sys.argv[1])
    print(solve(L))


if __name__ == "__main__":
    main()
