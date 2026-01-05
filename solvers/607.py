#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0607.cpp"""
import math


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, other):
        diff_x = self.x - other.x
        diff_y = self.y - other.y
        return math.sqrt(diff_x * diff_x + diff_y * diff_y)


def duration(points):
    speed = [10, 9, 8, 7, 6, 5, 10]
    result = 0.0
    for i in range(len(speed)):
        way = points[i].distance(points[i + 1])
        result += way / speed[i]
    return result


def myrand():
    if not hasattr(myrand, "seed"):
        myrand.seed = 0
    myrand.seed = (6364136223846793005 * myrand.seed + 1) & 0xFFFFFFFFFFFFFFFF
    return myrand.seed >> 30


def mutate(points, delta):
    old_duration = duration(points)

    if myrand() & 1:
        delta = -delta

    point_id = myrand() % 6 + 1
    points[point_id].y += delta

    if duration(points) >= old_duration:
        points[point_id].y -= delta


def initial_points():
    points = [Point(0.0, 0.0)]

    scaling = math.sqrt(2)
    direct = 50 * scaling
    current = ((100 - direct) / 2) / scaling
    points.append(Point(current, current))

    for i in range(1, 6):
        points.append(Point(current + i * 10, current + i * 10))

    points.append(Point(100 / scaling, 100 / scaling))
    return points


def solve():
    points = initial_points()
    myrand.seed = 0

    num_iterations = 10000
    delta = 0.01
    while delta >= 0.00001:
        for _ in range(num_iterations):
            mutate(points, delta)
        delta /= 10

    return duration(points)


def main():
    direct = duration(initial_points())
    assert round(direct, 4) == 13.4738
    print(f"{solve():.10f}")


if __name__ == "__main__":
    main()
