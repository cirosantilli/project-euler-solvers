#!/usr/bin/env python3
"""
Project Euler 602: Product of Head Counts

Key observation:
Let n be the number of friends (excluding Alice) and p be P(Tails), q=1-p.

Let T be the number of times Alice flips Tails before her first Head.
P(T=t) = p^t * q,  t >= 0   (geometric)

If T=t, then each friend flips exactly t times, so each friend's head-count H ~ Binomial(t, q).
Alice's random number is R = Π_{i=1..n} H_i.
By independence (given T=t): E[R | T=t] = Π E[H_i | T=t] = (t*q)^n.

Therefore:
e(n,p) = Σ_{t>=0} p^t q (t q)^n
       = (1-p)^{n+1} Σ_{t>=1} t^n p^t

A classic identity (Eulerian polynomials) says:
Σ_{t>=1} t^n p^t = p * A_n(p) / (1-p)^{n+1}
where A_n(p) is the Eulerian polynomial and its coefficients are Eulerian numbers A(n,k).

So:
e(n,p) = p * A_n(p)
and the coefficient c(n,k) of p^k equals Eulerian(n, k-1).

We compute Eulerian(n,m) with the explicit alternating sum:
A(n,m) = Σ_{j=0..m+1} (-1)^j * C(n+1, j) * (m+1-j)^n    (mod M)

This runs in O(m) time for a single coefficient, using:
- sequential update of binomial coefficients,
- precomputed modular inverses up to m+1,
- fast modular exponentiation (built-in pow).
"""

from array import array

MOD = 1_000_000_007


def eulerian_number(n: int, m: int, mod: int = MOD) -> int:
    """
    Return Eulerian number A(n,m) modulo mod, for 0 <= m <= n-1, using:
        A(n,m) = sum_{j=0..m+1} (-1)^j * C(n+1,j) * (m+1-j)^n
    """
    if n <= 0:
        return 0
    if m < 0 or m >= n:
        return 0

    M = m + 1  # convenient alias for m+1 in the formula

    # Precompute modular inverses up to M+1 using linear recurrence:
    # inv[i] = -(mod//i) * inv[mod%i] (mod mod)
    inv = array("I", [0]) * (M + 2)
    inv[1] = 1
    for i in range(2, M + 2):
        inv[i] = mod - (mod // i) * inv[mod % i] % mod

    comb = 1  # C(n+1, 0)
    res = 0
    n1 = n + 1

    # j goes 0..M inclusive (i.e., 0..m+1)
    for j in range(M + 1):
        base = M - j  # (m+1-j)
        if base:
            term = (comb * pow(base, n, mod)) % mod
            if j & 1:
                res -= term
                if res < 0:
                    res += mod
            else:
                res += term
                if res >= mod:
                    res -= mod
        # update comb -> C(n+1, j+1)
        if j < M:
            comb = (comb * (n1 - j)) % mod
            comb = (comb * inv[j + 1]) % mod

    return res


def c(n: int, k: int, mod: int = MOD) -> int:
    """Coefficient c(n,k) in the problem statement (1-indexed k)."""
    return eulerian_number(n, k - 1, mod)


def main() -> None:
    # Asserts from the problem statement
    assert c(3, 1) == 1
    assert c(3, 2) == 4
    assert c(3, 3) == 1
    assert c(100, 40) == 986_699_437

    # Required answer
    n = 10_000_000
    k = 4_000_000
    print(c(n, k))


if __name__ == "__main__":
    main()
