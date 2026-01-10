#!/usr/bin/env python3
"""
Project Euler 505: Bidirectional Recurrence (Exact, Derived)

We are given:

x(0)=0, x(1)=1
x(2k)   = (3*x(k) + 2*x(floor(k/2))) mod 2^60
x(2k+1) = (2*x(k) + 3*x(floor(k/2))) mod 2^60

y_n(k)= x(k) if k>=n
y_n(k)= 2^60-1 - max(y_n(2k), y_n(2k+1)) if k<n

A(n)=y_n(1)

Technique:
- Convert to alternating minimax via complement transform (see README).
- Evaluate exactly via Principal Variation Search (PVS) / alpha-beta.
- Compute x-values incrementally along the game tree.

No external libraries.
"""

MOD = 1 << 60
MASK = MOD - 1


def brute_A(n: int) -> int:
    """Brute for small n; used only for sample asserts."""
    x = [0] * (2 * n + 1)
    if 2 * n >= 1:
        x[1] = 1
    for k in range(1, n):
        v = x[k]
        p = x[k // 2]
        a = 2 * k
        x[a] = (3 * v + 2 * p) & MASK
        x[a + 1] = (2 * v + 3 * p) & MASK

    y = [0] * (2 * n)
    for k in range(2 * n - 1, 0, -1):
        if k >= n:
            y[k] = x[k]
        else:
            left = y[2 * k]
            right = y[2 * k + 1]
            y[k] = MASK - (left if left > right else right)
    return y[1]


def A(n: int) -> int:
    """Exact computation of A(n)=y_n(1) using derived minimax + PVS."""
    if n <= 0:
        raise ValueError("n must be positive")
    if n == 1:
        return 1

    d = n.bit_length() - 1  # floor(log2 n)

    # In s-space, a node at depth t uses s=y (even depth) or s=MASK-y (odd depth).
    # Leaves occur at depths d and d+1 in the truncated tree.
    # Therefore:
    # - leaves that are originally at depth d (k>=n at depth d): flipB depends on parity of d
    # - leaves at depth d+1 (children of k<n at depth d): flipA depends on parity of d+1
    flipA = MASK if ((d + 1) & 1) else 0
    flipB = MASK if (d & 1) else 0

    # At depth d, the minimax operator is MIN if d even else MAX (because depth 0 is MIN).
    terminal_is_max = (d & 1) == 1

    _MASK = MASK
    _MOD = MOD
    _n = n
    _flipA = flipA
    _flipB = flipB
    _term_is_max = terminal_is_max

    # Principal Variation Search (PVS) with fixed move ordering: bit=1 first, then bit=0.
    def rec(k: int, depth: int, a: int, b: int, alpha: int, beta: int) -> int:
        # a = x(k), b = x(k//2)
        if depth == d:
            # Terminal evaluation at depth d:
            if k >= _n:
                return a ^ _flipB
            # k < n: its children (2k,2k+1) are leaves at depth d+1
            a0 = (3 * a + 2 * b) & _MASK
            a1 = (2 * a + 3 * b) & _MASK
            v0 = a0 ^ _flipA
            v1 = a1 ^ _flipA
            if _term_is_max:
                return v0 if v0 >= v1 else v1
            else:
                return v0 if v0 <= v1 else v1

        if depth & 1:
            # MAX node
            # First child: bit=1 full window
            a1 = (2 * a + 3 * b) & _MASK
            best = rec((k << 1) | 1, depth + 1, a1, a, alpha, beta)
            if best > alpha:
                alpha = best
            if alpha >= beta:
                return best

            # Second child: bit=0 null window then (maybe) re-search
            a0 = (3 * a + 2 * b) & _MASK
            v = rec(k << 1, depth + 1, a0, a, alpha, alpha + 1)
            if v > alpha and v < beta:
                v = rec(k << 1, depth + 1, a0, a, alpha, beta)
            return v if v > best else best

        else:
            # MIN node
            # First child: bit=1 full window
            a1 = (2 * a + 3 * b) & _MASK
            best = rec((k << 1) | 1, depth + 1, a1, a, alpha, beta)
            if best < beta:
                beta = best
            if alpha >= beta:
                return best

            # Second child: bit=0 null window then (maybe) re-search
            a0 = (3 * a + 2 * b) & _MASK
            v = rec(k << 1, depth + 1, a0, a, beta - 1, beta)
            if v < beta and v > alpha:
                v = rec(k << 1, depth + 1, a0, a, alpha, beta)
            return v if v < best else best

    # Search root: depth 0 is MIN. Values are in [0..MASK].
    return rec(1, 0, 1, 0, -1, _MOD)


def main():
    # Asserts from the problem statement:
    assert A(4) == 8
    assert A(10) == (1 << 60) - 34
    assert A(1000) == 101881

    print(A(10**12))


if __name__ == "__main__":
    main()
