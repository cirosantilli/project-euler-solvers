#!/usr/bin/env python3
"""
Project Euler 648 - Skipping Squares

Compute F(1000) mod 1e9.

No external libraries are used.
"""

MOD = 10**9
N = 1000

# We multiply many truncated polynomials mod MOD.
# To avoid O(N^3) Python loops, we use a "big-int packing" trick:
# pack coefficients into base 2^SHIFT digits, multiply integers (fast in CPython),
# then unpack digits. Choose SHIFT so that no carries occur between digits.
SHIFT = 70
BASE = 1 << SHIFT
MASK = BASE - 1


def signed_mod(x: int) -> int:
    """Convert 0..MOD-1 to a small signed representative (useful for asserts)."""
    return x if x < MOD // 2 else x - MOD


def pack_digits(coeffs):
    """Pack little-endian digits into an integer in base 2^SHIFT."""
    v = 0
    for c in reversed(coeffs):
        v = (v << SHIFT) + c
    return v


def mul_trunc(a, b, out_len):
    """
    Multiply two little-endian digit arrays 'a' and 'b' (digits < MOD),
    return the first 'out_len' coefficients of the product, reduced mod MOD.

    Uses base 2^SHIFT packing to exploit CPython's fast big-integer multiplication.
    """
    if out_len <= 0:
        return []
    A = pack_digits(a)
    B = pack_digits(b)
    P = A * B
    out = [0] * out_len
    for i in range(out_len):
        out[i] = (P & MASK) % MOD
        P >>= SHIFT
    return out


def next_v(v_prev1, v_prev2):
    """
    Recurrence for v_k:

        v_k = ρ*v_{k-1} + (1-ρ)*v_{k-2}

    where polynomials are in ρ, truncated to degree N, coefficients mod MOD.

    We represent multiplication by ρ as a one-step degree shift.
    Using (1-ρ)*X = X - ρ*X, we get:
        v_k = v_{k-2} + ρ*(v_{k-1} - v_{k-2})
    """
    v = [0] * (N + 1)
    v[0] = v_prev2[0]  # constant term (ρ * anything has no constant contribution)
    for i in range(N):
        v[i + 1] = (v_prev2[i + 1] + v_prev1[i] - v_prev2[i]) % MOD
    return v


def solve():
    # f(ρ) = sum_{m>=1} P(skip at least m squares)
    # The coefficient array 'a' stores a_k in f(ρ) = Σ a_k ρ^k (mod MOD).
    a = [0] * (N + 1)

    # S_m = P(skip at least m squares). Start with m=1:
    # skip 1^2 happens iff first step is +2, with probability (1-ρ).
    # So S_1(ρ) = 1 - ρ.
    S_offset = 0  # smallest potentially-nonzero degree of S's polynomial in ρ
    S = [0] * (N + 1)
    S[0] = 1
    S[1] = MOD - 1  # -1 mod MOD

    # Add S_1 into f
    for i, c in enumerate(S):
        a[i] = (a[i] + c) % MOD

    # v_0 and v_1 for the per-square "skip probability" recurrence.
    v_prev2 = [0] * (N + 1)  # v_0
    v_prev1 = S[:]  # v_1 = 1 - ρ

    # For square j^2 (j>=2), after skipping (j-1)^2 we are deterministically at (j-1)^2+1,
    # which is exactly 2(j-1) below j^2. Let b_n(ρ) be the probability of skipping
    # a square when starting at distance 2n below it. Then b_n = v_{2n}.
    #
    # We iterate k=2..2N, computing v_k. Each time k is even (k=2n), we have b_n = v_k,
    # and we update S_{n+1} = S_n * b_n, adding into f.
    for k in range(2, 2 * N + 1):
        vk = next_v(v_prev1, v_prev2)
        v_prev2, v_prev1 = v_prev1, vk

        if k % 2 != 0:
            continue

        # n = k//2, factor is b_n = v_{2n}
        b = vk

        # Current S corresponds to "skip at least n squares", and has minimum degree n-1.
        # After multiplying by b_n (which has no constant term), S becomes "skip at least n+1 squares"
        # and its minimum degree increases by 1.
        maxdeg_factor = N - S_offset  # maximum degree needed from b_n
        factor = b[
            1 : maxdeg_factor + 1
        ]  # degrees 1..maxdeg_factor (length = maxdeg_factor)

        new_offset = S_offset + 1
        out_len = N - new_offset + 1  # number of degrees we still care about
        # For degrees <= N, we only need S coefficients up to degree N-1 (relative to S_offset).
        left = S[S_offset : S_offset + out_len]  # length out_len
        right = factor[:out_len]  # length out_len

        prod = mul_trunc(left, right, out_len)

        S_offset = new_offset
        # Rebuild S as full-length array for the next iteration (cheap, N=1000).
        S = [0] * S_offset + prod + [0] * (N - (S_offset + len(prod)) + 1)

        # Add S_{n+1} into f
        for i, c in enumerate(prod):
            a[S_offset + i] = (a[S_offset + i] + c) % MOD

    # Assertions from the problem statement
    assert signed_mod(a[0]) == 1
    assert signed_mod(a[1]) == 0
    assert signed_mod(a[5]) == -18
    assert signed_mod(a[10]) == 45176

    # F(n) = sum_{k=0}^n a_k
    F10 = sum(a[:11]) % MOD
    assert F10 == 53964

    F50 = sum(a[:51]) % MOD
    assert F50 == 842418857

    # Requested answer
    return sum(a[: N + 1]) % MOD


if __name__ == "__main__":
    print(solve())
