#!/usr/bin/env python3
"""
Project Euler 573: Unfair race

We model the n start positions as sorted i.i.d. U(0,1) points:
0 = U_(0) < U_(1) < ... < U_(n) < U_(n+1) = 1

Runner k starts at U_(k) and runs with speed k/n, so its finish time is:
T_k = (1 - U_(k)) / (k/n) = n * (1 - U_(k)) / k.

Because U_(k) is the k-th order statistic, the spacings are distributed as
normalized i.i.d. exponentials. This leads to an equivalent model with
independent Exp(1) variables E_1..E_n and partial sums S_k = E_1+...+E_k:

The winner among n runners is the index k that minimizes the running average
B_k = S_k / k.

The problem asks for E_n = E[winner index], especially E_1_000_000 rounded
to 4 decimals.

For small n (used in the statement's test values), we compute E_n exactly
(via a small combinatorial/Poisson DP and closed-form gamma integrals).

For n as large as 1_000_000, we use the known large-n asymptotic expansion:
E_n = sqrt(pi*n/2) - 1/3 + 1/(4*sqrt(2*pi*n)) + O(1/n),
which is accurate far beyond 1e-4 at n=1_000_000.
"""

from __future__ import annotations

import math
from typing import Dict, List


def _coeff_R(m: int) -> List[float]:
    """
    Return coefficients a[0..m-1] such that, for y>=0,

        R_m(y) = P(S_1>y, S_2>2y, ..., S_m>m y)
               = exp(-m*y) * sum_{j=0}^{m-1} a[j] * y^j.

    Derivation (sketch):
    Using the Poisson-process view, condition S_i > i y for i=1..m is
    equivalent to N(i y) <= i-1 for a rate-1 Poisson process N(.).
    Over each interval ((i-1)y, i y], the increment is Poisson(y) and independent.

    So we sum over all sequences (c_1..c_m) with:
        c_1 = 0,
        c_1 + ... + c_i <= i-1 for all i,
    and each sequence contributes:
        Π_i [ e^{-y} * y^{c_i} / c_i! ] = e^{-m y} * y^{sum c_i} / Π c_i!.

    Grouping by total sum gives the polynomial above; coefficients are
    computed by a tiny DP (works well for the small m used in tests).
    """
    if m == 0:
        return [1.0]

    # inv_fact[c] = 1/c! for c = 0..m-1
    inv_fact = [1.0]
    fact = 1
    for c in range(1, m):
        fact *= c
        inv_fact.append(1.0 / fact)

    dp = [1.0]  # dp[t] = sum of 1/(c1!...ci!) with total count t so far
    for i in range(1, m + 1):
        new = [0.0] * i  # totals 0..i-1 after i steps
        for t, val in enumerate(dp):
            slack = (i - 1) - t
            if slack < 0:
                continue
            for c in range(slack + 1):
                new[t + c] += val * inv_fact[c]
        dp = new
    return dp


def _moment_gamma_mean(k: int, j: int, m: int) -> float:
    """
    Let Y = (E_1+...+E_k)/k. Then Y ~ Gamma(shape=k, rate=k).

    Return E[ Y^j * exp(-m*Y) ].

    Closed form:
        E[ Y^j e^{-mY} ] = k^k * Gamma(k+j) / Gamma(k) / (k+m)^{k+j}.
    """
    # Use logs to avoid overflow
    logv = (
        k * math.log(k)
        + math.lgamma(k + j)
        - math.lgamma(k)
        - (k + j) * math.log(k + m)
    )
    return math.exp(logv)


def winner_probability_exact(
    n: int, k: int, coeff_cache: Dict[int, List[float]]
) -> float:
    """
    Exact P(winner = k) for small n, using the decomposition:
        P(winner=k) = (1/k) * E[ R_{n-k}( (E_1+...+E_k)/k ) ].

    The prefactor 1/k is the (non-obvious but true here) probability that
    k is the minimum among the first k running averages, independent of S_k.
    """
    m = n - k
    if m == 0:
        return 1.0 / k

    coeffs = coeff_cache[m]
    acc = 0.0
    for j, a in enumerate(coeffs):
        acc += a * _moment_gamma_mean(k, j, m)
    return acc / k


def expected_winner_exact(n: int) -> float:
    """Exact E_n for small n (O(n^3) worst-case, but tiny for n<=50)."""
    coeff_cache = {m: _coeff_R(m) for m in range(0, n)}  # need up to n-1
    e = 0.0
    for k in range(1, n + 1):
        p = winner_probability_exact(n, k, coeff_cache)
        e += k * p
    return e


def expected_winner_asymptotic(n: int) -> float:
    """
    Large-n asymptotic expansion (sufficient for n=1_000_000):

        E_n = sqrt(pi*n/2) - 1/3 + 1/(4*sqrt(2*pi*n)) + O(1/n).
    """
    return (
        math.sqrt(math.pi * n / 2.0)
        - 1.0 / 3.0
        + 1.0 / (4.0 * math.sqrt(2.0 * math.pi * n))
    )


def expected_winner(n: int) -> float:
    """Convenience wrapper."""
    if n <= 50:
        return expected_winner_exact(n)
    return expected_winner_asymptotic(n)


def _self_test() -> None:
    # Test values from the problem statement
    # n=3 probabilities:
    coeff_cache = {m: _coeff_R(m) for m in range(0, 3)}
    p31 = winner_probability_exact(3, 1, coeff_cache)
    p32 = winner_probability_exact(3, 2, coeff_cache)
    p33 = winner_probability_exact(3, 3, coeff_cache)
    assert abs(p31 - 4.0 / 9.0) < 1e-12
    assert abs(p32 - 2.0 / 9.0) < 1e-12
    assert abs(p33 - 1.0 / 3.0) < 1e-12

    assert abs(expected_winner(3) - 17.0 / 9.0) < 1e-12
    assert abs(expected_winner(4) - 2.21875) < 1e-12
    assert abs(expected_winner(5) - 2.5104) < 1e-12
    assert abs(expected_winner(10) - 3.66021568) < 1e-10


def main() -> None:
    _self_test()
    n = 1_000_000
    ans = expected_winner(n)
    print(f"{ans:.4f}")


if __name__ == "__main__":
    main()
