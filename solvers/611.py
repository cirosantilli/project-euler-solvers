#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0611.cpp"""
import math


def brute_force(from_value, to_value):
    size = to_value - from_value
    doors = [0] * size

    i = 1
    while 2 * i * i < to_value:
        min_j = i + 1
        if from_value > i * i + min_j * min_j:
            min_j = int(math.ceil(math.sqrt(from_value - i * i)))

        j = min_j
        while True:
            index = i * i + j * j
            if index >= to_value:
                break
            index -= from_value
            doors[index] ^= 1
            j += 1

        i += 1

    result = 0
    for x in doors:
        result += x & 1
    return result


def solve(limit=1000000000000, slice_size=100000000):
    num_slices = limit // slice_size
    if num_slices == 0:
        num_slices = 1

    total = 0
    for i in range(num_slices):
        start = i * slice_size
        end = start + slice_size
        if end >= limit:
            end = limit + 1
        total += brute_force(start, end)

    return total


def main():
    assert solve(5, 1000) == 1
    assert solve(100, 1000) == 27
    assert solve(1000, 1000) == 233
    assert solve(1000000, 100000) == 112168
    print(solve())


if __name__ == "__main__":
    main()
