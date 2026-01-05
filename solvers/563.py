#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0563.cpp"""
import bisect
import heapq
import math


def solve(max_combinations=100):
    no_solution = 0
    num_solutions = 1
    solutions = [no_solution] * (max_combinations + 1)

    result = 0

    areas = []
    heapq.heappush(areas, 1)

    sides = []

    ignore_above = 2300000000000000

    while num_solutions < max_combinations:
        current = heapq.heappop(areas)

        if current * current <= ignore_above:
            sides.append(current)

        multiples = [23, 19, 17, 13, 11, 7, 5, 3, 2]
        for multiple in multiples:
            next_value = multiple * current
            if next_value <= ignore_above:
                heapq.heappush(areas, next_value)
            if current % multiple == 0:
                break

        if num_solutions >= 56:
            if current % 800 != 0:
                continue
        elif num_solutions >= 8:
            if current % 80 != 0:
                continue
        elif current % 40 != 0:
            continue

        idx = bisect.bisect_right(sides, int(math.isqrt(current))) - 1
        if idx <= 0:
            continue

        num_found = 0
        while idx > 0:
            short_side = sides[idx]
            idx -= 1
            long_side = current // short_side

            if long_side * 10 > short_side * 11:
                break

            if long_side * short_side == current:
                num_found += 1

        if num_found < 2 or num_found > max_combinations:
            continue

        if solutions[num_found] == no_solution:
            solutions[num_found] = current
            result += current
            num_solutions += 1

    return result, solutions


def main():
    total, solutions = solve()
    assert solutions[3] == 889200
    print(total)


if __name__ == "__main__":
    main()
