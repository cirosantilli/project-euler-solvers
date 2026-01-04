from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations
from typing import Dict, List, Set, Tuple


def all_results(digits: Tuple[int, int, int, int]) -> Set[Fraction]:
    """
    Return all values obtainable by using each digit exactly once with + - * /
    and any parenthesization (i.e., any binary expression tree).
    """
    start: Tuple[Fraction, ...] = tuple(sorted(Fraction(d, 1) for d in digits))
    memo: Dict[Tuple[Fraction, ...], Set[Fraction]] = {}

    def rec(state: Tuple[Fraction, ...]) -> Set[Fraction]:
        if state in memo:
            return memo[state]
        if len(state) == 1:
            memo[state] = {state[0]}
            return memo[state]

        res: Set[Fraction] = set()
        m = len(state)
        for i in range(m):
            for j in range(i + 1, m):
                a, b = state[i], state[j]
                rest: List[Fraction] = [state[k] for k in range(m) if k != i and k != j]

                candidates: List[Fraction] = [a + b, a - b, b - a, a * b]
                if b != 0:
                    candidates.append(a / b)
                if a != 0:
                    candidates.append(b / a)

                for c in candidates:
                    new_state = tuple(sorted(rest + [c]))
                    res.update(rec(new_state))

        memo[state] = res
        return res

    return rec(start)


def consecutive_length(digits: Tuple[int, int, int, int]) -> Tuple[int, Set[int]]:
    vals = all_results(digits)
    ints: Set[int] = set()
    for v in vals:
        if v.denominator == 1 and v.numerator > 0:
            ints.add(v.numerator)

    n = 1
    while n in ints:
        n += 1
    return n - 1, ints


def solve() -> Tuple[str, int]:
    best_len = -1
    best_digits: Tuple[int, int, int, int] | None = None

    for comb in combinations(range(10), 4):
        L, _ = consecutive_length(comb)
        if L > best_len:
            best_len = L
            best_digits = comb

    assert best_digits is not None
    return "".join(map(str, best_digits)), best_len


def _self_test() -> None:
    # From the statement: for {1,2,3,4}, first non-expressible is 29, so run length is 28.
    L_1234, ints_1234 = consecutive_length((1, 2, 3, 4))
    assert L_1234 == 28
    assert max(ints_1234) == 36  # statement says 36 is the maximum for {1,2,3,4}

    ans, L = solve()
    assert L == 51


if __name__ == "__main__":
    _self_test()
    ans, _ = solve()
    print(ans)
