#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0240.cpp"""
num_dice = 20
max_points = 12
num_top = 10
sum_top = 70

factorial = []


def count(dices):
    how_often = [0] * (max_points + 1)
    for x in dices:
        how_often[x] += 1

    result = factorial[num_dice]
    for x in how_often:
        if x > 1:
            result //= factorial[x]

    return result


def search(dices):
    if len(dices) == num_dice:
        return count(dices)

    if len(dices) == num_top:
        if sum(dices) != sum_top:
            return 0

    max_dice = max_points
    if dices:
        max_dice = dices[-1]

    result = 0
    for dice in range(1, max_dice + 1):
        dices.append(dice)
        result += search(dices)
        dices.pop()

    return result


def solve(dice_count: int, sides: int, top_count: int, top_sum: int) -> int:
    global num_dice, max_points, num_top, sum_top, factorial
    num_dice = dice_count
    max_points = sides
    num_top = top_count
    sum_top = top_sum

    if num_top > num_dice:
        return 0

    factorial = [1] * (num_dice + 1)
    current = 1
    for i in range(1, num_dice + 1):
        current *= i
        factorial[i] = current

    dices = []
    return search(dices)


def main() -> None:
    assert solve(5, 6, 3, 15) == 1111
    print(solve(20, 12, 10, 70))


if __name__ == "__main__":
    main()
