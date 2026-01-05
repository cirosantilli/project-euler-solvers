#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0500.cpp"""
import heapq

sieve = []


def is_prime(x):
    if (x & 1) == 0:
        return x == 2
    return sieve[x >> 1]


def fill_sieve(size):
    global sieve
    half = (size >> 1) + 1
    sieve = [True] * half
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


def solve(value, modulo):
    candidates = []

    current_prime = 1
    while len(candidates) < value:
        current_prime += 1
        while not is_prime(current_prime):
            current_prime += 1
        heapq.heappush(candidates, (current_prime, current_prime, 1))

    choice = {}

    for _ in range(value):
        current_value, prime, exponent = heapq.heappop(candidates)
        if prime not in choice:
            choice[prime] = current_value % modulo
        else:
            choice[prime] = (choice[prime] * current_value) % modulo

        next_exponent = 2 * exponent
        next_value = current_value * current_value
        heapq.heappush(candidates, (next_value, prime, next_exponent))

    result = 1
    for val in choice.values():
        result = (result * val) % modulo

    return result


def main():
    fill_sieve(7400000)
    print(solve(500500, 500500507))


if __name__ == "__main__":
    main()
