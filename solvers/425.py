#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0425.cpp"""
import heapq

sieve = []


def is_prime(x):
    if (x & 1) == 0:
        return x == 2
    return sieve[x >> 1]


def fill_sieve(size):
    global sieve
    half = size >> 1
    sieve = [True] * half
    if half > 0:
        sieve[0] = False

    i = 1
    while 2 * i * i < half:
        if sieve[i]:
            current = 3 * i + 1
            step = 2 * i + 1
            while current < half:
                sieve[current] = False
                current += step
        i += 1


def find_edges(limit):
    connected = {}

    for i in range(2, limit):
        if not is_prime(i):
            continue

        max_pos = 7
        split = [0] * max_pos
        shift = 1
        reduced = i
        for pos in range(max_pos):
            shift *= 10
            split[pos] = reduced % shift
            reduced -= reduced % shift

        shift = 1
        pos = 0
        while shift < 10 * i and shift < limit:
            current = i
            digit = split[pos] + shift
            while digit <= 9 * shift:
                current += shift
                if is_prime(current):
                    connected.setdefault(i, set()).add(current)
                    connected.setdefault(current, set()).add(i)
                digit += shift
            pos += 1
            shift *= 10

    return connected


def find_lowest_paths(connected):
    best = {}
    todo = [2]

    while todo:
        current = heapq.heappop(todo)
        top = best.get(current, 0)
        if top < current:
            top = current

        if current not in connected:
            continue

        for edge in connected[current]:
            high = best.get(edge, 0)
            if high == 0 or top < high:
                best[edge] = top
                heapq.heappush(todo, edge)

    return best


def solve(limit=10000000):
    fill_sieve(limit)
    connected = find_edges(limit)
    best = find_lowest_paths(connected)

    result = 0
    for i in range(3, limit, 2):
        if is_prime(i) and (best.get(i, 0) == 0 or best[i] > i):
            result += i

    return result


def main():
    assert solve(1000) == 431
    assert solve(10000) == 78728
    print(solve())


if __name__ == "__main__":
    main()
