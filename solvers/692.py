#!/usr/bin/env python3
"""
Project Euler 692: Siegbert and Jo

We define a game on a heap of N pebbles:
- First move: take any number 1..N.
- Later moves: take 1..min(remaining, 2 * previous_take).
- Taking the last pebble wins.

Let H(N) be the smallest first move that guarantees a win if both players
play optimally afterwards.
Let G(n) = sum_{k=1..n} H(k).

This program computes G(23416728348467685).
"""

from bisect import bisect_right


def build_fibs(limit: int) -> list[int]:
    """Fibonacci numbers with F1=1, F2=2 up to the first value > limit."""
    fib = [1, 2]
    while fib[-1] <= limit:
        fib.append(fib[-1] + fib[-2])
    return fib


def smallest_zeckendorf_term(n: int, fib: list[int]) -> int:
    """
    Return the smallest Fibonacci number in the Zeckendorf decomposition of n
    (using Fibonacci numbers starting 1,2,...).
    """
    smallest = 0
    while n:
        i = bisect_right(fib, n) - 1
        smallest = fib[i]
        n -= smallest
    return smallest


def precompute_prefix_before(fib: list[int]) -> list[int]:
    """
    prefix_before[i] = G(fib[i] - 1)

    Recurrence (for i>=1):
      G(F_{i+1}-1) = G(F_i-1) + H(F_i) + G(F_{i-1}-1)
                  = prefix_before[i] + fib[i] + prefix_before[i-1]
    """
    prefix_before = [0] * len(fib)
    prefix_before[0] = 0  # G(0)
    if len(fib) > 1:
        prefix_before[1] = 1  # G(1) = H(1) = 1
    for i in range(1, len(fib) - 1):
        prefix_before[i + 1] = prefix_before[i] + fib[i] + prefix_before[i - 1]
    return prefix_before


def H(n: int) -> int:
    """Compute H(n)."""
    fib = build_fibs(n)
    return smallest_zeckendorf_term(n, fib)


def G(n: int) -> int:
    """Compute G(n) = sum_{k=1..n} H(k) in O(log n) time."""
    if n <= 0:
        return 0

    fib = build_fibs(n)
    prefix_before = precompute_prefix_before(fib)

    memo = {0: 0}

    def rec(x: int) -> int:
        if x in memo:
            return memo[x]
        i = bisect_right(fib, x) - 1  # largest fib[i] <= x
        # G(x) = G(fib[i]-1) + H(fib[i]) + sum_{t=1..x-fib[i]} H(t)
        #      = prefix_before[i] + fib[i] + G(x - fib[i])
        ans = prefix_before[i] + fib[i] + rec(x - fib[i])
        memo[x] = ans
        return ans

    return rec(n)


def _self_test() -> None:
    # Test values from the problem statement:
    assert H(1) == 1
    assert H(4) == 1
    assert H(17) == 1
    assert H(8) == 8
    assert H(18) == 5
    assert G(13) == 43


def main() -> None:
    _self_test()
    n = 23416728348467685
    print(G(n))


if __name__ == "__main__":
    main()
