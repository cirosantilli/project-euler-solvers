#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0290.cpp"""
SIGNATURE = 137
UNKNOWN = -1
CACHE = [UNKNOWN] * ((18 + 1) * 137 * 240)


def digit_sum(x):
    result = 0
    while x > 0:
        result += x % 10
        x //= 10
    return result


def search(num_digits, u=0, v=0):
    idx = num_digits
    idx = idx * 137 + u
    idx = idx * 240 + (v + 120)
    cached = CACHE[idx]
    if cached != UNKNOWN:
        return cached

    if num_digits == 1:
        result = 0
        for digit in range(10):
            if digit_sum(SIGNATURE * digit + u) + v == digit:
                result += 1
        CACHE[idx] = result
        return result

    result = 0
    for digit in range(10):
        next_u = (SIGNATURE * digit + u) // 10
        next_v = (SIGNATURE * digit + u) % 10 + v - digit
        result += search(num_digits - 1, next_u, next_v)

    CACHE[idx] = result
    return result


def solve(limit: int) -> int:
    return search(limit)


def main():
    print(solve(18))


if __name__ == "__main__":
    main()
