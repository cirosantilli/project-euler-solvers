#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0359.cpp"""
import math


def p_value(floor, room, modulo=100000000):
    result = (floor + 1) // 2 * floor
    if floor % 2 == 1 and floor > 1:
        result -= (floor + 1) // 2

    increment_even = 1
    if floor % 2 == 0:
        increment_even = 2 * floor + 1

    increment_odd = 2
    if floor % 2 == 1:
        increment_odd = 2 * floor

    if floor == 1:
        increment_odd = 3
        increment_even = 2

    num_even = room // 2
    triangle_even = num_even * (num_even + 1) // 2
    triangle_even *= 2

    num_odd = (room - 1) // 2
    triangle_odd = num_odd * (num_odd + 1) // 2
    triangle_odd *= 2

    result += num_even * (increment_even - 2) + triangle_even
    result += num_odd * (increment_odd - 2) + triangle_odd

    if modulo is None:
        return result
    return result % modulo


def solve(max_exponent_two=27, max_exponent_three=12):
    number = (2**max_exponent_two) * (3**max_exponent_three)
    modulo = 100000000

    total = 0
    two = 1
    for _ in range(max_exponent_two + 1):
        three = 1
        for _ in range(max_exponent_three + 1):
            floor = two * three
            room = number // floor
            total = (total + p_value(floor, room, modulo)) % modulo
            three *= 3
        two *= 2

    return total


def main():
    assert p_value(1, 1, None) == 1
    assert p_value(1, 2, None) == 3
    assert p_value(2, 1, None) == 2
    assert p_value(10, 20, None) == 440
    assert p_value(25, 75, None) == 4863
    assert p_value(99, 100, None) == 19454
    print(solve())


if __name__ == "__main__":
    main()
