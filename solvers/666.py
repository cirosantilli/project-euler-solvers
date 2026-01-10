#!/usr/bin/env python3
"""
Project Euler 666 - Polymorphic Bacteria

Compute the extinction probability for a multi-type branching process S_{k,m}.
No external libraries are used.
"""

from __future__ import annotations


def extinction_probability(
    k: int, m: int, eps: float = 1e-14, max_iter: int = 2_000_000
) -> float:
    """
    Return P_{k,m}: probability that the population eventually dies out,
    starting from a single bacterium of type alpha_0.

    The extinction probability vector p (size k) satisfies p = F(p),
    where F is the vector of offspring generating functions.
    The least fixed point is obtained by monotone iteration from p=0.
    """
    if k <= 0 or m <= 0:
        raise ValueError("k and m must be positive integers")

    MOD = 10007
    N = k * m  # we need r_0 ... r_{N-1}

    # Precompute r_n
    r = [0] * N
    r[0] = 306
    for n in range(1, N):
        x = r[n - 1]
        r[n] = (x * x) % MOD

    # For each type i, count how many j in [0,m) yield q in {0..4}.
    a0 = [0.0] * k
    a1 = [0.0] * k
    a2 = [0.0] * k
    a3 = [0.0] * k
    a4 = [0.0] * k

    inv_m = 1.0 / m
    for i in range(k):
        c0 = c1 = c2 = c3 = c4 = 0
        base = i * m
        for j in range(m):
            q = r[base + j] % 5
            if q == 0:
                c0 += 1
            elif q == 1:
                c1 += 1
            elif q == 2:
                c2 += 1
            elif q == 3:
                c3 += 1
            else:
                c4 += 1
        a0[i] = c0 * inv_m
        a1[i] = c1 * inv_m
        a2[i] = c2 * inv_m
        a3[i] = c3 * inv_m
        a4[i] = c4 * inv_m

    # Type transitions
    mutate_to = [(2 * i) % k for i in range(k)]
    split_to = [((i * i) + 1) % k for i in range(k)]
    spawn_to = [(i + 1) % k for i in range(k)]

    # Monotone fixed-point iteration: p^{(t+1)} = F(p^{(t)}), starting at 0.
    p = [0.0] * k
    for _ in range(max_iter):
        max_delta = 0.0
        newp = [0.0] * k
        for i in range(k):
            pi = p[i]
            val = (
                a0[i]
                + a1[i] * (pi * pi)
                + a2[i] * p[mutate_to[i]]
                + a3[i] * (p[split_to[i]] ** 3)
                + a4[i] * (pi * p[spawn_to[i]])
            )
            newp[i] = val
            d = val - pi
            if d < 0:
                d = -d
            if d > max_delta:
                max_delta = d
        p = newp
        if max_delta < eps:
            break
    else:
        raise RuntimeError("Did not converge; try increasing max_iter")

    return p[0]


def solve() -> str:
    # Asserts from the problem statement (rounded to 8 decimals)
    assert f"{extinction_probability(2, 2):.8f}" == "0.07243802"
    assert f"{extinction_probability(4, 3):.8f}" == "0.18554021"
    assert f"{extinction_probability(10, 5):.8f}" == "0.53466253"

    ans = extinction_probability(500, 10)
    return f"{ans:.8f}"


if __name__ == "__main__":
    print(solve())
