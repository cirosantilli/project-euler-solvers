#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0306.cpp"""


def brute_force(num_squares, occupied_mask=0):
    for pos in range(num_squares - 1):
        two_squares = 3 << pos
        if (occupied_mask & two_squares) == 0:
            if not brute_force(num_squares, occupied_mask | two_squares):
                return True
    return False


def nim_sum(max_squares):
    num_lost = 0
    mex = [0] * (max_squares + 1)

    max_xor = 1
    while max_xor < max_squares:
        max_xor <<= 1

    found = [False] * max_xor
    for i in range(2, max_squares + 1):
        left = 0
        right = i - 2
        last_xor = 0
        while left <= right:
            xored = mex[left] ^ mex[right]
            found[xored] = True
            if last_xor < xored:
                last_xor = xored
            left += 1
            right -= 1

        unused = 0
        while found[unused]:
            unused += 1

        mex[i] = unused
        if mex[i] == 0:
            num_lost += 1

        for reset in range(last_xor + 1):
            found[reset] = False

    return max_squares - num_lost


def fast(max_squares):
    initial = [1, 5, 9, 15, 21, 25, 29, 35, 39, 43, 55, 59, 63]
    last5 = [0, 0, 0, 0, 0]

    num_lost = 0
    while True:
        current = last5[num_lost % 5] + 34
        if num_lost < len(initial):
            current = initial[num_lost]

        if current > max_squares:
            return max_squares - num_lost

        last5[num_lost % 5] = current
        num_lost += 1


def solve(limit: int) -> int:
    return fast(limit)


def main():
    assert solve(5) == 3
    assert solve(50) == 40
    print(solve(1000000))


if __name__ == "__main__":
    main()
