#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0205.cpp"""


def roll(dices: int, sides: int, count: list[int], total: int = 0) -> None:
    if dices == 0:
        count[total] += 1
        return
    for i in range(1, sides + 1):
        roll(dices - 1, sides, count, total + i)


def solve(
    dices_peter: int, sides_peter: int, dices_colin: int, sides_colin: int
) -> float:
    max_total = max(dices_peter * sides_peter, dices_colin * sides_colin)

    peter = [0] * (max_total + 1)
    roll(dices_peter, sides_peter, peter)
    sum_peter = sum(peter)

    colin = [0] * (max_total + 1)
    roll(dices_colin, sides_colin, colin)
    sum_colin = sum(colin)

    win_peter = 0.0
    for total in range(1, max_total + 1):
        num_wins = sum(colin[1:total])
        beats = num_wins / sum_colin
        win_peter += beats * peter[total] / sum_peter

    return win_peter


def main() -> None:
    print(f"{solve(9, 4, 6, 6):.7f}")


if __name__ == "__main__":
    main()
