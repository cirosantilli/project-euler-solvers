#!/usr/bin/env python3
"""Project Euler 298: Selective Amnesia

We compute the expected value of |L-R| after 50 turns.

Game rules:
- Each turn, a uniform random integer in {1,...,10} is called.
- Each player remembers up to 5 distinct numbers.
- If the called number is in a player's memory, that player scores 1 point.
- Otherwise, the player inserts the called number, evicting a number if full.

Eviction strategies:
- Larry evicts the number that hasn't been called in the longest time (LRU).
- Robin evicts the number that has been in memory the longest time (FIFO).

Approach:
The actual labels 1..10 are symmetric. A game state only depends on the
overlap pattern between the two ordered memories, not on the specific labels.
We canonicalize states by renaming the numbers in a deterministic order,
reducing the Markov chain to 438 states.

We do dynamic programming over turns, carrying the exact count of sequences
leading to each (state, score_difference) pair. Because each turn has 10
equiprobable outcomes, counts are integers with an implicit denominator 10^t.
This gives an exact expected value, then we round to 8 decimals.
"""

from __future__ import annotations

from collections import defaultdict
from functools import lru_cache
from typing import Dict, Iterable, List, Tuple

CAPACITY = 5
NUMBERS = 10
TURNS = 50


# --- Player update rules -----------------------------------------------------


def larry_update(memory: Tuple[int, ...], x: int) -> Tuple[Tuple[int, ...], int]:
    """Larry's memory as an LRU list, stored MRU->LRU. Returns (new_memory, hit)."""
    try:
        idx = memory.index(x)
    except ValueError:
        new_mem = (x,) + memory
        if len(new_mem) > CAPACITY:
            new_mem = new_mem[:CAPACITY]  # evict LRU at the end
        return new_mem, 0

    # hit: move to front (MRU)
    if idx == 0:
        return memory, 1
    return (x,) + memory[:idx] + memory[idx + 1 :], 1


def robin_update(memory: Tuple[int, ...], x: int) -> Tuple[Tuple[int, ...], int]:
    """Robin's memory as a FIFO queue, stored oldest->newest. Returns (new_memory, hit)."""
    if x in memory:
        return memory, 1
    new_mem = memory + (x,)
    if len(new_mem) > CAPACITY:
        new_mem = new_mem[1:]  # evict oldest
    return new_mem, 0


# --- Canonical state representation -----------------------------------------


State = Tuple[Tuple[int, ...], Tuple[int, ...]]  # (Larry_mem, Robin_mem)


def canonicalize(L: Tuple[int, ...], R: Tuple[int, ...]) -> State:
    """Rename ids in (L, R) to 0..k-1 in deterministic first-seen order (L then R)."""
    mapping: Dict[int, int] = {}
    nxt = 0
    for a in L:
        if a not in mapping:
            mapping[a] = nxt
            nxt += 1
    for a in R:
        if a not in mapping:
            mapping[a] = nxt
            nxt += 1
    return tuple(mapping[a] for a in L), tuple(mapping[a] for a in R)


def union_size(state: State) -> int:
    """Number of distinct labels currently present in either memory."""
    L, R = state
    if not L and not R:
        return 0
    return max((max(L) if L else -1), (max(R) if R else -1)) + 1


@lru_cache(maxsize=None)
def transitions(state: State) -> Tuple[Tuple[State, int, int], ...]:
    """Return compressed transitions as (next_state, delta, weight) triples.

    - delta = (Larry_hit - Robin_hit) in {-1,0,1}
    - weight = number of actual numbers in {1..10} that correspond to this transition
    """
    L, R = state
    k = union_size(state)
    trans_counts: Dict[Tuple[State, int], int] = defaultdict(int)

    # Call one of the k numbers currently present in the union.
    for x in range(k):
        L2, hitL = larry_update(L, x)
        R2, hitR = robin_update(R, x)
        delta = hitL - hitR
        ns = canonicalize(L2, R2)
        trans_counts[(ns, delta)] += 1

    # Call a number absent from both memories (all absent labels are symmetric).
    if k < NUMBERS:
        x = k  # fresh temporary id
        L2, hitL = larry_update(L, x)
        R2, hitR = robin_update(R, x)
        delta = hitL - hitR
        ns = canonicalize(L2, R2)
        trans_counts[(ns, delta)] += NUMBERS - k

    return tuple((ns, delta, w) for (ns, delta), w in trans_counts.items())


# --- Dynamic programming -----------------------------------------------------


def expected_abs_diff_numerator(turns: int = TURNS) -> int:
    """Return numerator of E[|L-R|] with implicit denominator 10^turns.

    We keep exact counts of length-t sequences leading to each (state, diff).
    """
    start = canonicalize((), ())
    # For turn t, each distribution list has length 2t+1, representing diffs [-t..t]
    cur: Dict[State, List[int]] = {start: [1]}

    for t in range(turns):
        new_len = 2 * (t + 1) + 1  # old_len + 2
        nxt: Dict[State, List[int]] = {}

        for st, dist in cur.items():
            for ns, delta, weight in transitions(st):
                shift = delta + 1  # map -1,0,+1 -> 0,1,2 in index space
                dest = nxt.get(ns)
                if dest is None:
                    dest = [0] * new_len
                    nxt[ns] = dest

                if weight == 1:
                    for i, val in enumerate(dist):
                        dest[i + shift] += val
                else:
                    for i, val in enumerate(dist):
                        dest[i + shift] += val * weight

        cur = nxt

    # Compute numerator: sum |diff| * count
    offset = turns
    numerator = 0
    for dist in cur.values():
        for idx, count in enumerate(dist):
            diff = idx - offset
            numerator += abs(diff) * count
    return numerator


def format_expected_value(numerator: int, turns: int = TURNS, decimals: int = 8) -> str:
    """Format numerator / 10^turns rounded (half-up) to `decimals` places."""
    if decimals < 0:
        raise ValueError("decimals must be non-negative")
    if turns < decimals:
        # Not needed here, but keep it correct in general.
        denom = 10**turns
        scaled = numerator * (10**decimals)
        # half-up rounding
        rounded_units = (scaled + denom // 2) // denom
    else:
        # expected * 10^decimals = numerator / 10^(turns-decimals)
        denom = 10 ** (turns - decimals)
        rounded_units = (numerator + denom // 2) // denom  # half-up

    whole = rounded_units // (10**decimals)
    frac = rounded_units % (10**decimals)
    return f"{whole}.{frac:0{decimals}d}"


def solve() -> str:
    numerator = expected_abs_diff_numerator(TURNS)
    return format_expected_value(numerator, TURNS, 8)


# --- Problem statement example asserts --------------------------------------


def _run_example_asserts() -> None:
    # Example sequence from the problem statement (10 turns)
    calls = [1, 2, 4, 6, 1, 8, 10, 2, 4, 1]

    # Expected per-turn (sorted) memories and scores from the table in the statement.
    exp_L_mem = [
        [1],
        [1, 2],
        [1, 2, 4],
        [1, 2, 4, 6],
        [1, 2, 4, 6],
        [1, 2, 4, 6, 8],
        [1, 4, 6, 8, 10],
        [1, 2, 6, 8, 10],
        [1, 2, 4, 8, 10],
        [1, 2, 4, 8, 10],
    ]
    exp_L_score = [0, 0, 0, 0, 1, 1, 1, 1, 1, 2]

    exp_R_mem = [
        [1],
        [1, 2],
        [1, 2, 4],
        [1, 2, 4, 6],
        [1, 2, 4, 6],
        [1, 2, 4, 6, 8],
        [2, 4, 6, 8, 10],
        [2, 4, 6, 8, 10],
        [2, 4, 6, 8, 10],
        [1, 4, 6, 8, 10],
    ]
    exp_R_score = [0, 0, 0, 0, 1, 1, 1, 2, 3, 3]

    L: Tuple[int, ...] = ()
    R: Tuple[int, ...] = ()
    L_score = 0
    R_score = 0

    for t, x in enumerate(calls):
        L, hitL = larry_update(L, x)
        R, hitR = robin_update(R, x)
        L_score += hitL
        R_score += hitR

        assert sorted(L) == exp_L_mem[t], (t + 1, sorted(L), exp_L_mem[t])
        assert L_score == exp_L_score[t], (t + 1, L_score, exp_L_score[t])

        assert sorted(R) == exp_R_mem[t], (t + 1, sorted(R), exp_R_mem[t])
        assert R_score == exp_R_score[t], (t + 1, R_score, exp_R_score[t])

    assert L_score == 2 and R_score == 3


def main() -> None:
    _run_example_asserts()
    print(solve())


if __name__ == "__main__":
    main()
