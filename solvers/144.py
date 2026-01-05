#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0144.cpp"""
import math


def main() -> None:
    steps = 0
    from_x, from_y = 0.0, 10.1
    to_x, to_y = 1.4, -9.6

    while True:
        if -0.01 <= to_x <= 0.01 and to_y > 9.9:
            break

        normal_x, normal_y = -4 * to_x, -to_y
        length = math.hypot(normal_x, normal_y)
        normal_x /= length
        normal_y /= length

        direction_x = to_x - from_x
        direction_y = to_y - from_y
        if direction_x == 0:
            steps += 1
            break

        dot = direction_x * normal_x + direction_y * normal_y
        reflect_x = direction_x - 2 * dot * normal_x
        reflect_y = direction_y - 2 * dot * normal_y

        slope = reflect_y / reflect_x

        from_x, from_y = to_x, to_y

        to_x = (4 * from_x - slope * slope * from_x + 2 * slope * from_y) / (
            -4 - slope * slope
        )
        to_y = slope * (to_x - from_x) + from_y

        steps += 1

    print(steps)


if __name__ == "__main__":
    main()
