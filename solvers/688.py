#!/usr/bin/env python3
"""
Project Euler 688: Piles of Plates

We stack n plates into k non-empty piles, all different sizes.
Let f(n,k) be the maximum possible size of the smallest pile.
Let F(n) = sum_{k>=1} f(n,k).
Let S(N) = sum_{n=1..N} F(n).

This program prints S(10^16) mod 1_000_000_007.

No external libraries are used.
"""

from math import isqrt

MOD = 1_000_000_007


def k_max_for_n(n: int) -> int:
    """
    Largest k such that it's possible to have k distinct positive pile sizes
    totaling <= n. The smallest such configuration is 1+2+...+k = k(k+1)/2.
    """
    # k(k+1)/2 <= n  <=>  k^2 + k - 2n <= 0
    # k = floor((sqrt(1+8n)-1)/2)
    return (isqrt(8 * n + 1) - 1) // 2


def f(n: int, k: int) -> int:
    """
    Closed form from the problem:
    Using piles m, m+1, ..., m+k-1 uses k*m + k(k-1)/2 plates.
    So the maximum feasible m is floor((n - k(k-1)/2)/k), clipped at 0.
    """
    b = k * (k - 1) // 2
    if n <= b:
        return 0
    return max(0, (n - b) // k)


def F(n: int) -> int:
    km = k_max_for_n(n)
    s = 0
    for k in range(1, km + 1):
        s += f(n, k)
    return s


def S_bruteforce(N: int) -> int:
    """Brute-force definition: sum_{n<=N} F(n). Suitable only for small N."""
    return sum(F(n) for n in range(1, N + 1))


def S_fast_exact(N: int) -> int:
    """
    Exact (non-modular) O(sqrt(N)) summation, derived by exchanging sums:

      S(N) = sum_{k>=1} sum_{m>=1, k*m + k(k-1)/2 <= N} (N+1 - (k*m + k(k-1)/2))

    For fixed k, let b = k(k-1)/2 and q = floor((N-b)/k). Then:

      contribution(k) = q*(N+1-b) - k*q(q+1)/2

    This routine is used only in self-tests for small N.
    """
    km = k_max_for_n(N)
    t = N  # t = N - b, starting with b=0 for k=1
    total = 0
    for k in range(1, km + 1):
        q = t // k
        # (N+1-b) == (t+1)
        total += q * (t + 1) - k * q * (q + 1) // 2
        t -= k  # since b increases by k each step, N-b decreases by k
    return total


def S_fast_mod(N: int, mod: int = MOD) -> int:
    """
    Optimized modular version of S_fast_exact.

    Micro-optimizations:
      - Maintain t = N - k(k-1)/2 incrementally: t_{k+1} = t_k - k.
      - Maintain t_mod = t % mod incrementally too, avoiding huge % each loop.
      - Avoid total %= mod in the inner loop (use 1-step normalization).
      - Use inv2 = (mod+1)//2 (valid when mod is odd) to handle /2 in modulus.
    """
    if mod % 2 == 0:
        raise ValueError("mod must be odd (so 2 has an inverse modulo mod)")
    inv2 = (mod + 1) // 2

    km = k_max_for_n(N)

    t = N
    t_mod = N % mod

    total = 0
    k = 1
    while k <= km:
        q = t // k
        q_mod = q % mod

        # term1 = q * (t+1)
        x = t_mod + 1
        if x >= mod:
            x -= mod
        term1 = (q_mod * x) % mod

        # term2 = k * (q*(q+1)/2)
        tri = (q_mod * (q_mod + 1)) % mod
        tri = (tri * inv2) % mod
        term2 = (k * tri) % mod  # k < mod for our constraints, but keep % anyway

        total += term1
        if total >= mod:
            total -= mod
        total -= term2
        if total < 0:
            total += mod

        t -= k
        t_mod -= k
        if t_mod < 0:
            t_mod += mod

        k += 1

    return total


def _self_tests() -> None:
    # Values explicitly given in the problem statement
    assert f(10, 3) == 2
    assert f(10, 5) == 0
    assert F(100) == 275
    assert S_fast_exact(100) == 12656

    # Cross-check fast formula vs brute force for small ranges
    for N in range(1, 301):
        assert S_fast_exact(N) == S_bruteforce(N)

    # Modular path sanity: mod result matches exact % mod for small N
    for N in (1, 2, 3, 10, 50, 100, 250, 300):
        assert S_fast_mod(N, MOD) == S_fast_exact(N) % MOD


def main() -> None:
    _self_tests()
    print(S_fast_mod(10**16, MOD))


if __name__ == "__main__":
    main()
