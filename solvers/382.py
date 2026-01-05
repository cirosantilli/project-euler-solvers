#!/usr/bin/env python3
"""
Project Euler 382: Generating Polygons

Compute the last 9 digits of f(10^18), where f(n) counts subsets of U_n
that generate at least one (non-self-intersecting) polygon.
"""

MOD = 10**9


def _mat_mul(A, B, mod=MOD):
    """Multiply two square matrices (small fixed size) modulo mod."""
    n = len(A)
    res = [[0] * n for _ in range(n)]
    for i in range(n):
        Ai = A[i]
        for k in range(n):
            a = Ai[k]
            if a:
                Bk = B[k]
                for j in range(n):
                    res[i][j] = (res[i][j] + a * Bk[j]) % mod
    return res


def _mat_pow(M, e, mod=MOD):
    """Fast exponentiation of a square matrix modulo mod."""
    n = len(M)
    # Identity matrix
    R = [[0] * n for _ in range(n)]
    for i in range(n):
        R[i][i] = 1
    while e > 0:
        if e & 1:
            R = _mat_mul(M, R, mod)
        M = _mat_mul(M, M, mod)
        e >>= 1
    return R


def _mat_vec_mul(M, v, mod=MOD):
    """Multiply matrix M by vector v modulo mod."""
    n = len(M)
    out = [0] * n
    for i in range(n):
        s = 0
        Mi = M[i]
        for j in range(n):
            c = Mi[j]
            if c:
                s = (s + c * v[j]) % mod
        out[i] = s
    return out


def _build_transition_matrix():
    """
    State at index i (i>=5):
      [ b_i, b_{i-1}, b_{i-2}, b_{i-3}, b_{i-4}, b_{i-5},
        p_i, p_{i-1}, p_{i-2}, p_{i-3},
        S_i, 1 ]
    where:
      b_i = #subsets of {s1..si} with sum <= s_{i+1}
      p_i = 2^i (mod MOD)
      S_i = sum_{k=0..i} b_k (mod MOD)

    Recurrence (for i>=5, producing b_{i+1}):
      b_{i+1} = 2*b_{i-2} + b_{i-3} - b_{i-5} + 5*p_{i-3} + 1  (mod MOD)
      p_{i+1} = 2*p_i
      S_{i+1} = S_i + b_{i+1}
    """
    n = 12
    M = [[0] * n for _ in range(n)]

    # Row 0: b_{i+1}
    M[0][2] = 2 % MOD
    M[0][3] = 1
    M[0][5] = MOD - 1  # -b_{i-5}
    M[0][9] = 5
    M[0][11] = 1  # +1

    # Shift b's
    M[1][0] = 1
    M[2][1] = 1
    M[3][2] = 1
    M[4][3] = 1
    M[5][4] = 1

    # Powers of two
    M[6][6] = 2
    M[7][6] = 1
    M[8][7] = 1
    M[9][8] = 1

    # Prefix sum S_{i+1} = S_i + b_{i+1}
    M[10][10] = 1
    for j in range(n):
        M[10][j] = (M[10][j] + M[0][j]) % MOD

    # Constant 1 stays 1
    M[11][11] = 1

    return M


# Precomputed b_0..b_5 (derived from small direct counting; see README)
_B_INIT = [1, 2, 4, 6, 11, 20]


def _prefix_sum_b(n):
    """
    Return S_{n-1} = sum_{i=0..n-1} b_i (mod MOD).
    For n<=0 returns 0.
    """
    if n <= 0:
        return 0
    idx = n - 1
    if idx <= 5:
        return sum(_B_INIT[: idx + 1]) % MOD

    # Initial state at i=5
    S5 = sum(_B_INIT) % MOD
    v = [
        _B_INIT[5],
        _B_INIT[4],
        _B_INIT[3],
        _B_INIT[2],
        _B_INIT[1],
        _B_INIT[0],
        pow(2, 5, MOD),
        pow(2, 4, MOD),
        pow(2, 3, MOD),
        pow(2, 2, MOD),
        S5,
        1,
    ]

    M = _build_transition_matrix()
    P = _mat_pow(M, idx - 5, MOD)
    v2 = _mat_vec_mul(P, v, MOD)
    return v2[10] % MOD


def f(n):
    """Return f(n) modulo 1e9 (last 9 digits, without padding)."""
    # f(n) = 2^n - 1 - sum_{k=1..n} g(k)
    # and g(k) = b_{k-1}, so sum_{k=1..n} g(k) = sum_{i=0..n-1} b_i = S_{n-1}.
    bad_without_empty = _prefix_sum_b(n)  # sum of bad non-empty subsets
    return (pow(2, n, MOD) - 1 - bad_without_empty) % MOD


def main():
    # Test values from the problem statement:
    assert f(5) == 7
    assert f(10) == 501
    assert f(25) == 18635853

    n = 10**18
    ans = f(n)
    print(f"{ans:09d}")  # last 9 digits, zero-padded


if __name__ == "__main__":
    main()
