#!/usr/bin/env python3
"""
Project Euler 684 - Inverse Digit Sum

We need:
  s(n): smallest non-negative integer with digit sum n
  S(k) = sum_{n=1..k} s(n)
  Answer = sum_{i=2..90} S(f_i) mod 1_000_000_007

Key observation:
If n = 9q + r with 0 <= r <= 8, then
  s(n) = (r+1)*10^q - 1
(e.g. n=10 => q=1,r=1 => 2*10 - 1 = 19)

This allows a closed form for S(k) using geometric sums of powers of 10 mod MOD.
"""

MOD = 1_000_000_007


def s_small(n: int) -> int:
    """Exact s(n) for small n (used only for asserts)."""
    if n < 0:
        raise ValueError("n must be non-negative")
    q, r = divmod(n, 9)
    return (r + 1) * (10**q) - 1  # works for n=0 too: s(0)=0


def S_mod(k: int, mod: int = MOD) -> int:
    """
    Compute S(k) = sum_{n=1..k} s(n) modulo mod, in O(log k) time.

    Group n by q = n//9. For fixed q, r runs 0..8:
      s(9q+r) = (r+1)*10^q - 1
      sum_{r=0..8} s(9q+r) = 45*10^q - 9
    Use geometric series for sum_{q} 10^q.
    """
    if k <= 0:
        return 0

    q, r = divmod(k, 9)
    p10 = pow(10, q, mod)  # 10^q mod mod

    # Full blocks for q' = 0..q-1:
    # sum (45*10^{q'} - 9) = 5*(10^q - 1) - 9*q
    part_full = (5 * (p10 - 1) - 9 * q) % mod

    # Last partial block for q with r' = 0..r:
    # sum_{t=1..r+1} (t*10^q - 1) = 10^q * (r+1)(r+2)/2 - (r+1)
    tri = (r + 1) * (r + 2) // 2  # small integer (r<=8)
    part_tail = (p10 * (tri % mod) - (r + 1)) % mod

    return (part_full + part_tail) % mod


def solve() -> int:
    total = 0
    f0, f1 = 0, 1  # f_0, f_1
    for _i in range(2, 91):  # i = 2..90 inclusive
        f0, f1 = f1, f0 + f1
        total = (total + S_mod(f1)) % MOD
    return total


def _self_test() -> None:
    # Test values given in the problem statement
    assert s_small(10) == 19
    assert S_mod(20) == 1074

    # A couple of tiny sanity checks
    assert S_mod(1) == 1
    assert S_mod(9) == sum(s_small(n) for n in range(1, 10)) % MOD


if __name__ == "__main__":
    _self_test()
    print(solve())
