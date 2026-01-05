#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0209.cpp"""
from typing import List


def main() -> None:
    sixty_four = 64

    connections = [0] * sixty_four
    for from_state in range(sixty_four):
        left = [(from_state >> i) & 1 for i in range(6)]
        right = [0] * 6
        right[0] = left[1]
        right[1] = left[2]
        right[2] = left[3]
        right[3] = left[4]
        right[4] = left[5]
        right[5] = left[0] ^ (left[1] & left[2])

        to_state = 0
        for i in range(6):
            to_state |= (right[i] & 1) << i
        connections[from_state] = to_state

    lucas = [0] * (sixty_four + 1)
    lucas[0] = 2
    lucas[1] = 1
    for i in range(2, sixty_four + 1):
        lucas[i] = lucas[i - 2] + lucas[i - 1]

    result = 1
    used = [False] * sixty_four
    while not all(used):
        start = 0
        while used[start]:
            start += 1

        current = start
        cycle_length = 0
        while True:
            used[current] = True
            cycle_length += 1
            current = connections[current]
            if current == start:
                break

        result *= lucas[cycle_length]

    print(result)


if __name__ == "__main__":
    main()
