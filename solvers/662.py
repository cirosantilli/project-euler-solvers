#!/usr/bin/env python3
"""
Project Euler 662: Fibonacci Paths

Alice can step from (a,b) to (a+x, b+y) when:
  - x >= 0, y >= 0
  - sqrt(x^2 + y^2) is a Fibonacci number (1,2,3,5,8,...)

We compute F(W,H) modulo 1_000_000_007.

Notes:
- No external libraries are used.
- Test values from the problem statement are asserted.
"""

from array import array
from math import isqrt

MOD = 1_000_000_007


def fibs_upto(n: int) -> list[int]:
    """Return Fibonacci numbers starting with 1,2 up to n (inclusive)."""
    if n < 1:
        return []
    fibs = [1, 2]
    while fibs[-1] + fibs[-2] <= n:
        fibs.append(fibs[-1] + fibs[-2])
    return fibs


def step_vectors(W: int, H: int) -> list[tuple[int, int]]:
    """
    Enumerate all step vectors (dx,dy) with 0<=dx<=W, 0<=dy<=H, not both 0,
    such that sqrt(dx^2+dy^2) is a Fibonacci number.
    """
    max_len = isqrt(W * W + H * H)
    fibs = fibs_upto(max_len)

    steps = set()
    for f in fibs:
        ff = f * f
        # dx beyond min(f,W) can't work since dx^2 <= f^2
        lim = min(f, W)
        for dx in range(lim + 1):
            dy2 = ff - dx * dx
            dy = isqrt(dy2)
            if dy * dy == dy2 and dy <= H:
                if dx or dy:
                    steps.add((dx, dy))
    return sorted(steps)


def count_paths(W: int, H: int, mod: int = MOD) -> int:
    """
    Dynamic programming over the W x H grid, using a rolling buffer on y.

    dp[y][x] = number of paths to (x,y)
    dp[y][x] = sum_{(dx,dy) in steps, x>=dx, y>=dy} dp[y-dy][x-dx], with dp[0][0]=1.
    """
    if W < 0 or H < 0:
        return 0
    if W == 0 and H == 0:
        return 1

    steps = step_vectors(W, H)

    # Split out dy==0 steps to allow in-row dependencies (horizontal-only moves)
    horiz = []
    other = []
    max_dy = 0
    for dx, dy in steps:
        if dy == 0:
            horiz.append(dx)
        else:
            other.append((dx, dy))
            if dy > max_dy:
                max_dy = dy

    # Rolling buffer: store rows for y % (max_dy+1)
    buf = max_dy + 1
    # Each row is an array('I') to keep memory lower than Python int lists.
    buffer = [array('I', [0]) * (W + 1) for _ in range(buf)]

    for y in range(H + 1):
        idx = y % buf
        row = buffer[idx]

        # reset this row to 0
        for x in range(W + 1):
            row[x] = 0

        for x in range(W + 1):
            val = 1 if (x == 0 and y == 0) else 0

            # horizontal (dy=0) steps depend on current row values
            for dx in horiz:
                if x >= dx:
                    val += row[x - dx]

            # steps with dy>0 read from earlier rows in the ring buffer
            for dx, dy in other:
                if y >= dy and x >= dx:
                    val += buffer[(y - dy) % buf][x - dx]

            row[x] = val % mod

    return int(buffer[H % buf][W])


def main() -> None:
    # Given test values
    assert count_paths(3, 4) == 278
    assert count_paths(10, 10) == 215846462

    # Required output (do not hardcode/assert the final answer)
    W = 10_000
    H = 10_000
    print(count_paths(W, H) % MOD)


if __name__ == "__main__":
    main()
