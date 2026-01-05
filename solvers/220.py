#!/usr/bin/env python3
"""
Project Euler 220 - Heighway Dragon

Compute the cursor position after a given number of forward-steps in D_n without
building the exponentially large instruction string.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, List


# Directions: 0=up, 1=right, 2=down, 3=left
DIR_VECS = [(0, 1), (1, 0), (0, -1), (-1, 0)]


def rot_cw(x: int, y: int, k: int) -> Tuple[int, int]:
    """Rotate vector (x,y) by k quarter-turns clockwise."""
    k &= 3
    if k == 0:
        return x, y
    if k == 1:
        return y, -x
    if k == 2:
        return -x, -y
    # k == 3
    return -y, x


@dataclass(frozen=True)
class Transform:
    """Effect of executing a fully-expanded symbol sequence."""

    steps: int  # number of 'F' moves
    dx: int  # displacement in local frame (facing up)
    dy: int
    rot: int  # net rotation in quarter-turns clockwise (mod 4)

    def apply(self, pos: Tuple[int, int], d: int) -> Tuple[Tuple[int, int], int]:
        """Apply this transform from a given global position and direction."""
        gx, gy = rot_cw(self.dx, self.dy, d)
        x, y = pos
        return (x + gx, y + gy), (d + self.rot) & 3


def compose(t1: Transform, t2: Transform) -> Transform:
    """
    Return the transform of executing t1 followed by t2, both expressed in the
    same local frame.
    """
    rx, ry = rot_cw(t2.dx, t2.dy, t1.rot)
    return Transform(
        steps=t1.steps + t2.steps,
        dx=t1.dx + rx,
        dy=t1.dy + ry,
        rot=(t1.rot + t2.rot) & 3,
    )


# Terminal transforms (local frame assumes direction 0=up)
T_F = Transform(steps=1, dx=0, dy=1, rot=0)
T_L = Transform(steps=0, dx=0, dy=0, rot=3)  # -1 mod 4
T_R = Transform(steps=0, dx=0, dy=0, rot=1)
T_NOOP = Transform(steps=0, dx=0, dy=0, rot=0)


def build_transforms(max_n: int) -> Tuple[List[Transform], List[Transform]]:
    """
    Precompute transforms for expanding 'a' and 'b' after n rewrites.

    Rules:
      a -> a R b F R
      b -> L F a L b

    When interpreting the final string, 'a' and 'b' are ignored (no-op).
    """
    A = [T_NOOP] * (max_n + 1)  # A[n] is transform for expanding 'a' n times
    B = [T_NOOP] * (max_n + 1)  # B[n] is transform for expanding 'b' n times

    for n in range(1, max_n + 1):
        # A(n) = A(n-1) R B(n-1) F R
        t = A[n - 1]
        t = compose(t, T_R)
        t = compose(t, B[n - 1])
        t = compose(t, T_F)
        t = compose(t, T_R)
        A[n] = t

        # B(n) = L F A(n-1) L B(n-1)
        t = T_L
        t = compose(t, T_F)
        t = compose(t, A[n - 1])
        t = compose(t, T_L)
        t = compose(t, B[n - 1])
        B[n] = t

    return A, B


def exec_prefix(
    sym: str,
    n: int,
    k: int,
    pos: Tuple[int, int],
    d: int,
    A: List[Transform],
    B: List[Transform],
) -> Tuple[Tuple[int, int], int, int]:
    """
    Execute a prefix of the expansion of `sym` (at rewrite depth `n`) that consumes
    up to `k` forward-steps ('F'). Returns (pos, d, k_remaining).

    Important detail:
      - Turns ('L'/'R') consume 0 steps, but MUST still be executed as long as we
        haven't already consumed all k steps (k>0).
    """
    if k == 0:
        return pos, d, k

    # Terminals
    if sym == "F":
        x, y = pos
        vx, vy = DIR_VECS[d]
        return (x + vx, y + vy), d, k - 1
    if sym == "L":
        return pos, (d + 3) & 3, k
    if sym == "R":
        return pos, (d + 1) & 3, k

    # Nonterminals: 'a' / 'b'
    if n == 0:
        return pos, d, k  # ignored

    total_steps = A[n].steps if sym == "a" else B[n].steps
    if k >= total_steps:
        # Execute whole segment in O(1)
        t = A[n] if sym == "a" else B[n]
        pos, d = t.apply(pos, d)
        return pos, d, k - total_steps

    # Need partial execution: traverse the production at depth n
    if sym == "a":
        seq = [("a", n - 1), ("R", 0), ("b", n - 1), ("F", 0), ("R", 0)]
    else:
        seq = [("L", 0), ("F", 0), ("a", n - 1), ("L", 0), ("b", n - 1)]

    for s, nn in seq:
        pos, d, k = exec_prefix(s, nn, k, pos, d, A, B)
        if k == 0:
            break
    return pos, d, k


def position_after(n: int, steps: int) -> Tuple[int, int]:
    """
    Position after `steps` forward-moves in D_n.

    D_0 = "Fa"
    D_{n} is obtained by applying the rewrite rules n times to D_0.
    """
    if steps < 0:
        raise ValueError("steps must be >= 0")

    # In D_n, the only rewritable symbol from D_0 is the trailing 'a'.
    # We execute: "F" then the n-times expansion of "a".
    A, B = build_transforms(n)
    pos = (0, 0)
    d = 0  # up
    k = steps

    pos, d, k = exec_prefix("F", 0, k, pos, d, A, B)
    pos, d, k = exec_prefix("a", n, k, pos, d, A, B)

    if k != 0:
        raise ValueError("Requested more steps than exist in D_n.")
    return pos


def solve() -> str:
    x, y = position_after(50, 10**12)
    return f"{x},{y}"


if __name__ == "__main__":
    # Test value from the problem statement:
    assert position_after(10, 500) == (18, 16)

    print(solve())
