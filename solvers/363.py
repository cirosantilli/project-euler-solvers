#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0363.cpp"""
import math

PI = 3.14159265358979323846264338327950288419


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, other):
        diff_x = self.x - other.x
        diff_y = self.y - other.y
        return math.sqrt(diff_x * diff_x + diff_y * diff_y)


def bezier_arc(v, t):
    return Point(
        (1 - t) ** 3 + 3 * (1 - t) ** 2 * t + 3 * (1 - t) * t * t * v,
        3 * (1 - t) ** 2 * t * v + 3 * (1 - t) * t * t + t * t * t,
    )


def get_length(v, start, end, epsilon):
    bisect = (start + end) / 2
    p_start = bezier_arc(v, start)
    p_middle = bezier_arc(v, bisect)
    p_end = bezier_arc(v, end)

    total_distance = p_start.distance(p_end)
    first_half = p_middle.distance(p_start)
    second_half = p_middle.distance(p_end)
    more_precise = first_half + second_half
    if more_precise < total_distance + epsilon:
        return more_precise

    return get_length(v, start, bisect, epsilon) + get_length(v, bisect, end, epsilon)


def solve():
    v = 0.551778477804467717845437407295027163650331289
    pi_div2 = PI / 2

    epsilon = 1e-17
    length = get_length(v, 0.0, 1.0, epsilon)
    error = 100 * (length - pi_div2) / pi_div2
    return error


def main():
    print(f"{solve():.10f}")


if __name__ == "__main__":
    main()
