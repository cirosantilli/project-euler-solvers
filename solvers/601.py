#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0601.cpp"""


def gcd(a, b):
    while a != 0:
        a, b = b % a, a
    return b


def lcm(a, b):
    return a * (b // gcd(a, b))


def brute_force(limit, streak):
    result = 0
    for i in range(2, limit):
        current = 1
        while (i + current - 1) % current == 0:
            current += 1
        current -= 1
        if current == streak:
            result += 1
    return result


def solve(limit, streak):
    multiple = streak
    for i in range(2, streak):
        multiple = lcm(multiple, i)

    limit -= 1
    limit -= 1
    at_least = limit // multiple

    multiple = lcm(multiple, streak + 1)
    too_many = limit // multiple

    return at_least - too_many


def main():
    assert solve(14, 3) == 1
    assert solve(1000000, 6) == 14286

    result = 0
    pow4 = 4
    for i in range(1, 31 + 1):
        result += solve(pow4, i)
        pow4 *= 4

    print(result)


if __name__ == "__main__":
    main()
