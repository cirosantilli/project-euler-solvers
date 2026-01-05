#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0160.cpp"""
MODULO = 100000


def powmod(base: int, exponent: int, modulo: int) -> int:
    result = 1
    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulo
        base = (base * base) % modulo
        exponent >>= 1
    return result


def algorithm1(limit: int) -> int:
    iterations = limit // 10
    twos = 0
    result = powmod(1 * 2 * 3 * 6 * 7 * 8 * 9, iterations, MODULO)

    for i in range(iterations):
        if twos > 100:
            result *= 4
        else:
            twos += 2

        five = i * 2 + 1
        twos -= 1
        while five % 5 == 0:
            five //= 5
            twos -= 1
        result *= five % MODULO

        ten = i + 1
        while ten % 5 == 0:
            ten //= 5
            twos -= 1
        result *= ten % MODULO

        result %= MODULO

    while twos > 0:
        result = (result * 2) % MODULO
        twos -= 1

    return result


def algorithm2(limit: int) -> int:
    result = 1
    for i in range(1, limit + 1):
        current = i
        while current % 5 == 0:
            current //= 5
            result //= 2
        result *= current % MODULO
        result %= 1000000000
    return result % MODULO


def trailing_digits(limit: int) -> int:
    while limit % MODULO == 0:
        limit //= 5

    if limit > 2560000:
        return algorithm1(limit)
    return algorithm2(limit)


def main() -> None:
    assert trailing_digits(9) == 36288
    assert trailing_digits(10) == 36288
    assert trailing_digits(20) == 17664
    print(trailing_digits(1000000000000))


if __name__ == "__main__":
    main()
