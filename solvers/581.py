#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0581.cpp'''
import heapq


def solve(limit=47):
    primes = [47, 43, 41, 37, 31, 29, 23, 19, 17, 13, 11, 7, 5, 3, 2]
    while primes and primes[0] > limit:
        primes.pop(0)

    next_values = []
    heapq.heappush(next_values, 1)

    total = 0
    last = 1

    for _ in range(10000000):
        current = heapq.heappop(next_values)

        if last + 1 == current:
            total += last

        last = current

        for p in primes:
            todo = current * p
            if todo < 1111111111111:
                heapq.heappush(next_values, todo)
            if current % p == 0:
                break

    return total


def main():
    print(solve())


if __name__ == "__main__":
    main()
