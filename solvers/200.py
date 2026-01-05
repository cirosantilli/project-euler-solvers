#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0200.cpp"""
from typing import Set


def mulmod(a: int, b: int, modulo: int) -> int:
    return (a * b) % modulo


def powmod(base: int, exponent: int, modulo: int) -> int:
    result = 1
    while exponent > 0:
        if exponent & 1:
            result = mulmod(result, base, modulo)
        base = mulmod(base, base, modulo)
        exponent >>= 1
    return result


def is_prime(p: int) -> bool:
    small_mask = (
        (1 << 2)
        | (1 << 3)
        | (1 << 5)
        | (1 << 7)
        | (1 << 11)
        | (1 << 13)
        | (1 << 17)
        | (1 << 19)
        | (1 << 23)
        | (1 << 29)
    )
    if p < 31:
        return (small_mask & (1 << p)) != 0

    if (
        p % 2 == 0
        or p % 3 == 0
        or p % 5 == 0
        or p % 7 == 0
        or p % 11 == 0
        or p % 13 == 0
        or p % 17 == 0
    ):
        return False

    if p < 17 * 19:
        return True

    test_against1 = (377687, 0)
    test_against2 = (31, 73, 0)
    test_against3 = (2, 7, 61, 0)
    test_against4 = (2, 13, 23, 1662803, 0)
    test_against7 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022, 0)

    if p < 5329:
        test_against = test_against1
    elif p < 9080191:
        test_against = test_against2
    elif p < 4759123141:
        test_against = test_against3
    elif p < 1122004669633:
        test_against = test_against4
    else:
        test_against = test_against7

    d = p - 1
    shift = 0
    while d % 2 == 0:
        d //= 2
        shift += 1

    for base in test_against:
        if base == 0:
            break
        x = powmod(base, d, p)
        if x == 1 or x == p - 1:
            continue
        maybe_prime = False
        for _ in range(shift):
            x = mulmod(x, x, p)
            if x == 1:
                return False
            if x == p - 1:
                maybe_prime = True
                break
        if not maybe_prime:
            return False

    return True


def is_prime_proof(value: int) -> bool:
    str_value = str(value)
    for pos in range(len(str_value)):
        if value % 2 == 0:
            pos = len(str_value) - 1

        for digit in "0123456789":
            if digit == "0" and pos == 0:
                continue
            if (ord(digit) % 2 == 0) and pos == len(str_value) - 1:
                continue
            if digit == str_value[pos]:
                continue

            modified = int(str_value[:pos] + digit + str_value[pos + 1 :])
            if is_prime(modified):
                return False

    return True


def next_prime(start: int, other: int) -> int:
    value = start
    while value == other or not is_prime(value):
        value += 1
    return value


def solve(target: int, token: str) -> tuple[int, int]:
    count = 0
    second_value = -1

    squbes: Set[tuple[int, int, int]] = set()
    squbes.add((3, 2, 3 * 3 * 2 * 2 * 2))
    squbes.add((2, 3, 2 * 2 * 3 * 3 * 3))

    while True:
        current = min(squbes, key=lambda x: x[2])
        squbes.remove(current)
        p, q, value = current

        if token in str(value) and is_prime_proof(value):
            count += 1
            if count == 2:
                second_value = value
            if count == target:
                return value, second_value

        next_p = next_prime(p + 1, q)
        squbes.add((next_p, q, next_p * next_p * q * q * q))

        next_q = next_prime(q + 1, p)
        squbes.add((p, next_q, p * p * next_q * next_q * next_q))


if __name__ == "__main__":
    value, second_value = solve(200, "200")
    assert second_value == 1992008
    print(value)
