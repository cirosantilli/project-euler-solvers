#!/usr/bin/env python3
"""
Project Euler 505: Bidirectional Recurrence
------------------------------------------

We are given:

x(0)=0, x(1)=1
x(2k)   = (3*x(k) + 2*x(floor(k/2))) mod 2^60
x(2k+1) = (2*x(k) + 3*x(floor(k/2))) mod 2^60

y_n(k)= x(k) if k>=n
y_n(k)= 2^60-1 - max(y_n(2k), y_n(2k+1)) if k<n

A(n)=y_n(1)

This solution derives an O(log n) minimax algorithm (see README.md).

No third-party libraries are used.
"""

MOD = 1 << 60
C = MOD - 1

# Matrices for computing x(k) from bits (mod 2^60).
# If v(k) = [x(k), x(floor(k/2))]^T then:
#   v(2k)   = M0 * v(k)
#   v(2k+1) = M1 * v(k)
M0 = ((3, 2), (1, 0))
M1 = ((2, 3), (1, 0))


def _mat_vec(M, v):
    """2x2 matrix times 2-vector, modulo 2^60."""
    return (
        (M[0][0] * v[0] + M[0][1] * v[1]) % MOD,
        (M[1][0] * v[0] + M[1][1] * v[1]) % MOD,
    )


def x_value(k: int) -> int:
    """Compute x(k) in O(log k) time."""
    if k <= 0:
        return 0
    # v(1) = [x(1), x(0)] = [1, 0]
    v = (1, 0)
    # Walk bits of k from MSB to LSB, skipping the leading 1.
    for i in range(k.bit_length() - 2, -1, -1):
        bit = (k >> i) & 1
        v = _mat_vec(M1 if bit else M0, v)
    return v[0]


def _off_min_root(D: int) -> int:
    """
    Winner offset inside a perfect subtree of depth D (leaf distance D),
    when the node at the top of that subtree is a MIN node and leaf payoffs are x(leaf).

    D=0 => offset 0 (single leaf).
    For D>0:
      - if D even:  (2^(D+1) - 2) / 3   (base-4: 22...2)
      - if D odd:   (2^(D+1) - 1) / 3   (base-4: 11...1)
    """
    if D <= 0:
        return 0
    if D & 1:
        return ((1 << (D + 1)) - 1) // 3
    return ((1 << (D + 1)) - 2) // 3


def _off_x(D: int, root_is_min: bool) -> int:
    """
    Winner offset inside a perfect subtree of depth D when leaf payoffs are x(leaf),
    and the subtree root operator is MIN (root_is_min=True) or MAX (False).
    """
    if root_is_min:
        return _off_min_root(D)
    # If the root is MAX, the winner pattern is the MIN pattern with one fewer level.
    return _off_min_root(D - 1) if D > 0 else 0


def _uniform_eval_A(j0: int, D: int, root_is_min: bool, leaf_depth_even: bool):
    """
    Evaluate a perfect subtree interval fully in region A (j < 2n):
      leaves are heap indices j in [j0, j0+2^D)
      leaf payoff in s-space is:
        - x(j)       if leaf_depth_even
        - C - x(j)   if leaf_depth_odd
    Returns (value, winner_leaf_index_j).
    """
    if leaf_depth_even:
        win = j0 + _off_x(D, root_is_min)
        return x_value(win), win

    # Payoff is C - x(j), which reverses comparisons -> swap MIN<->MAX for winner selection.
    win = j0 + _off_x(D, not root_is_min)
    return (C - x_value(win)) % MOD, win


def _uniform_eval_B(j0: int, D: int, root_is_min: bool, leaf_depth_even: bool):
    """
    Evaluate a perfect subtree interval fully in region B (j >= 2n):
      leaves are heap indices j in [j0, j0+2^D)
      payoff in s-space depends only on u=j//2:
        - C - x(u)   if leaf_depth_even
        - x(u)       if leaf_depth_odd
    Since u repeats twice (for 2u and 2u+1), we can drop the last level when D>=1.
    Returns (value, winner_leaf_index_j) (we choose j=2*u for determinism).
    """
    u0 = j0 // 2

    if D <= 0:
        u = u0
        if leaf_depth_even:
            return (C - x_value(u)) % MOD, j0
        return x_value(u), j0

    D1 = D - 1
    if leaf_depth_even:
        # Payoff is C - x(u): swap MIN<->MAX in winner selection.
        win_u = u0 + _off_x(D1, not root_is_min)
        val = (C - x_value(win_u)) % MOD
    else:
        win_u = u0 + _off_x(D1, root_is_min)
        val = x_value(win_u)

    win_j = 2 * win_u
    return val, win_j


def A(n: int) -> int:
    """Compute A(n)=y_n(1). Runs in O(log n) time."""
    if n <= 0:
        raise ValueError("n must be positive")
    if n == 1:
        return 1

    # Let d=floor(log2 n), m=2^(d+1).
    # All frontier leaves of the original truncated tree lie at depths d or d+1.
    # We 'uniformize' to a complete tree with leaves at depth d+1, i.e. leaf indices j in [m, 2m).
    d = n.bit_length() - 1
    m = 1 << (d + 1)
    D_total = d + 1
    boundary = 2 * n

    # In the s-transform (see README), the leaf payoff depends on parity of the (uniform) leaf depth.
    leaf_depth_even = (D_total & 1) == 0

    memo = {}

    def rec(j0: int, D: int, root_is_min: bool):
        """Return (minimax_value_in_s_space, winner_leaf_index_j) for interval [j0, j0+2^D)."""
        key = (j0, D, root_is_min)
        if key in memo:
            return memo[key]

        length = 1 << D
        end = j0 + length

        if end <= boundary:
            ans = _uniform_eval_A(j0, D, root_is_min, leaf_depth_even)
        elif j0 >= boundary:
            ans = _uniform_eval_B(j0, D, root_is_min, leaf_depth_even)
        else:
            # Mixed: split and recurse.
            if D == 0:
                j = j0
                if j < boundary:
                    ans = _uniform_eval_A(j, 0, root_is_min, leaf_depth_even)
                else:
                    ans = _uniform_eval_B(j, 0, root_is_min, leaf_depth_even)
            else:
                mid = j0 + (length >> 1)
                left_val, left_win = rec(j0, D - 1, not root_is_min)
                right_val, right_win = rec(mid, D - 1, not root_is_min)

                if root_is_min:
                    ans = (
                        (left_val, left_win)
                        if left_val <= right_val
                        else (right_val, right_win)
                    )
                else:
                    ans = (
                        (left_val, left_win)
                        if left_val >= right_val
                        else (right_val, right_win)
                    )

        memo[key] = ans
        return ans

    # Root is depth 0 -> MIN in s-space. At root, s=y, so this is exactly A(n).
    value, _ = rec(m, D_total, True)
    return value


def main() -> None:
    # Asserts from the problem statement:
    assert A(4) == 8
    assert A(10) == (1 << 60) - 34
    assert A(1000) == 101881

    print(A(10**12))


if __name__ == "__main__":
    main()
