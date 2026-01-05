#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0232.cpp"""
WIN1 = 0.5
LOSE1 = 0.5


def two_wins(need_one: int, need_two: int, max_score: int, cache: list) -> float:
    if need_two == 0:
        return 1.0
    if need_one == 0:
        return 0.0

    idx = (need_one - 1) * max_score + (need_two - 1)
    if cache[idx] >= 0:
        return cache[idx]

    best = 0.0
    bet = 1
    while True:
        win2 = 0.5 / bet
        lose2 = 1 - win2

        next_two = 0 if need_two < bet else need_two - bet

        current = (
            WIN1 * win2 * two_wins(need_one - 1, next_two, max_score, cache)
            + LOSE1 * win2 * two_wins(need_one, next_two, max_score, cache)
            + WIN1 * lose2 * two_wins(need_one - 1, need_two, max_score, cache)
        )

        current /= 1 - LOSE1 * lose2

        if best < current:
            best = current

        if next_two == 0:
            break
        bet *= 2

    cache[idx] = best
    return best


def solve(max_score: int) -> float:
    cache = [-1.0] * (max_score * max_score)

    result = WIN1 * two_wins(
        max_score - 1, max_score, max_score, cache
    ) + LOSE1 * two_wins(max_score, max_score, max_score, cache)

    return result


def main() -> None:
    print(f"{solve(100):.8f}")


if __name__ == "__main__":
    main()
