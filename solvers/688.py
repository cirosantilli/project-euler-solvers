#!/usr/bin/env python3
"""
Project Euler 688: Piles of Plates

No external libraries are used.

Running this file prints S(10^16) modulo 1_000_000_007.
"""

from math import isqrt

MOD = 1_000_000_007
INV2 = (MOD + 1) // 2  # modular inverse of 2 mod MOD, since MOD is prime and odd


def k_max_for_n(n: int) -> int:
    """Largest k with 1+2+...+k <= n, i.e. k(k+1)/2 <= n."""
    # k = floor((sqrt(1+8n)-1)/2)
    return (isqrt(1 + 8 * n) - 1) // 2


def f(n: int, k: int) -> int:
    """f(n,k) as defined in the problem."""
    # Minimum sum for k distinct positive piles is 1+2+...+k = k(k+1)/2
    if n < k * (k + 1) // 2:
        return 0
    # With smallest pile m, minimal configuration is m, m+1, ..., m+k-1
    # Sum = k*m + k(k-1)/2 <= n  =>  m <= (n - k(k-1)/2)/k
    return (n - k * (k - 1) // 2) // k


def F(n: int) -> int:
    """F(n) = sum_{k>=1} f(n,k)."""
    km = k_max_for_n(n)
    total = 0
    for k in range(1, km + 1):
        total += f(n, k)
    return total


def S_bruteforce(n: int) -> int:
    """S(n) = sum_{i=1..n} F(i). For small n only."""
    total = 0
    for i in range(1, n + 1):
        total += F(i)
    return total


def S_fast(n: int, mod: int = MOD) -> int:
    """
    Computes S(n) modulo mod using the transformed double-sum:

    S(n) = sum_{k>=1} sum_{m>=1, k*m + k(k-1)/2 <= n} (n + 1 - (k*m + k(k-1)/2))

    For fixed k, q = floor((n - k(k-1)/2) / k) = f(n,k), and:

    contribution(k) = q*(n + 1 - k(k-1)/2) - k*q*(q+1)/2.
    """
    km = k_max_for_n(n)

    n1_mod = (n + 1) % mod
    ans = 0

    # b = k(k-1)/2 (triangular number), maintained incrementally.
    b = 0
    b_mod = 0

    for k in range(1, km + 1):
        q = (n - b) // k  # q = f(n,k) for the top bound n

        # term = q*(n+1-b) - k*q*(q+1)/2
        q_mod = q % mod
        term1 = q_mod * ((n1_mod - b_mod) % mod) % mod
        term2 = (k % mod) * q_mod % mod * ((q + 1) % mod) % mod * INV2 % mod
        ans = (ans + term1 - term2) % mod

        # advance b for next k: b_{k+1} = b_k + k
        b += k
        b_mod = (b_mod + k) % mod

    return ans


def _self_tests() -> None:
    # Test values from the problem statement
    assert f(10, 3) == 2
    assert f(10, 5) == 0
    assert F(100) == 275
    assert S_bruteforce(100) == 12656

    # Cross-check the fast summation against brute force for small n
    for n in (1, 2, 3, 10, 50, 100):
        assert S_fast(n, mod=10**18) == S_bruteforce(n)  # exact check with huge "mod"


def main() -> None:
    _self_tests()
    n = 10**16
    print(S_fast(n, MOD))


if __name__ == "__main__":
    main()
