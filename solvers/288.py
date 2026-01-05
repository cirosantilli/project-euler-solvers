#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0288.cpp"""


def count_factors(value, prime):
    result = 0
    power = prime
    while power <= value:
        result += value // power
        power *= prime
    return result


def solve(prime, iterations, exponent):
    modulo = 1
    for _ in range(exponent):
        modulo *= prime

    max_power = 1
    s = 290797

    cache = {}
    result = 0
    for _ in range(iterations + 1):
        t = s % prime
        product = t * max_power

        if product in cache:
            result += cache[product]
        else:
            current = count_factors(product, prime)
            cache[product] = current
            result += current

        result %= modulo

        if max_power < modulo:
            max_power *= prime

        s = (s * s) % 50515093

    return result


def main():
    assert solve(3, 10000, 20) == 624955285
    print(solve(61, 10000000, 10))


if __name__ == "__main__":
    main()
