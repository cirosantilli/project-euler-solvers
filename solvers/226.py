#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0226.cpp"""
import math

EPSILON = 1e-8


def s_curve(x: float) -> float:
    result = 0.0
    n = 0
    while True:
        power = 2**n
        parameter = power * x

        s_val = parameter - math.floor(parameter)
        if s_val > 0.5:
            s_val = 1 - s_val

        add = s_val / power
        result += add

        if add < EPSILON:
            return result
        n += 1


def find_intersection(
    circle_x: float, circle_y: float, radius: float, x: float, step: float
) -> float:
    while True:
        y = s_curve(x)

        delta_x = x - circle_x
        delta_y = y - circle_y
        distance = math.sqrt(delta_x * delta_x + delta_y * delta_y)

        error = abs(distance - radius)
        if error < EPSILON:
            return x

        turn_around = False

        if distance < radius:
            if delta_x > 0 and step < 0:
                turn_around = True
            if delta_x < 0 and step > 0:
                turn_around = True
        else:
            if delta_x > 0 and step > 0:
                turn_around = True
            if delta_x < 0 and step < 0:
                turn_around = True

        if turn_around:
            step = -step / 2

        x += step


def integrate(
    circle_x: float,
    circle_y: float,
    radius: float,
    from_x: float,
    to_x: float,
    step: float,
) -> float:
    result = 0.0
    x = from_x
    while x <= to_x:
        upper = s_curve(x)
        lower = circle_y - math.sqrt(radius * radius - (x - circle_x) * (x - circle_x))
        result += (upper - lower) * step
        x += step
    return result


def solve(circle_x: float, circle_y: float, radius: float) -> float:
    from_x = find_intersection(circle_x, circle_y, radius, circle_x, -0.1)
    to_x = find_intersection(circle_x, circle_y, radius, circle_x, 0.1)

    step = 0.00001
    area = integrate(circle_x, circle_y, radius, from_x, to_x, step)

    return area


def main() -> None:
    print(f"{solve(0.25, 0.5, 0.25):.8f}")


if __name__ == "__main__":
    main()
