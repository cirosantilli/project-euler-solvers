#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0346.cpp"""


def strong_repunits(limit):
    found = [1]

    base = 2
    while base * base < limit:
        current = 1 + base + base * base
        powers = base * base
        while current < limit:
            found.append(current)
            powers *= base
            current += powers
        base += 1

    found.sort()
    unique = []
    for value in found:
        if not unique or value != unique[-1]:
            unique.append(value)

    return unique


def solve(limit=1000000000000):
    unique = strong_repunits(limit)
    total = 0
    for value in unique:
        total += value
    return total


def main():
    assert len(strong_repunits(50)) == 8
    assert solve(1000) == 15864
    print(solve())


if __name__ == "__main__":
    main()
