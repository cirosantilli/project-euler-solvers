#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0310.cpp"""
MAX_VALUE = 100000


def brute_force(a, b, c, occupied=None):
    if a == 0 and b == 0 and c == 0:
        return False

    if a > b:
        a, b = b, a
    if b > c:
        b, c = c, b
    if a > b:
        a, b = b, a

    if occupied is None:
        occupied = set()

    key = a * MAX_VALUE * MAX_VALUE + b * MAX_VALUE + c
    if key in occupied:
        return True

    for i in range(1, c + 1):
        sq = i * i
        if sq > c:
            break
        if sq <= a and not brute_force(a - sq, b, c, occupied):
            occupied.add(key)
            return True
        if sq <= b and not brute_force(a, b - sq, c, occupied):
            occupied.add(key)
            return True
        if not brute_force(a, b, c - sq, occupied):
            occupied.add(key)
            return True

    return False


def search(limit):
    mex = [0] * (limit + 1)
    for size in range(limit + 1):
        moves = [False] * 80
        i = 1
        while i * i <= size:
            moves[mex[size - i * i]] = True
            i += 1

        available = 0
        while moves[available]:
            available += 1
        mex[size] = available

    max_nim_value = max(mex)
    next_power_of_two = 1
    while next_power_of_two < max_nim_value:
        next_power_of_two *= 2

    frequency = [0] * next_power_of_two
    num_lost = 0
    for a in range(limit, -1, -1):
        b = a
        for c in range(b, limit + 1):
            frequency[mex[b] ^ mex[c]] += 1
        num_lost += frequency[mex[a]]

    return num_lost


def solve(limit: int) -> int:
    return search(limit)


def main():
    assert solve(29) == 1160
    print(solve(100000))


if __name__ == "__main__":
    main()
