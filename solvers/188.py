#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0188.cpp"""


def powmod(base: int, exponent: int, modulo: int) -> int:
    result = 1
    while exponent > 0:
        if exponent & 1:
            result = (result * base) % modulo
        base = (base * base) % modulo
        exponent >>= 1
    return result


def tetration(a: int, b: int, modulo: int) -> int:
    last = 0
    result = 1
    while b > 0:
        b -= 1
        result = powmod(a, result, modulo)
        if last == result:
            break
        last = result
    return result


def solve(a: int, b: int, modulo: int) -> int:
    if a % 10 == 0:
        return 0
    return tetration(a, b, modulo)


if __name__ == "__main__":
    print(solve(1777, 1855, 100000000))
