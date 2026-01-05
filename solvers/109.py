from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class Throw:
    name: str
    score: int


def generate_throws() -> Tuple[List[Throw], List[Throw]]:
    # All possible single-dart outcomes (excluding misses), by identity:
    # S1..S20, D1..D20, T1..T20, plus outer bull (S25) and inner bull (D25).
    singles = [Throw(f"S{i}", i) for i in range(1, 21)] + [Throw("S25", 25)]
    doubles = [Throw(f"D{i}", 2 * i) for i in range(1, 21)] + [Throw("D25", 50)]
    trebles = [Throw(f"T{i}", 3 * i) for i in range(1, 21)]
    all_throws = singles + doubles + trebles
    finishing_doubles = doubles[:]  # last dart must be a double (including D25)
    return all_throws, finishing_doubles


def count_checkouts_under(
    limit_exclusive: int, all_throws: List[Throw], finishing_doubles: List[Throw]
) -> int:
    """
    Count distinct checkout combinations with total score < limit_exclusive.
    Distinctness rules:
      - Last dart is a chosen finishing double (order matters via the last dart).
      - First two darts (if present) are unordered (multiset of size 0..2).
      - Misses are not included; fewer than 3 darts are represented by using 0,1,2 pre-darts.
    """
    scores = [t.score for t in all_throws]
    n = len(all_throws)
    total = 0

    for d in finishing_doubles:
        ds = d.score

        # 1-dart checkout: [d]
        if ds < limit_exclusive:
            total += 1

        # 2-dart checkout: [x, d]
        for s in scores:
            if s + ds < limit_exclusive:
                total += 1

        # 3-dart checkout: [x, y, d] with x<=y by identity (unordered first two darts)
        for i in range(n):
            si = scores[i]
            # small pruning
            if si + ds >= limit_exclusive:
                continue
            for j in range(i, n):
                if si + scores[j] + ds < limit_exclusive:
                    total += 1

    return total


def count_checkouts_exact(
    target: int, all_throws: List[Throw], finishing_doubles: List[Throw]
) -> int:
    """Count distinct checkout combinations with total score exactly equal to target."""
    scores = [t.score for t in all_throws]
    n = len(all_throws)
    total = 0

    for d in finishing_doubles:
        ds = d.score

        if ds == target:
            total += 1

        for s in scores:
            if s + ds == target:
                total += 1

        for i in range(n):
            si = scores[i]
            for j in range(i, n):
                if si + scores[j] + ds == target:
                    total += 1

    return total


def main() -> None:
    all_throws, finishing_doubles = generate_throws()

    # Given in the problem statement: exactly 11 distinct ways to checkout on a score of 6.
    assert count_checkouts_exact(6, all_throws, finishing_doubles) == 11

    # Given in the problem statement: 42336 distinct ways of checking out in total.
    # The maximum checkout is 170, so counting all totals < 171 should match.
    assert count_checkouts_under(171, all_throws, finishing_doubles) == 42336

    result = count_checkouts_under(100, all_throws, finishing_doubles)
    print(result)


if __name__ == "__main__":
    main()
