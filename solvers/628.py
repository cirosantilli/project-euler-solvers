#!/usr/bin/env python3
"""
Project Euler 628: Open Chess Positions

Key result:
    f(n) = (n - 3) * (!n) + 2  (mod M),
where
    !n = sum_{k=0}^{n-1} k!      ("left factorial")
and M = 1008691207.

This file computes f(10^8) modulo M and prints it.

No external libraries are used.
"""

MOD = 1008691207


def left_factorial(n: int, mod: int = MOD) -> int:
    """
    Compute !n = sum_{k=0}^{n-1} k! (mod mod).

    This uses the straightforward recurrence:
        fact = k!  (mod mod)
        sum += fact
    """
    if n <= 0:
        return 0

    fact = 1  # 0!
    s = 1     # sum starts with 0!

    # Add 1!, 2!, ..., (n-1)!
    # Micro-optimization: don't mod-reduce 's' each iteration; it's safe to do once at the end.
    for k in range(1, n):
        fact = (fact * k) % mod
        s += fact

    return s % mod


def f(n: int, mod: int = MOD) -> int:
    """
    Number of open positions for an n x n board, modulo mod.
    """
    lf = left_factorial(n, mod)
    return ((n - 3) % mod) * lf % mod + 2 % mod


def _self_test() -> None:
    # Test values given in the problem statement
    assert f(3, MOD) % MOD == 2
    assert f(5, MOD) % MOD == 70


def main() -> None:
    _self_test()
    n = 10**8
    ans = f(n, MOD) % MOD
    print(ans)


if __name__ == "__main__":
    main()
