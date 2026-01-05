#!/usr/bin/env python3
"""Project Euler 253: Tidying Up A

We have a line of N positions (pieces 1..N in the final caterpillar).
Pieces are picked up in a random order (i.e., a random permutation), and each
picked piece is placed into its correct position.

At any time, the set of placed positions decomposes into contiguous segments.
Let M be the maximum number of segments encountered during the whole process.

Goal: For N = 40, compute the average value of M, rounded to 6 decimals.

Key observation (state compression)
---------------------------------
The future evolution depends only on the lengths of the *gaps* of unplaced
positions, not on the exact positions.

If there is at least one segment, the unplaced positions form:
- Two edge gaps (to the left of the leftmost segment, and to the right of the
  rightmost segment), with lengths e0 and e1.
- A multiset of internal gaps between neighboring segments, each with length >= 1.

The segment lengths themselves do not matter, only the gap lengths.
Therefore, we can represent a state as:
  (min_edge, max_edge, sorted_tuple_of_internal_gaps)
with edge gaps stored unordered (min<=max) and internal gaps stored as a sorted
multiset.

Dynamic programming
------------------
We count, exactly, how many permutations produce each (state, current_max) after
k placements. Transitions are enumerated by choosing the next placed piece
uniformly among remaining empty positions; in the DP, this corresponds to
multiplying by the number of empty positions that lead to the same next state.

At the end (all pieces placed), we have an exact distribution of M.
"""

from __future__ import annotations

from bisect import bisect_left
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP, getcontext
from math import factorial
from typing import DefaultDict, Dict, List, Optional, Tuple

# State representation
# - Empty (no segments yet): state is None
# - Otherwise: state = (e0, e1, internal_gaps_tuple) with e0 <= e1
State = Optional[Tuple[int, int, Tuple[int, ...]]]


def _canon_edges(a: int, b: int) -> Tuple[int, int]:
    return (a, b) if a <= b else (b, a)


def _remove_one(t: Tuple[int, ...], x: int) -> Tuple[int, ...]:
    """Remove one occurrence of x from sorted tuple t."""
    i = bisect_left(t, x)
    return t[:i] + t[i + 1 :]


def _insert_one(t: Tuple[int, ...], x: int) -> Tuple[int, ...]:
    """Insert x into sorted tuple t, returning a new sorted tuple."""
    i = bisect_left(t, x)
    return t[:i] + (x,) + t[i:]


def _segments(state: State) -> int:
    if state is None:
        return 0
    return len(state[2]) + 1


def _initial_transitions(n: int) -> List[Tuple[State, int]]:
    """Transitions from the empty state (no pieces placed yet)."""
    mult: Dict[State, int] = defaultdict(int)
    for p in range(n):
        left = p
        right = n - 1 - p
        e0, e1 = _canon_edges(left, right)
        st: State = (e0, e1, ())
        mult[st] += 1
    return list(mult.items())


_TRANS_CACHE: Dict[Tuple[int, int, Tuple[int, ...]], List[Tuple[State, int]]] = {}


def _transitions(state: Tuple[int, int, Tuple[int, ...]]) -> List[Tuple[State, int]]:
    """Enumerate all next states and their multiplicities (number of choices).

    Multiplicity counts how many empty positions in the current configuration
    yield the same next compressed state.
    """
    if state in _TRANS_CACHE:
        return _TRANS_CACHE[state]

    e0, e1, internal = state
    out: DefaultDict[State, int] = defaultdict(int)

    # Internal gaps: multiset in 'internal'
    # Process each distinct length once (with its multiplicity).
    i = 0
    L = len(internal)
    while i < L:
        g = internal[i]
        j = i
        while j < L and internal[j] == g:
            j += 1
        count = j - i

        base_removed = _remove_one(internal, g)

        if g == 1:
            # Only one position: placing it merges two segments => remove this gap
            out[(e0, e1, base_removed)] += count
        else:
            # Place at either end: extends a segment, gap shrinks by 1
            out[(e0, e1, _insert_one(base_removed, g - 1))] += count * 2

            # Place inside (not ends): creates a new segment, splitting the gap
            # Choose split sizes a and b (unordered), a+b = g-1, a>=1, b>=1
            # Multiplicity: 2 if a!=b (two symmetric positions), else 1
            for a in range(1, g - 1):
                b = (g - 1) - a
                if a > b:
                    break
                mult = count * (1 if a == b else 2)
                new_internal = _insert_one(_insert_one(base_removed, a), b)
                out[(e0, e1, new_internal)] += mult

        i = j

    # Edge gaps: two gaps with lengths e0 and e1, unordered.
    if e0 == e1:
        edge_groups = [(e0, 2, e0)]  # (gap_len, how_many_edges, other_edge_len)
    else:
        edge_groups = [(e0, 1, e1), (e1, 1, e0)]

    for g, how_many, other in edge_groups:
        if g == 0:
            continue

        # Place next to the segment on this edge: extends it, edge gap shrinks
        ne0, ne1 = _canon_edges(g - 1, other)
        out[(ne0, ne1, internal)] += how_many

        # Place not adjacent to the segment: creates a new segment.
        # edge_new = boundary side length, internal_gap = g - edge_new - 1
        for edge_new in range(0, g - 1):
            internal_gap = g - edge_new - 1
            ne0, ne1 = _canon_edges(edge_new, other)
            new_internal = _insert_one(internal, internal_gap)
            out[(ne0, ne1, new_internal)] += how_many

    trans_list = list(out.items())
    _TRANS_CACHE[state] = trans_list
    return trans_list


def max_segments_distribution(n: int) -> Dict[int, int]:
    """Return a dict {M_value: number_of_permutations_with_that_M} for size n."""
    # curr maps state -> {max_so_far: count_of_sequences}
    curr: Dict[State, Dict[int, int]] = {None: {0: 1}}
    init_trans = _initial_transitions(n)

    for _ in range(n):
        nxt: DefaultDict[State, DefaultDict[int, int]] = defaultdict(
            lambda: defaultdict(int)
        )
        for st, max_map in curr.items():
            trans = init_trans if st is None else _transitions(st)  # type: ignore[arg-type]
            for m_so_far, ways in max_map.items():
                for st2, mult in trans:
                    s2 = _segments(st2)
                    m2 = m_so_far if m_so_far >= s2 else s2
                    nxt[st2][m2] += ways * mult
        curr = {k: dict(v) for k, v in nxt.items()}

    final_state: State = (0, 0, ())
    if final_state not in curr:
        raise RuntimeError(
            "Did not reach the final full state; bug in transitions/state."
        )

    dist = curr[final_state]
    total = sum(dist.values())
    assert total == factorial(n), (total, factorial(n))
    return dist


def expected_max_segments(n: int) -> Decimal:
    """Exact expected value E[M] as a Decimal."""
    dist = max_segments_distribution(n)
    num = sum(m * c for m, c in dist.items())
    den = factorial(n)
    return Decimal(num) / Decimal(den)


def solve() -> str:
    # Test values from the problem statement for n=10
    dist10 = max_segments_distribution(10)
    assert dist10 == {1: 512, 2: 250912, 3: 1815264, 4: 1418112, 5: 144000}

    # Average for n=10 is 385643/113400, and 10! = 113400 * 32
    num10 = sum(m * c for m, c in dist10.items())
    assert num10 == 385_643 * 32

    # Main answer for n=40
    getcontext().prec = 80
    val = expected_max_segments(40)
    rounded = val.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
    return f"{rounded:.6f}"


if __name__ == "__main__":
    print(solve())
