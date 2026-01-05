#!/usr/bin/env python3
"""
Project Euler 391

We compute M(n) for n=1..1000 and output sum_{n=1..1000} M(n)^3.

No external libraries used.
"""

from typing import List, Optional, Union

# A "mapping" represents a function f: {0..N} -> {0..N}
#   None        : identity mapping (f(s)=s)
#   int         : constant mapping (f(s)=c)
#   list[int]   : explicit table of length N+1


Mapping = Union[None, int, List[int]]


def _const_value(table: List[int]) -> Optional[int]:
    """If table is constant, return that constant; else None."""
    first = table[0]
    for x in table[1:]:
        if x != first:
            return None
    return first


def _apply_map(m: Mapping, s: int) -> int:
    """Apply mapping m to input s."""
    if m is None:
        return s
    if isinstance(m, int):
        return m
    return m[s]


def _compose(A: Mapping, B: Mapping, N: int) -> Mapping:
    """
    Return composition A ∘ B: s -> A(B(s)), over s in [0..N].
    """
    # If A is constant, result is constant (A ignores its input).
    if isinstance(A, int):
        return A

    # If B is constant, the whole composition is A(constant) -> constant
    if isinstance(B, int):
        return _apply_map(A, B)

    # Identity shortcuts
    if A is None:
        return B
    if B is None:
        return A

    # Both are tables
    # out[s] = A[B[s]]
    return [A[x] for x in B]


def M(n: int) -> int:
    """
    Compute M(n): the largest winning first move for the described game.

    Technique:
      - Reduce to scanning a popcount-derived sequence with an "overflow resets to 0" accumulator.
      - Use divide-and-conquer structure of popcount sequences to build block transforms.
      - Stop early once the transform becomes constant (saturation), which happens quickly for n<=1000.
    """
    N = n

    # Empirically (and safely for n<=1000) saturation occurs well below 40 levels.
    # Using 40 gives plenty of safety margin while staying fast.
    MAX_K = 40
    WIDTH = MAX_K + 2  # we index off up to MAX_K+1 because of off+1 in recurrence

    # Base level k=0 maps for offsets off=0..MAX_K+1
    # For k=0 the sequence length is 1 and the value is "off" (since popcount(0)=0).
    maps_prev: List[Mapping] = [0] * WIDTH
    maps_prev[0] = None  # identity for off=0

    for off in range(1, WIDTH):
        if off > N:
            maps_prev[off] = 0
        else:
            lim = N - off
            table = [0] * (N + 1)
            # For s <= lim: s+off <= N, so it becomes s+off; else reset to 0.
            for s in range(lim + 1):
                table[s] = s + off
            maps_prev[off] = table

    # Build k=1.. until saturation of (k,off=0)
    for _k in range(1, MAX_K + 1):
        maps_curr: List[Mapping] = [0] * WIDTH
        for off in range(WIDTH - 1):
            maps_curr[off] = _compose(maps_prev[off], maps_prev[off + 1], N)
        maps_curr[WIDTH - 1] = 0  # not used except as a safe boundary

        root = maps_curr[0]
        if not isinstance(root, int) and root is not None:
            c = _const_value(root)
            if c is not None:
                maps_curr[0] = c
                root = c

        if isinstance(root, int):
            return root

        maps_prev = maps_curr

    # Should not happen for n<=1000 with MAX_K=40
    raise RuntimeError(f"No saturation reached for n={n}. Increase MAX_K.")


def solve() -> int:
    total = 0
    for n in range(1, 1001):
        x = M(n)
        total += x * x * x
    return total


def _tests() -> None:
    # Asserts required by the prompt: sample values from the problem statement
    assert M(2) == 2
    assert M(7) == 1
    assert M(20) == 4

    s = 0
    for n in range(1, 21):
        x = M(n)
        s += x * x * x
    assert s == 8150


if __name__ == "__main__":
    _tests()
    print(solve())
