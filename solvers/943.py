#!/usr/bin/env python3

# Converted to Python from: https://github.com/lucky-bai/projecteuler-solutions/issues/100#issuecomment-3552252592

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
import sys

U64_MASK = (1 << 64) - 1


def u64(x: int) -> int:
    """Emulate uint64_t wrap-around."""
    return x & U64_MASK


@dataclass
class Result:
    count_a: int = 0
    count_b: int = 0
    next_state: int = 0

    def total(self) -> int:
        return self.count_a + self.count_b


class KolakoskiSolver:
    __slots__ = ("a", "b", "cache")

    def __init__(self, a: int, b: int) -> None:
        self.a = a
        self.b = b
        self.cache: Dict[int, Result] = {}

    def calc(self, state: int, level: int, maxlen: int) -> Result:
        state = u64(state)
        if maxlen <= 0:
            return Result(0, 0, state)

        length_bit = u64(2 << level)
        bit = state & length_bit
        run_len = self.b if bit else self.a
        count = run_len if run_len < maxlen else maxlen

        if level == 0:
            if (state & 1) == 0:
                return Result(count_a=count, count_b=0, next_state=u64(state ^ 1))
            else:
                return Result(count_a=0, count_b=count, next_state=u64(state ^ 1))

        produced_a = 0
        produced_b = 0
        substate = u64(state ^ bit)

        for _ in range(count):
            child_key = u64(substate + (2 << level))
            cached = self.cache.get(child_key)

            if cached is not None:
                child_total = cached.count_a + cached.count_b
                if produced_a + produced_b + child_total <= maxlen:
                    child = cached
                else:
                    child = self.calc(
                        substate,
                        level - 1,
                        maxlen - (produced_a + produced_b),
                    )
            else:
                child = self.calc(
                    substate,
                    level - 1,
                    maxlen - (produced_a + produced_b),
                )

            produced_a += child.count_a
            produced_b += child.count_b
            substate = child.next_state

        res = Result(
            count_a=produced_a,
            count_b=produced_b,
            next_state=u64(substate ^ bit ^ (1 << level)),
        )

        cache_key = u64(state + (4 << level))
        self.cache[cache_key] = res
        return res


@dataclass(frozen=True)
class CountsAB:
    count_a: int
    count_b: int
    level_used: int


def evaluate_counts(a: int, b: int, limit: int) -> CountsAB:
    solver = KolakoskiSolver(a, b)
    level = 0
    res = Result()

    while True:
        res = solver.calc(0, level, limit)
        level += 1
        if res.total() >= limit or level >= 64:
            break

    if res.total() < limit:
        raise RuntimeError("Insufficient level depth")

    return CountsAB(res.count_a, res.count_b, level - 1)


def compute_T(a: int, b: int, limit: int) -> int:
    counts = evaluate_counts(a, b, limit)
    return counts.count_a * a + counts.count_b * b


if __name__ == "__main__":
    assert compute_T(2, 3, 10) == 25
    assert compute_T(4, 2, 10_000) == 30004
    MOD = 2233222333
    N = 22332223332233
    total = 0
    for a in range(2, 224):
        for b in range(2, 224):
            if a == b:
                continue
            contribution = compute_T(a, b, N) % MOD
            total = (total + contribution) % MOD
    print(total % MOD)
