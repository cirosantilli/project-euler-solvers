#!/usr/bin/env python3
"""Project Euler 672: One More One

We must compute H(10^9) modulo 1_117_117_717.

Process definition:
  - if n == 1: stop
  - if n divisible by 7: n := n/7
  - else: n := n+1 (count a '+1')

Let g(n) = number of '+1' operations until termination.
Let S(N) = sum_{n=1..N} g(n).
Let H(K) = S((7^K - 1)/11).

This file contains a fast solution (O(log K)) with small sanity asserts from the
problem statement.
"""

MOD = 1_117_117_717


# ----------------------------
# Small helpers / test g(n)
# ----------------------------


def g_slow(n: int) -> int:
    """Direct simulation (only for small test values)."""
    if n <= 0:
        raise ValueError("n must be positive")
    adds = 0
    while n != 1:
        if n % 7 == 0:
            n //= 7
        else:
            n += 1
            adds += 1
    return adds


# ----------------------------
# Matrix utilities (4x4)
# ----------------------------


def mat_mul(A, B, mod: int):
    """Multiply two 4x4 matrices modulo mod."""
    res = [[0] * 4 for _ in range(4)]
    for i in range(4):
        Ai = A[i]
        for k in range(4):
            aik = Ai[k]
            if aik == 0:
                continue
            Bk = B[k]
            res[i][0] = (res[i][0] + aik * Bk[0]) % mod
            res[i][1] = (res[i][1] + aik * Bk[1]) % mod
            res[i][2] = (res[i][2] + aik * Bk[2]) % mod
            res[i][3] = (res[i][3] + aik * Bk[3]) % mod
    return res


def mat_pow(M, e: int, mod: int):
    """Fast exponentiation of a 4x4 matrix modulo mod."""
    # identity
    R = [[1 if i == j else 0 for j in range(4)] for i in range(4)]
    while e > 0:
        if e & 1:
            R = mat_mul(M, R, mod)
        M = mat_mul(M, M, mod)
        e >>= 1
    return R


def mat_vec(M, v, mod: int):
    """Multiply 4x4 matrix by length-4 vector modulo mod."""
    return [
        (M[0][0] * v[0] + M[0][1] * v[1] + M[0][2] * v[2] + M[0][3] * v[3]) % mod,
        (M[1][0] * v[0] + M[1][1] * v[1] + M[1][2] * v[2] + M[1][3] * v[3]) % mod,
        (M[2][0] * v[0] + M[2][1] * v[1] + M[2][2] * v[2] + M[2][3] * v[3]) % mod,
        (M[3][0] * v[0] + M[3][1] * v[1] + M[3][2] * v[2] + M[3][3] * v[3]) % mod,
    ]


# ----------------------------
# Core mathematics
# ----------------------------


def one_over_11_base7_period10():
    """Return the repeating base-7 digits of 1/11 with period 10.

    Long division in base 7:
      r_{i+1} = (r_i * 7) mod 11
      digit_i = floor((r_i * 7) / 11)

    For 7 and 11 coprime, the period is 10.
    """
    den = 11
    base = 7
    r = 1 % den
    digits = []
    for _ in range(10):
        r *= base
        digits.append(r // den)
        r %= den
    # Should return to remainder 1 after 10 digits
    if r != 1:
        raise RuntimeError("Unexpected period for 1/11 in base 7")
    return digits


def digit_matrix(r: int, mod: int):
    """Matrix for appending one base-7 digit r to a prefix m (n = 7m + r).

    State vector is [S(m), g(m+1), m, 1]^T.

    Then:
      S(n)     = 7*S(m) + 21*m + r*g(m+1) + c1[r]
      g(n+1)   = g(m+1) + c2[r]
      n        = 7*m + r
      constant = 1

    where:
      c1[r] = -6 + sum_{t=1..r} (7-t) = -6 + 7r - r(r+1)/2
      c2[r] = 6-r for r=0..5, and 0 for r=6

    This compactly reproduces H(10) exactly and scales via matrix powers.
    """
    c1 = (-6 + 7 * r - (r * (r + 1)) // 2) % mod
    c2 = 0 if r == 6 else (6 - r) % mod
    return [
        [7 % mod, r % mod, 21 % mod, c1],
        [0, 1, 0, c2],
        [0, 0, 7 % mod, r % mod],
        [0, 0, 0, 1],
    ]


def H_of_K(K: int, mod: int) -> int:
    """Compute H(K) modulo mod, assuming K is a multiple of 10."""
    if K % 10 != 0:
        raise ValueError("This implementation expects K to be a multiple of 10")

    # Base-7 digits of 1/11 repeat with period 10.
    # For K multiple of 10, N = (7^K - 1)/11 has base-7 digits equal to that
    # period repeated K/10 times. The first digit is 0 (since 1/11 < 1/7), so
    # we drop it to avoid leading-zero complications.
    A = one_over_11_base7_period10()  # e.g. [0,4,3,1,1,6,2,3,5,5]
    if A[0] != 0:
        raise RuntimeError("Unexpected leading digit for 1/11 in base 7")

    # Digits of N without its single leading zero: a left-rotation by 1
    # produces the repeating block.
    B = A[1:] + A[:1]  # [4,3,1,1,6,2,3,5,5,0]

    # Total digits after dropping leading zero: K-1
    total_digits = K - 1
    full_blocks, rem = divmod(total_digits, 10)

    # Build block matrix for B
    M_block = [[1 if i == j else 0 for j in range(4)] for i in range(4)]
    for d in B:
        M_block = mat_mul(digit_matrix(d, mod), M_block, mod)

    v = [0, 0, 0, 1]  # [S(0), g(1), 0, 1]

    if full_blocks:
        v = mat_vec(mat_pow(M_block, full_blocks, mod), v, mod)

    # remaining digits (first 'rem' digits of B)
    for d in B[:rem]:
        v = mat_vec(digit_matrix(d, mod), v, mod)

    return v[0] % mod


def main() -> None:
    # Asserts from the problem statement
    assert g_slow(125) == 8
    assert g_slow(1000) == 9
    assert g_slow(10000) == 21

    # Given value: H(10) = 690409338
    assert H_of_K(10, 10**18) == 690_409_338  # no modulus needed for this size

    # Actual Project Euler query
    ans = H_of_K(10**9, MOD)
    print(ans)


if __name__ == "__main__":
    main()
