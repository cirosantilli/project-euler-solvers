#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0549.cpp"""
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


def naive(n):
    factorial = 1
    result = 0
    while factorial % n != 0:
        result += 1
        factorial *= result
        factorial %= n
    return result


primes = []
cache = {}


def get_smallest_factorial(n):
    best = 0
    for p in primes:
        if n % p != 0:
            continue

        prime_power = 1
        while n % p == 0:
            n //= p
            prime_power *= p

        best = max(best, cache.get(prime_power, 0))

        if n == 1:
            return best
        if is_prime(n):
            return max(best, n)

    return best


def solve(limit=100000000):
    total = 0

    fill_sieve(limit)
    for i in range(2, limit):
        if is_prime(i):
            primes.append(i)

    for i in range(2, limit + 1):
        if is_prime(i):
            power = i * i
            exponent = 2
            while power <= limit:
                factorial = i
                result = i
                while True:
                    result += i
                    factorial = (factorial * result) % power
                    if factorial % power == 0:
                        break
                cache[power] = result
                power *= i
                exponent += 1

            total += i
        else:
            total += get_smallest_factorial(i)

    return total


def main():
    assert naive(10) == 5
    assert naive(25) == 10
    assert solve(100) == 2012
    print(solve())


if __name__ == "__main__":
    main()
