#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0219.cpp"""
import heapq


def queue(limit: int) -> int:
    codes = [1, 4]
    heapq.heapify(codes)
    total_cost = 5

    num_codes = 2
    while num_codes < limit:
        current = heapq.heappop(codes)
        heapq.heappush(codes, current + 1)
        heapq.heappush(codes, current + 4)

        num_codes += 1
        total_cost += current + 5

    return total_cost


def array(limit: int) -> int:
    costs = [0] * 70
    costs[1] = 1
    costs[4] = 1
    total_cost = 5

    current = 1
    remaining = limit - 2
    while remaining > 0:
        while costs[current] == 0:
            current += 1

        block = costs[current]
        if block > remaining:
            block = remaining

        remaining -= block
        costs[current] -= block
        costs[current + 1] += block
        costs[current + 4] += block
        total_cost += block * (current + 5)

    return total_cost


def main() -> None:
    assert array(6) == 35
    print(array(1000000000))


if __name__ == "__main__":
    main()
