#!/usr/bin/env python3
"""
Project Euler 652: Distinct Values of a Proto-logarithmic Function

We compute D(N), the number of distinct values of any proto-logarithmic function g(m,n)
over 2 <= m,n <= N, and output the last 9 digits for N=10^18.

No external libraries are used.
"""

from math import gcd

MOD = 10**9


def integer_kth_root(n: int, k: int) -> int:
    """Return floor(n ** (1/k)) for integers n>=0, k>=1, using binary search (exact)."""
    if k <= 1:
        return n
    if n < 2:
        return n

    # Upper bound: 2^(ceil(bitlen/k)) is guaranteed >= n^(1/k)
    high = 1 << ((n.bit_length() + k - 1) // k)
    low = 1
    while low + 1 < high:
        mid = (low + high) // 2
        if pow(mid, k) <= n:
            low = mid
        else:
            high = mid
    return low


def mobius_upto(n: int):
    """Compute Möbius function μ(1..n) with a linear sieve."""
    mu = [0] * (n + 1)
    mu[1] = 1
    primes = []
    is_comp = [False] * (n + 1)
    for i in range(2, n + 1):
        if not is_comp[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            v = i * p
            if v > n:
                break
            is_comp[v] = True
            if i % p == 0:
                mu[v] = 0
                break
            mu[v] = -mu[i]
    return mu


def totients_prefix(n: int):
    """Return prefix sums of Euler's totient function phi(1..n)."""
    phi = list(range(n + 1))
    for i in range(2, n + 1):
        if phi[i] == i:  # prime
            for j in range(i, n + 1, i):
                phi[j] -= phi[j] // i
    pref = [0] * (n + 1)
    for i in range(1, n + 1):
        pref[i] = pref[i - 1] + phi[i]
    return pref


def primitive_count(x: int, mu) -> int:
    """
    Count integers u with 2 <= u <= x that are NOT perfect powers.

    Uses Möbius inversion on counts of d-th powers:
      F(d) = #{ n in [2..x] : n is a d-th power } = floor(x^(1/d)) - 1
      F(d) = sum_{d|k} G(k), where G(k) is #{ n with maximal power-exponent = k }.
    Then G(1) = sum_{d>=1} mu(d) * F(d).

    So primitive_count(x) = G(1).
    """
    if x < 2:
        return 0
    K = x.bit_length() - 1  # floor(log2 x)
    s = 0
    for d in range(1, K + 1):
        md = mu[d]
        if md == 0:
            continue
        s += md * (integer_kth_root(x, d) - 1)
    return s


def D(N: int) -> int:
    """Compute D(N) exactly as an integer (can be huge)."""
    if N < 2:
        return 0

    L = N.bit_length() - 1  # floor(log2 N)
    mu = mobius_upto(L)
    phisum = totients_prefix(L)

    # Distinct rational values correspond to reduced fractions p/q with 1<=p,q<=L:
    rational = 2 * phisum[L] - 1

    # Precompute floor(N^(1/e)) for e=1..L+1
    rootN = [0] * (L + 2)
    for e in range(1, L + 2):
        rootN[e] = integer_kth_root(N, e)

    # P[e] = number of primitive bases <= floor(N^(1/e))
    P = [0] * (L + 2)
    for e in range(1, L + 2):
        P[e] = primitive_count(rootN[e], mu)

    # count_e = #{ m<=N : maximal power-exponent(m) = e } = P[e]
    count = [0] * (L + 1)
    for e in range(1, L + 1):
        count[e] = P[e]

    # T = total ordered primitive pairs (m,n) with gcd(exp(m),exp(n)) = 1
    T = 0
    for e in range(1, L + 1):
        ce = count[e]
        if ce == 0:
            continue
        for f in range(1, L + 1):
            if gcd(e, f) == 1:
                T += ce * count[f]

    # S = those pairs where m,n share the same primitive root (=> rational), still with gcd(exponents)=1.
    # Group by K = floor(log_u N) (max exponent available for primitive base u).
    S = 0
    for k in range(1, L + 1):
        num_roots_with_K = (
            P[k] - P[k + 1]
        )  # primitive u with N^(1/(k+1)) < u <= N^(1/k)
        coprime_pairs_upto_k = 2 * phisum[k] - 1  # #{(i,j) in [1..k]^2 : gcd(i,j)=1}
        S += num_roots_with_K * coprime_pairs_upto_k

    irrational = T - S
    return rational + irrational


def solve() -> str:
    n = 10**18
    ans = D(n) % MOD
    return f"{ans:09d}"


if __name__ == "__main__":
    # Asserts from the problem statement
    assert D(5) == 13
    assert D(10) == 69
    assert D(100) == 9607
    assert D(10000) == 99959605

    print(solve())
