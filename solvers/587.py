#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0587.cpp"""
import math

EPSILON = 0.00000000001
NO_LINE = 0


def get_intersection(slope):
    x = 0.5
    step = 0.1
    while True:
        left_side = slope * x
        right_side = 1 - math.sqrt(1 - (x - 1) * (x - 1))
        if abs(left_side - right_side) < EPSILON:
            return x
        if left_side > right_side:
            x -= step
        else:
            x += step
        step *= 0.99


def get_area_l(slope):
    intersection = 0.0
    left_area = 0.0
    if slope > 0:
        intersection = get_intersection(slope)
        left_area = intersection * (intersection * slope) / 2

    right_area = 0.0
    step = (1 - intersection) / 100000
    x = intersection
    while x < 1:
        y = 1 - math.sqrt(1 - (x - 1) * (x - 1))
        right_area += y * step
        x += step

    return left_area + right_area


def solve(limit=0.1):
    l_section = get_area_l(NO_LINE)

    num_circles = 1
    step = 64
    while True:
        slope = 1.0 / num_circles
        area = get_area_l(slope)
        percentage = 100 * area / l_section
        if percentage < limit:
            if step == 1:
                break
            num_circles -= step
            step //= 2
        num_circles += step

    return num_circles


def main():
    assert solve(10) == 15
    print(solve())


if __name__ == "__main__":
    main()
