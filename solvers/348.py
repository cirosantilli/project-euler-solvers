#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0348.cpp"""
import heapq


def find_palindromes(max_found):
    heap = []
    seen = set()

    def push(square, cube):
        key = (square, cube)
        if key in seen:
            return
        seen.add(key)
        value = cube * cube * cube + square * square
        heapq.heappush(heap, (value, cube, square))

    push(2, 2)

    num_found = 0
    total = 0
    values = []

    while num_found < max_found:
        value, cube, square = heapq.heappop(heap)
        push(square + 1, cube)
        push(square, cube + 1)

        while (
            heap and heap[0][0] == value and heap[0][1] == cube and heap[0][2] == square
        ):
            heapq.heappop(heap)

        num_same = 1
        while heap and heap[0][0] == value:
            num_same += 1
            same_value, same_cube, same_square = heapq.heappop(heap)
            push(same_square + 1, same_cube)
            push(same_square, same_cube + 1)

            while (
                heap
                and heap[0][0] == same_value
                and heap[0][1] == same_cube
                and heap[0][2] == same_square
            ):
                heapq.heappop(heap)

        if num_same == 4:
            reverse = int(str(value)[::-1])
            if value == reverse:
                num_found += 1
                values.append(value)
                total += value

    return values


def solve(max_found=5):
    values = find_palindromes(max_found)
    return sum(values)


def main():
    values = find_palindromes(1)
    assert values[0] == 5229225
    print(solve())


if __name__ == "__main__":
    main()
