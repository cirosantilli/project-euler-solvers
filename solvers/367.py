#!/usr/bin/env python3
"""
Project Euler 367 - Bozo Sort (variant with 3-element shuffle)

We model the process as a symmetric random walk on S_n, stopped when the
identity permutation (sorted sequence) is reached. Averaging over all n!
starting permutations means the start distribution is uniform (stationary).

For a symmetric class-invariant walk on a finite group:
    E_uniform[T_hit(identity)] = sum_{irreps rho != trivial} d_rho^2 / (1 - lambda_rho)

Here lambda_rho is the eigenvalue of the transition operator on irrep rho.
For this problem's step distribution:
    with prob 1/6: do nothing (identity)
    with prob 1/2: apply a random transposition
    with prob 1/3: apply a random 3-cycle

So:
    lambda = 1/6 + (1/2) * r2 + (1/3) * r3
where r2, r3 are normalized character ratios on a transposition and 3-cycle.

We compute r2 and r3 using the Murnaghan–Nakayama rule for cycle types
(2,1^{n-2}) and (3,1^{n-3}) and dimensions via the hook-length formula.
"""

from __future__ import annotations

from fractions import Fraction
from functools import lru_cache
from itertools import combinations
from math import factorial
from typing import Iterable, List, Set, Tuple


Partition = Tuple[int, ...]
Cell = Tuple[int, int]


def gen_partitions(n: int, max_part: int | None = None) -> Iterable[Partition]:
    """Generate all partitions of n as non-increasing tuples."""
    if max_part is None or max_part > n:
        max_part = n
    if n == 0:
        yield ()
        return
    for first in range(min(max_part, n), 0, -1):
        for rest in gen_partitions(n - first, first):
            yield (first,) + rest


def diagram_cells(part: Partition) -> List[Cell]:
    cells: List[Cell] = []
    for r, ln in enumerate(part):
        for c in range(ln):
            cells.append((r, c))
    return cells


@lru_cache(None)
def dim(part: Partition) -> int:
    """Dimension f^part via the hook-length formula."""
    n = sum(part)
    if n == 0:
        return 1
    maxc = max(part) if part else 0
    col_lens = [sum(1 for ln in part if ln > c) for c in range(maxc)]
    prod = 1
    for r, ln in enumerate(part):
        for c in range(ln):
            hook = (ln - c) + (col_lens[c] - r) - 1
            prod *= hook
    return factorial(n) // prod


def remaining_partition(part: Partition, removed: Set[Cell]) -> Partition | None:
    """
    Remove cells and return the remaining partition (left-justified), or None if invalid.
    """
    new: List[int] = []
    for r, ln in enumerate(part):
        remaining_cols = [c for c in range(ln) if (r, c) not in removed]
        if not remaining_cols:
            new_len = 0
        else:
            new_len = max(remaining_cols) + 1
            # Ensure contiguity: remaining cells must be columns 0..new_len-1
            for c in range(new_len):
                if (r, c) in removed:
                    return None
        new.append(new_len)

    # Trim trailing zeros
    while new and new[-1] == 0:
        new.pop()

    # Must be non-increasing row lengths
    for i in range(len(new) - 1):
        if new[i] < new[i + 1]:
            return None

    return tuple(new)


def is_connected(cells: Set[Cell]) -> bool:
    """4-neighbour connectivity."""
    if not cells:
        return False
    start = next(iter(cells))
    stack = [start]
    seen = {start}
    while stack:
        r, c = stack.pop()
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (r + dr, c + dc)
            if nb in cells and nb not in seen:
                seen.add(nb)
                stack.append(nb)
    return len(seen) == len(cells)


def has_2x2(cells: Set[Cell]) -> bool:
    """Border strips cannot contain a 2x2 square."""
    for r, c in cells:
        if (r + 1, c) in cells and (r, c + 1) in cells and (r + 1, c + 1) in cells:
            return True
    return False


def border_strips(part: Partition, k: int) -> List[Tuple[Partition, int]]:
    """
    Enumerate all rim hooks (border strips) of size k removable from `part`.
    Returns list of (remaining_partition, height), where height = (#rows occupied) - 1.
    """
    cells = diagram_cells(part)
    out: List[Tuple[Partition, int]] = []
    for comb in combinations(cells, k):
        strip = set(comb)
        nu = remaining_partition(part, strip)
        if nu is None:
            continue
        if not is_connected(strip):
            continue
        if has_2x2(strip):
            continue
        height = len({r for r, _ in strip}) - 1
        out.append((nu, height))
    return out


def character_cycle_k(part: Partition, k: int) -> int:
    """
    Character chi^part on cycle type (k, 1^{n-k}), using Murnaghan–Nakayama:
        chi = sum_{rim hooks of size k} (-1)^{height} * f^{remaining}
    """
    total = 0
    for nu, height in border_strips(part, k):
        total += (-1) ** height * dim(nu)
    return total


def ratios_transposition_and_3cycle(part: Partition) -> Tuple[Fraction, Fraction]:
    d = dim(part)
    n = sum(part)
    chi2 = character_cycle_k(part, 2) if n >= 2 else d
    chi3 = character_cycle_k(part, 3) if n >= 3 else d
    return Fraction(chi2, d), Fraction(chi3, d)


def expected_steps_variant(n: int) -> Fraction:
    """
    Expected number of 3-element shuffles to reach the identity, starting from uniform over S_n.
    """
    total = Fraction(0, 1)
    for part in gen_partitions(n):
        if part == (n,):  # trivial rep has eigenvalue 1; exclude
            continue
        d = dim(part)
        r2, r3 = ratios_transposition_and_3cycle(part)
        lam = Fraction(1, 6) + Fraction(1, 2) * r2 + Fraction(1, 3) * r3
        total += Fraction(d * d, 1 - lam)
    return total


def expected_steps_transposition_bozo(n: int) -> Fraction:
    """
    Expected number of swaps for the original 'swap two elements' bozo sort,
    starting from uniform over S_n.
    """
    total = Fraction(0, 1)
    for part in gen_partitions(n):
        if part == (n,):
            continue
        d = dim(part)
        r2, _ = ratios_transposition_and_3cycle(part)
        lam = r2  # uniform random transposition
        total += Fraction(d * d, 1 - lam)
    return total


def round_fraction_nearest(x: Fraction) -> int:
    """Round to nearest integer, with .5 rounded up."""
    q, r = divmod(x.numerator, x.denominator)
    return q + (1 if 2 * r >= x.denominator else 0)


def solve() -> int:
    n = 11
    exp_steps = expected_steps_variant(n)
    return round_fraction_nearest(exp_steps)


def _self_test() -> None:
    # Given examples in the problem statement:
    # - Original bozo sort (random transpositions) for n=4: 24.75
    assert expected_steps_transposition_bozo(4) == Fraction(99, 4)
    # - Variant (shuffle 3) for n=4: 27.5
    assert expected_steps_variant(4) == Fraction(55, 2)


if __name__ == "__main__":
    _self_test()
    print(solve())
