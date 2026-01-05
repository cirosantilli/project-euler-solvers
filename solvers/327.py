#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0327.cpp"""


def search(cards, rooms):
    need = 1
    transport = cards - 2

    for _ in range(rooms, 0, -1):
        consumed = 0
        if need >= cards:
            moves = (need - cards) // transport
            if need - moves * transport >= cards:
                moves += 1

            need -= moves * transport
            consumed += moves * cards

        previous = need + consumed + 1
        need = previous

    return need


def solve(rooms=30, max_cards=40):
    result = 0
    for i in range(3, max_cards + 1):
        result += search(i, rooms)

    return result


def main():
    assert search(3, 6) == 123
    assert search(4, 6) == 23
    assert search(3, 6) + search(4, 6) == 146
    assert solve(10, 10) == 10382
    print(solve())


if __name__ == "__main__":
    main()
