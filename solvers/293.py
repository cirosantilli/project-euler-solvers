#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0293.cpp"""
import heapq
import math


def solve(limit: int) -> int:
    factors = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    num_factors = len(factors)

    admissible = []
    todo = {2: 0}
    heap = [2]
    while heap:
        number = heapq.heappop(heap)
        if number not in todo:
            continue
        max_prime = todo.pop(number)
        admissible.append(number)

        for i in range(max_prime + 2):
            if i >= num_factors:
                break
            next_value = number * factors[i]
            if next_value < limit:
                next_max = max(max_prime, i)
                if next_value not in todo or todo[next_value] < next_max:
                    todo[next_value] = next_max
                    heapq.heappush(heap, next_value)

    prime_limit = limit + 1000
    primes = [2]
    max_i = int(math.isqrt(prime_limit))
    i = 3
    while i <= max_i:
        is_prime = True
        for p in primes:
            if p * p > i:
                break
            if i % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(i)
        i += 2

    fortunate = set()
    pos = 0
    for x in admissible:
        min_distance = 3
        if x <= primes[-1] - min_distance:
            while primes[pos] < x + min_distance:
                pos += 1
            distance = primes[pos] - x
            fortunate.add(distance)
            continue

        m = min_distance
        while True:
            candidate = x + m
            is_prime = True
            for p in primes:
                if candidate % p == 0:
                    is_prime = False
                    break
            if is_prime:
                fortunate.add(candidate - x)
                break
            m += 2

    total = sum(fortunate)
    return total


if __name__ == "__main__":
    print(solve(1000000000))
