#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0615.cpp"""
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
    if half:
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


def solve(num_candidates=1000000):
    modulo = 123454321

    max_prime = 15485863
    if num_candidates <= 1000000:
        max_prime = 173207

    fill_sieve(max_prime + 1)

    primes = [2]
    for i in range(3, max_prime + 1, 2):
        if is_prime(i):
            primes.append(i)

    num_variable_factors = 27
    if num_candidates < 27:
        num_variable_factors = num_candidates
    seed = 1 << num_variable_factors

    candidates = []
    heapq.heappush(candidates, (seed, 2))

    too_large = seed // 2 * primes[-1]

    previous = 0
    for _ in range(num_candidates):
        current, max_factor = heapq.heappop(candidates)

        while current == previous:
            current, max_factor = heapq.heappop(candidates)
        previous = current

        for p in primes:
            next_value = current * p
            if next_value >= too_large:
                break
            if p >= max_factor:
                heapq.heappush(candidates, (next_value, p))

        for p in primes:
            next_value = (current // 2) * p
            if next_value >= too_large:
                break
            if p >= max_factor and p > 2:
                heapq.heappush(candidates, (next_value, p))

    result = candidates[0][0] % modulo
    for _ in range(num_variable_factors, num_candidates):
        result = (result * 2) % modulo

    return result


def main():
    assert solve(5) == 80
    print(solve())


if __name__ == "__main__":
    main()
