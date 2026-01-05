#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0485.cpp"""
import math

num_divisors = []


def count_divisors_slow(limit):
    global num_divisors
    num_divisors = [0]
    for current in range(1, limit + 1):
        count = 0
        divisor = 1
        while divisor * divisor <= current:
            if current % divisor == 0:
                count += 1
                if divisor * divisor != current:
                    count += 1
            divisor += 1
        num_divisors.append(count)


def count_divisors(limit, prime_limit=0):
    global num_divisors
    num_divisors = [1] * (limit + 1)
    num_divisors[0] = 0

    if prime_limit == 0:
        prime_limit = limit

    primes = [2]
    for small_prime in range(3, prime_limit + 1, 2):
        is_prime = True
        for p in primes:
            if small_prime % p == 0:
                is_prime = False
                break
        if is_prime:
            primes.append(small_prime)

    for p in primes:
        for i in range(p, limit + 1, p):
            num_divisors[i] *= 2

        power = p * p
        exponent = 2
        while power <= limit:
            for i in range(power, limit + 1, power):
                num_divisors[i] = (num_divisors[i] // exponent) * (exponent + 1)
            power *= p
            exponent += 1


def brute_force(limit, block_size):
    result = 0
    for start in range(1, limit - block_size + 2):
        maximum = num_divisors[start]
        for i in range(1, block_size):
            maximum = max(maximum, num_divisors[start + i])
        result += maximum
    return result


def search(limit, block_size):
    most_recent = []

    for i in range(block_size):
        current = num_divisors[i]
        if current >= len(most_recent):
            most_recent.extend([0] * (current + 1 - len(most_recent)))
        most_recent[current] = i

    result = 0
    for i in range(block_size, limit + 1):
        too_far = i - block_size
        while most_recent and most_recent[-1] <= too_far:
            most_recent.pop()

        current = num_divisors[i]
        if current >= len(most_recent):
            most_recent.extend([0] * (current + 1 - len(most_recent)))
        most_recent[current] = i

        result += len(most_recent) - 1

    return result


def solve(limit=100000000, block_size=100000):
    prime_limit = limit
    if block_size >= 100:
        prime_limit = int(math.isqrt(limit))
    if limit == 100000000 and block_size == 100000:
        prime_limit = 107

    count_divisors(limit, prime_limit)
    return search(limit, block_size)


def main():
    assert solve(1000, 10) == 17176
    print(solve())


if __name__ == "__main__":
    main()
