#!/usr/bin/env python3
"""
Project Euler 463: A Weird Recurrence Relation

We need S(n) = sum_{i=1..n} f(i) for n = 3^37, and output the last 9 digits.

Key idea:
- Introduce g(k) = f(2k+1) and a 2D state v(k) = [f(k), g(k)]^T.
- Derive linear transitions for appending a binary digit:
    v(2k)   = M0 * v(k),   M0 = [[ 1, 0],
                                [-1, 2]]
    v(2k+1) = M1 * v(k),   M1 = [[ 0, 1],
                                [-2, 3]]
- Then f(k) is the first component of v(k).

For sums over a full aligned block of size 2^d:
- The block [k*2^d, (k+1)*2^d - 1] corresponds to appending all d-bit suffixes to k.
- Summing f over all suffixes gives:
    sum_{x=0..2^d-1} f(k*2^d + x) = [1,0] * (M0+M1)^d * v(k)
  where A = M0 + M1 = [[1,1],[-3,5]].

Finally:
- Decompose [1..N] into O(log N) aligned power-of-two blocks and add each block sum.
"""

MOD = 1_000_000_000  # last 9 digits


def mat_mul(X, Y):
    """2x2 matrix multiplication modulo MOD."""
    return (
        (
            (X[0][0] * Y[0][0] + X[0][1] * Y[1][0]) % MOD,
            (X[0][0] * Y[0][1] + X[0][1] * Y[1][1]) % MOD,
        ),
        (
            (X[1][0] * Y[0][0] + X[1][1] * Y[1][0]) % MOD,
            (X[1][0] * Y[0][1] + X[1][1] * Y[1][1]) % MOD,
        ),
    )


def mat_pow(M, e):
    """2x2 matrix exponentiation modulo MOD."""
    # Identity
    R = ((1, 0), (0, 1))
    B = (
        (M[0][0] % MOD, M[0][1] % MOD),
        (M[1][0] % MOD, M[1][1] % MOD),
    )
    while e > 0:
        if e & 1:
            R = mat_mul(R, B)
        B = mat_mul(B, B)
        e >>= 1
    return R


# Transition matrices (mod handled during operations)
M0 = ((1, 0), (-1, 2))
M1 = ((0, 1), (-2, 3))
A = (
    (M0[0][0] + M1[0][0], M0[0][1] + M1[0][1]),
    (M0[1][0] + M1[1][0], M0[1][1] + M1[1][1]),
)  # A = M0 + M1 = [[1,1],[-3,5]]


def vk(k):
    """
    Return v(k) = (f(k), g(k)) mod MOD, where g(k)=f(2k+1).
    Works for k>=1.

    Uses the binary representation of k:
    starting from v(1) = (f(1), g(1)) = (1, f(3)=3),
    then appending each next bit applies M0 or M1.
    """
    if k == 1:
        return 1, 3

    a, b = 1, 3  # v(1)
    # Skip leading '1' in binary; process remaining bits MSB->LSB
    for ch in bin(k)[3:]:
        if ch == "0":
            # v <- M0*v : (a, b) -> (a, -a + 2b)
            a, b = a, (-a + 2 * b) % MOD
        else:
            # v <- M1*v : (a, b) -> (b, -2a + 3b)
            a, b = b, (-2 * a + 3 * b) % MOD
    return a % MOD, b % MOD


def f_value(n):
    """Compute f(n) mod MOD (n>=1)."""
    if n == 1:
        return 1
    a, b = 1, 3  # v(1)
    for ch in bin(n)[3:]:
        if ch == "0":
            a, b = a, (-a + 2 * b) % MOD
        else:
            a, b = b, (-2 * a + 3 * b) % MOD
    return a % MOD


def sum_interval(k, d):
    """
    Sum of f over the aligned block:
      [k*2^d, k*2^d + 2^d - 1], with k>=1 and d>=0.
    """
    a, b = vk(k)
    P = mat_pow(A, d)  # A^d
    r0, r1 = P[0]  # [1,0] * A^d is the first row of A^d
    return (r0 * a + r1 * b) % MOD


def S(n):
    """Compute S(n) = sum_{i=1..n} f(i) mod MOD for n>=1."""
    res = 0
    pos = 1
    while pos <= n:
        remaining = n - pos + 1

        # Largest block size 2^d aligned at pos:
        # - d <= trailing_zeros(pos) to keep pos divisible by 2^d
        # - 2^d <= remaining
        tz = (pos & -pos).bit_length() - 1
        d = min(tz, remaining.bit_length() - 1)

        size = 1 << d
        k = pos >> d  # because pos = k*2^d
        res = (res + sum_interval(k, d)) % MOD
        pos += size
    return res


def main():
    # Asserts for the values given in the problem statement
    assert f_value(1) == 1
    assert f_value(3) == 3
    assert S(8) == 22
    assert S(100) == 3604

    n = 3**37
    ans = S(n)
    print(f"{ans:09d}")


if __name__ == "__main__":
    main()
