#!/usr/bin/env python3
"""
Project Euler 400: Fibonacci Tree Game

We model the game with Sprague-Grundy numbers.
Let h(k) be the Grundy value of T(k) when the root is removable.
Let g(k) be the Grundy value of T(k) when the root is poisoned (unremovable).

For a tree with removable root and child Grundy values a, b, every move
changes only one child, and the set of reachable Grundy values contains
all values (x xor b) + 1 for 0 <= x < a and (a xor y) + 1 for 0 <= y < b,
plus 0 for removing the root. The mex of that set is (a xor b) + 1.
Thus for Fibonacci trees:
  h(k) = (h(k-1) xor h(k-2)) + 1
  g(k) = h(k) - 1

We need f(k): number of winning moves in the poisoned-root game on T(k).
A move in the left subtree is winning iff the left subtree is changed to a
removable-root Grundy value equal to h(k-2). Symmetrically for the right.

Let M(k, v) be the number of moves in T(k) (root removable) that yield
a resulting Grundy value v. For v>0 and k>=2:
  M(k, v) = M(k-1, (v-1) xor h(k-2)) + M(k-2, (v-1) xor h(k-1))
Base cases:
  M(0, v) = 0
  M(k, 0) = 1 for k>=1 (remove root)
  M(1, v>0) = 0

We only ever query v in the range [0, max(h)], and the recursion stays
within that range because it only uses XOR with h values (< 2^m).
"""

MOD = 10**18
N = 10000


def main() -> None:
    h = [0] * (N + 1)
    h[1] = 1
    h[2] = 2
    for k in range(3, N + 1):
        h[k] = (h[k - 1] ^ h[k - 2]) + 1

    limit = 1 << (max(h).bit_length())

    # M(0, v) = 0 for all v
    prev2 = [0] * limit
    # M(1, 0) = 1, M(1, v>0) = 0
    prev1 = [0] * limit
    prev1[0] = 1

    f5 = None
    f10 = None
    result = 0

    for k in range(2, N + 1):
        result = (prev1[h[k - 2]] + prev2[h[k - 1]]) % MOD
        if k == 5:
            f5 = result
        elif k == 10:
            f10 = result

        cur = [0] * limit
        cur[0] = 1
        h1 = h[k - 2]
        h2 = h[k - 1]
        p1 = prev1
        p2 = prev2
        c = cur
        for v in range(1, limit):
            c[v] = (p1[(v - 1) ^ h1] + p2[(v - 1) ^ h2]) % MOD

        prev2, prev1 = prev1, cur

    assert f5 == 1
    assert f10 == 17
    print(f"{result:018d}")


if __name__ == "__main__":
    main()
