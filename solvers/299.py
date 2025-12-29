#!/usr/bin/env python3

from __future__ import annotations

import math


def count_incenter(limit: int) -> int:
    target = limit - 1  # strict: b + d < limit
    total = 0

    stack = [(3, 4, 5)]  # Berggren root: (odd_leg, even_leg, hypotenuse)
    while stack:
        a, b, c = stack.pop()
        s = a + b
        if s > target:
            continue
        total += target // s

        a1 = a - 2 * b + 2 * c
        b1 = 2 * a - b + 2 * c
        c1 = 2 * a - 2 * b + 3 * c

        a2 = a + 2 * b + 2 * c
        b2 = 2 * a + b + 2 * c
        c2 = 2 * a + 2 * b + 3 * c

        a3 = -a + 2 * b + 2 * c
        b3 = -2 * a + b + 2 * c
        c3 = -2 * a + 2 * b + 3 * c

        if a1 + b1 <= target:
            stack.append((a1, b1, c1))
        if a2 + b2 <= target:
            stack.append((a2, b2, c2))
        if a3 + b3 <= target:
            stack.append((a3, b3, c3))

    # Ordered pairs (b,d) count both leg orders.
    return 2 * total


def count_parallel(limit: int) -> int:
    # strict 2*b < limit  =>  b <= (limit-1)//2
    max_b = (limit - 1) // 2
    total = 0

    gcd = math.gcd
    isqrt = math.isqrt

    umax = isqrt(2 * max_b) + 1
    for u in range(1, umax + 1, 2):  # u odd
        disc = 2 * max_b - u * u
        if disc < 0:
            break
        v_max = (isqrt(disc) - u) // 2
        if v_max < 1:
            continue

        uu = u * u
        for v in range(1, v_max + 1):
            if gcd(u, v) != 1:
                continue
            base_b = uu + 2 * v * v + 2 * u * v  # (u^2+2v^2)+(2uv)
            total += max_b // base_b
    return total


def solve(limit: int = 100_000_000) -> int:
    return count_incenter(limit) + count_parallel(limit)


def _self_test() -> None:
    # Example from the problem statement: (a,b,d) = (2,3,4) has P=(1,1)
    b, d = 3, 4
    s = math.isqrt(b * b + d * d)
    assert s == 5
    a = b + d - s
    assert a == 2
    assert (a // 2, a // 2) == (1, 1)

    # Given test values in the statement
    assert solve(100) == 92
    assert solve(100_000) == 320_471


def main() -> None:
    _self_test()
    print(solve(100_000_000))


if __name__ == "__main__":
    main()
