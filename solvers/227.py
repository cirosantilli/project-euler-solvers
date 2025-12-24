#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0227.cpp'''
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
            0.5 * win2 * two_wins(need_one - 1, next_two, max_score, cache)
            + 0.5 * win2 * two_wins(need_one, next_two, max_score, cache)
            + 0.5 * lose2 * two_wins(need_one - 1, need_two, max_score, cache)
        )

        current /= 1 - 0.5 * lose2

        if best < current:
            best = current

        if next_two == 0:
            break
        bet *= 2

    cache[idx] = best
    return best


def solve(players: int) -> float:
    max_score = players
    cache = [-1.0] * (max_score * max_score)

    result = 0.5 * two_wins(max_score - 1, max_score, max_score, cache) + 0.5 * two_wins(
        max_score, max_score, max_score, cache
    )

    return result


def main() -> None:
    print(f"{solve(100):.6f}")


if __name__ == "__main__":
    main()
