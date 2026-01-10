#!/usr/bin/env python3
"""
Project Euler 528 - Constrained Sums

Let S(n, k, b) be the number of integer k-tuples (x1..xk) such that:
    x1 + x2 + ... + xk <= n
    0 <= xm <= b^m  for m=1..k

We compute:
    (sum_{k=10..15} S(10^k, k, k)) mod 1_000_000_007
"""

MOD = 1_000_000_007


def _inv_factorials_upto(n: int, mod: int = MOD):
    """Return (fact, inv_fact) lists for 0..n."""
    fact = [1] * (n + 1)
    for i in range(2, n + 1):
        fact[i] = (fact[i - 1] * i) % mod
    inv_fact = [1] * (n + 1)
    inv_fact[n] = pow(fact[n], mod - 2, mod)
    for i in range(n, 0, -1):
        inv_fact[i - 1] = (inv_fact[i] * i) % mod
    return fact, inv_fact


def comb_small_k(n: int, k: int, inv_fact_k: int, mod: int = MOD) -> int:
    """
    Compute C(n, k) mod mod for huge n but small k (k < mod).
    Uses falling factorial: n*(n-1)*...*(n-k+1) / k!
    """
    if n < k or k < 0:
        return 0
    prod = 1
    # Falling factorial modulo mod
    for i in range(k):
        prod = (prod * ((n - i) % mod)) % mod
    return (prod * inv_fact_k) % mod


def constrained_sums(n: int, k: int, b: int, mod: int = MOD) -> int:
    """
    Inclusion-exclusion over upper bounds.

    Unrestricted count (xi >= 0):  C(n + k, k)  for sum(xi) <= n.
    For any subset A where xi >= ui+1 (ui=b^i), shift those variables down by (ui+1),
    reducing the budget by sum(ui+1). Apply inclusion-exclusion.
    """
    # weights wi = (upper bound + 1) for variable i (1-indexed in statement)
    w = [
        pow(b, i, 1 << 63) for i in range(1, k + 1)
    ]  # dummy mod; we need exact ints below
    # The above pow with mod is just to avoid any accidental float; replace with exact pow:
    w = [b**i + 1 for i in range(1, k + 1)]

    # Precompute subset sums of w for all masks (0..2^k - 1)
    m = 1 << k
    shift = [0] * m
    for mask in range(1, m):
        lsb = mask & -mask
        i = lsb.bit_length() - 1
        shift[mask] = shift[mask ^ lsb] + w[i]

    # Precompute inv factorial for this k
    _, inv_fact = _inv_factorials_upto(k, mod)
    inv_fact_k = inv_fact[k]

    ans = 0
    for mask in range(m):
        budget = n - shift[mask]
        if budget < 0:
            continue
        N = budget + k  # choose k
        term = comb_small_k(N, k, inv_fact_k, mod)
        if mask.bit_count() & 1:
            ans -= term
        else:
            ans += term
    return ans % mod


def solve() -> int:
    total = 0
    for k in range(10, 16):
        total = (total + constrained_sums(10**k, k, k, MOD)) % MOD
    return total


def _self_test():
    # Test values from the problem statement
    assert constrained_sums(14, 3, 2, MOD) == 135
    assert constrained_sums(200, 5, 3, MOD) == 12949440
    assert constrained_sums(1000, 10, 5, MOD) == 624839075


if __name__ == "__main__":
    _self_test()
    print(solve())
