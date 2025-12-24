#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0386.cpp'''
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


def antichain(exponents, idx, half):
    total = 0
    num_exponents = len(exponents) - idx
    if num_exponents == 0:
        return 0

    sum_exponents = sum(exponents[idx:])
    if sum_exponents < half:
        return 0
    if half == 0 or num_exponents == 1:
        return 1

    for i in range(exponents[idx] + 1):
        total += antichain(exponents, idx + 1, half - i)
    return total


def evaluate(factors, cache):
    exponents = [1]
    for i in range(1, len(factors)):
        if factors[i] == factors[i - 1]:
            exponents[-1] += 1
        else:
            exponents.append(1)

    exponents.sort()
    key = tuple(exponents)
    if key in cache:
        return cache[key]

    result = antichain(exponents, 0, len(factors) // 2)
    cache[key] = result
    return result


def search(limit, current=1, largest_factor=1, factors=None, cache=None):
    if factors is None:
        factors = []
    if cache is None:
        cache = {}

    result = 0
    if not factors:
        result = 1

    factors.append(0)
    prime = largest_factor
    if prime <= 2:
        prime = 2
    while prime <= limit:
        if not is_prime(prime):
            prime = 3 if prime == 2 else prime + 2
            continue

        next_value = current * prime
        if next_value > limit:
            break

        factors[-1] = prime
        result += evaluate(factors, cache)

        if next_value * prime <= limit:
            result += search(limit, next_value, prime, factors, cache)

        prime = 3 if prime == 2 else prime + 2

    factors.pop()
    return result


def solve(limit=100000000):
    fill_sieve(limit)
    return search(limit)


def main():
    print(solve())


if __name__ == "__main__":
    main()
