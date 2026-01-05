#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0247.cpp"""
import heapq
import math


class Square:
    def __init__(self, x, y, left, below):
        self.x = x
        self.y = y
        self.left = left
        self.below = below
        self.side = 0.5 * (math.sqrt((x - y) * (x - y) + 4.0) - x - y)


def solve(index_left: int, index_below: int) -> int:
    result = 0

    first = Square(1.0, 0.0, 0, 0)
    squares = {first.side: first}
    heap = [-first.side]
    heapq.heapify(heap)

    candidates = 1
    while candidates > 0:
        result += 1

        while heap:
            side = -heap[0]
            current = squares.get(side)
            if current is None:
                heapq.heappop(heap)
                continue
            break
        else:
            break

        side = -heap[0]
        current = squares.pop(side)
        heapq.heappop(heap)

        top = Square(
            current.x, current.y + current.side, current.left, current.below + 1
        )
        if top.side not in squares:
            squares[top.side] = top
            heapq.heappush(heap, -top.side)
        right = Square(
            current.x + current.side, current.y, current.left + 1, current.below
        )
        if right.side not in squares:
            squares[right.side] = right
            heapq.heappush(heap, -right.side)

        if top.left <= index_left and top.below <= index_below:
            candidates += 1
        if right.left <= index_left and right.below <= index_below:
            candidates += 1
        if current.left <= index_left and current.below <= index_below:
            candidates -= 1

    return result


if __name__ == "__main__":
    assert solve(1, 1) == 50
    print(solve(3, 3))
