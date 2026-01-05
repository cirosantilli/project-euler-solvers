#!/usr/bin/env python3
"""
Project Euler 356 - Largest Roots of Cubic Polynomials

Let a_n be the largest real root of:
    g_n(x) = x^3 - 2^n * x^2 + n

We need the last 8 digits of:
    sum_{n=1..30} floor(a_n ^ 987654321)

No external libraries are used.
"""

from __future__ import annotations


MOD = 10**8
EXP = 987654321


def _mat_mul_3(a: list[list[int]], b: list[list[int]], mod: int) -> list[list[int]]:
    """3x3 matrix multiply (mod mod)."""
    return [
        [
            (a[i][0] * b[0][j] + a[i][1] * b[1][j] + a[i][2] * b[2][j]) % mod
            for j in range(3)
        ]
        for i in range(3)
    ]


def _mat_pow_3(mat: list[list[int]], exp: int, mod: int) -> list[list[int]]:
    """3x3 matrix exponentiation (mod mod)."""
    res = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]  # identity
    base = mat
    e = exp
    while e > 0:
        if e & 1:
            res = _mat_mul_3(res, base, mod)
        base = _mat_mul_3(base, base, mod)
        e //= 2
    return res


def power_sum_mod(n: int, k: int, mod: int = MOD) -> int:
    """
    Let the three roots of x^3 - A x^2 + n = 0 (with A = 2^n) be r1, r2, r3.
    Define S_k = r1^k + r2^k + r3^k. Then S_k is an integer and satisfies:

        S_0 = 3
        S_1 = A
        S_2 = A^2
        S_k = A*S_{k-1} - n*S_{k-3}  (k >= 3)

    This function returns S_k (mod mod) using matrix exponentiation.
    """
    if k == 0:
        return 3 % mod

    A = pow(2, n, mod)

    if k == 1:
        return A
    if k == 2:
        return (A * A) % mod

    # State vector: [S_t, S_{t-1}, S_{t-2}]
    # Transition:
    #   S_{t+1} = A*S_t - n*S_{t-2}
    #   S_t     = 1*S_t + 0 + 0  (shift)
    #   S_{t-1} = 0 + 1*S_{t-1} + 0 (shift)
    # Matrix for V_{t+1} = M * V_t:
    M = [
        [A, 0, (-n) % mod],
        [1, 0, 0],
        [0, 1, 0],
    ]

    # We know V_2 = [S_2, S_1, S_0] = [A^2, A, 3]
    v2 = [(A * A) % mod, A, 3 % mod]

    P = _mat_pow_3(M, k - 2, mod)
    Sk = (P[0][0] * v2[0] + P[0][1] * v2[1] + P[0][2] * v2[2]) % mod
    return Sk


def solve() -> int:
    """
    Using the fact that for n>=2 the other two roots lie in (-1,0) and (0,1),
    their k-th powers are tiny for huge k, so:

        floor(a_n^k) = S_k - 1

    For n=1, one of the other roots is exactly 1; since k is odd here,
    the same identity still gives floor(a_1^k) = S_k - 1.

    We only need results modulo 1e8.
    """
    total = 0
    for n in range(1, 31):
        Sk = power_sum_mod(n, EXP, MOD)
        total = (total + Sk - 1) % MOD
    return total


def _largest_root_bisect(n: int, iters: int = 120) -> float:
    """Bisection for the largest real root of x^3 - 2^n x^2 + n = 0 (testing only)."""
    A = 2.0**n

    def f(x: float) -> float:
        return x * x * x - A * x * x + n

    lo = A - 1.0
    hi = A
    flo = f(lo)
    fhi = f(hi)
    if not (flo <= 0.0 <= fhi):
        # In the unlikely event the bracket is wrong (shouldn't happen for n=2 used below),
        # widen it a bit.
        lo = 0.0
        hi = A
        flo = f(lo)
        fhi = f(hi)
        if not (flo <= 0.0 <= fhi):
            raise ValueError("Failed to bracket the largest root")

    for _ in range(iters):
        mid = (lo + hi) / 2.0
        fm = f(mid)
        if fm <= 0.0:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def _self_test() -> None:
    # Test value given in the problem statement:
    a2 = _largest_root_bisect(2)
    assert abs(a2 - 3.86619826) < 1e-8, a2


if __name__ == "__main__":
    _self_test()
    ans = solve()
    print(f"{ans:08d}")
