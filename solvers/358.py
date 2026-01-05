#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0358.cpp"""
sieve = []


def is_prime(x):
    if (x & 1) == 0:
        return x == 2
    return sieve[x >> 1]


def fill_sieve(size):
    global sieve
    half = (size >> 1) + 1
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


def ends_with_56789(prime):
    cyclic = 56789
    modulo = 100000
    product = cyclic * prime
    return (product + 1) % modulo == 0


def starts_with_137(prime):
    cyclic = 1.0 / prime
    return 0.00000000137 < cyclic < 0.00000000138


def cyclic_digit_sum(prime):
    result = 0
    numerator = 1
    cycle_length = 0
    while True:
        cycle_length += 1
        numerator *= 10
        result += numerator // prime
        numerator %= prime
        if numerator <= 1 or cycle_length == prime:
            break

    if cycle_length != prime - 1:
        return 0

    return result


def solve(limit=750000000):
    fill_sieve(limit)

    prime = limit - 1
    while prime > 1:
        if is_prime(prime):
            if starts_with_137(prime) and ends_with_56789(prime):
                digit_sum = cyclic_digit_sum(prime)
                if digit_sum > 0:
                    return digit_sum
        prime -= 2

    return 0


def main():
    print(solve())


if __name__ == "__main__":
    main()
