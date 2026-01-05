#!/usr/bin/env python3
"""
Project Euler 374: Maximum Integer Partition Product

We need:
  S(N) = sum_{1<=n<=N} f(n)*m(n)  (mod 982451653)
where f(n) is the maximum product over partitions of n into DISTINCT parts,
and m(n) is the number of parts in any partition that attains that maximum.

This program prints S(10^14) mod 982451653.

No external libraries are used (only Python standard library).
"""

from __future__ import annotations

from array import array
import math

MOD = 982451653
TARGET_N = 10**14


def max_base_k(n: int) -> int:
    """
    Let S_k = 2+3+...+k = k*(k+1)//2 - 1.
    For each n>=2 there is a unique k>=2 such that S_k <= n <= S_{k+1}-1.

    Return that k (the "base" maximum element for the optimal partition).
    """
    # Solve k(k+1)/2 - 1 <= n  =>  k^2+k-2(n+1) <= 0
    d = 1 + 8 * (n + 1)
    s = math.isqrt(d)
    k = (s - 1) // 2
    # adjust for any integer sqrt rounding
    while k * (k + 1) // 2 - 1 > n:
        k -= 1
    while (k + 1) * (k + 2) // 2 - 1 <= n:
        k += 1
    return k


def best_partition(n: int) -> list[int]:
    """
    Construct an optimal (max-product) partition of n into distinct parts.

    Used only for small-value tests (exact arithmetic).
    """
    if n <= 0:
        raise ValueError("n must be positive")
    if n == 1:
        return [1]

    k = max_base_k(n)
    if k == 2:
        # Only one part is possible/optimal in this range.
        return [n]

    parts = list(range(2, k + 1))  # 2..k (k-1 parts)
    t = k - 1
    r = n - (k * (k + 1) // 2 - 1)  # remainder within this k-block, 0..k
    q, s = divmod(r, t)  # for k>=3, q is 0 or 1
    if q:
        for i in range(t):
            parts[i] += q
    if s:
        # add 1 to the largest s parts
        for i in range(t - 1, t - s - 1, -1):
            parts[i] += 1
    return parts


def f_m(n: int) -> tuple[int, int]:
    """Return (f(n), m(n)) exactly for small n (by constructing the partition)."""
    parts = best_partition(n)
    prod = 1
    for x in parts:
        prod *= x
    return prod, len(parts)


def sum_fm_exact(limit: int) -> int:
    """Exact sum for small limits (used for statement checks)."""
    total = 0
    for n in range(1, limit + 1):
        f, m = f_m(n)
        total += f * m
    return total


def solve(limit: int = TARGET_N, mod: int = MOD) -> int:
    """
    Compute sum_{1<=n<=limit} f(n)*m(n) (mod mod), with mod prime (as in the problem).

    Time:  O(K) where K ~ floor((sqrt(1+8(limit+1))-1)/2) ~ sqrt(2*limit)
    Memory: O(K) for modular inverses.
    """
    if limit < 1:
        return 0

    p = mod
    inv2 = (p + 1) // 2  # modular inverse of 2 since p is an odd prime

    # n=1 special case
    ans = 1

    if limit == 1:
        return ans % p

    # Determine last k-block and remainder
    k_last = max_base_k(limit)
    r_max = limit - (k_last * (k_last + 1) // 2 - 1)  # 0..k_last

    # Precompute modular inverses inv[i] for i up to k_last (needs p prime).
    # inv[i] = p - (p//i) * inv[p%i] (mod p) for i>=2
    inv_size = max(2, k_last) + 1
    inv = array("I", [0]) * inv_size
    inv[1] = 1
    for i in range(2, inv_size):
        inv[i] = p - (p // i) * inv[p % i] % p

    # k=2 block covers n=2..4 with f(n)=n and m(n)=1
    upto = 4 if limit >= 4 else limit
    if upto >= 2:
        # sum_{n=2..upto} n
        cnt = upto - 1
        ans += (2 + upto) * cnt // 2
    ans %= p

    if k_last < 3:
        # limit is within the k=2 block, we're done
        return ans

    # For k>=3, let H_k = sum_{m=3..k} inv[m] (mod p) (running).
    # For a full k-block (all n with this k), we can show:
    #   sum_{r=0..k} f(S_k+r) = k! * ( 1 + (k+1)*H_k + (2k+3)/2 )   (mod p)
    # and m(n)=k-1 for all n in that block.
    fact = 2  # 2!
    sum_inv3 = 0  # H_k running
    prefix_Lm1 = 0

    need_prefix = 1 <= r_max <= k_last - 2
    capture_k = (
        k_last - r_max
    )  # L-1, where L = k_last - r_max + 1 (only used if need_prefix)
    chunk = 4096  # reduce costly mod operations on ans
    c = 0

    # Full blocks k=3..k_last-1
    for k in range(3, k_last):
        fact = (fact * k) % p
        sum_inv3 += inv[k]
        if sum_inv3 >= p:
            sum_inv3 -= p

        tmp = (1 + (k + 1) * sum_inv3 + (2 * k + 3) * inv2) % p
        sum_f_block = (fact * tmp) % p

        ans += (k - 1) * sum_f_block
        c += 1
        if c == chunk:
            ans %= p
            c = 0

        if need_prefix and k == capture_k:
            prefix_Lm1 = sum_inv3

    if c:
        ans %= p

    # Last (possibly partial) block k=k_last
    k = k_last
    fact = (fact * k) % p
    sum_inv3 += inv[k]
    if sum_inv3 >= p:
        sum_inv3 -= p

    if r_max <= k - 2:
        if r_max == 0:
            sum_f = fact
        else:
            # Need sum_{m=L..k} inv[m] where L=k-r_max+1 (and L>=3 here)
            sum_inv_range = (sum_inv3 - prefix_Lm1) % p
            tmp = (1 + (k + 1) * sum_inv_range) % p
            sum_f = (fact * tmp) % p
    elif r_max == k - 1:
        tmp = (1 + (k + 1) * sum_inv3 + (k + 1) * inv2) % p
        sum_f = (fact * tmp) % p
    else:
        # r_max == k -> full block
        tmp = (1 + (k + 1) * sum_inv3 + (2 * k + 3) * inv2) % p
        sum_f = (fact * tmp) % p

    ans = (ans + (k - 1) * sum_f) % p
    return ans


def _self_test() -> None:
    # Tests explicitly stated in the problem statement:
    f5, m5 = f_m(5)
    assert (f5, m5) == (6, 2)

    f10, m10 = f_m(10)
    assert (f10, m10) == (30, 3)
    assert f10 * m10 == 90

    assert sum_fm_exact(100) == 1683550844462
    assert solve(100) == 1683550844462 % MOD


def main() -> None:
    _self_test()
    print(solve(TARGET_N, MOD))


if __name__ == "__main__":
    main()
