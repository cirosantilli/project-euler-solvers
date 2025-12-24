#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0577.cpp'''
import math

PI = 3.14159265358979323846264
PRECISION = 0.00001


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx * dx + dy * dy)

    def angle(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        radian = math.atan2(dy, dx)
        degrees = radian * 180 / PI
        if degrees < 0:
            degrees += 360
        return degrees


def round_value(value, precision):
    return round(value / precision) * precision


def brute_force(size):
    dx = 1.0
    dy = math.sqrt(3.0) / 2

    points = []
    num_points = (size + 1) * (size + 2) // 2
    for grid_y in range(size + 1):
        y = grid_y * dy
        x = grid_y * dx / 2
        width = size - grid_y
        for _ in range(width + 1):
            points.append(Point(x, y))
            x += dx

    polar = []
    for i in points:
        current = {}
        for j in points:
            distance = i.distance(j)
            angle = i.angle(j)
            distance = round_value(distance, PRECISION)
            angle = round_value(angle, PRECISION)
            if distance > 0:
                current.setdefault(distance, []).append(angle)
        polar.append(current)

    num_found = 0
    for point in range(num_points):
        for distance, candidates in polar[point].items():
            if len(candidates) < 6:
                continue
            candidates.sort()
            for start in candidates:
                if start >= 60:
                    break
                valid = True
                next_angle = start + 60
                while next_angle < 360:
                    target = round_value(next_angle, PRECISION)
                    idx = math.floor((next_angle - start) / 60)
                    if target not in candidates:
                        valid = False
                        break
                    next_angle += 60
                if valid:
                    num_found += 1

    return num_found


def a000914(n):
    return n * (n + 1) * (n + 2) * (3 * n + 5) // 24


def a228317(n):
    return n * (n - 1) * (n - 2) * (3 * n - 5) // 8


def a236770(n):
    return n * (n + 1) * (3 * n * n + 3 * n - 2) // 8


def hexagons(n):
    if n < 3:
        return 0
    if n % 3 == 0:
        return a236770(n // 3)
    if n % 3 == 1:
        return a228317((n + 2) // 3)
    return 3 * a000914((n + 1) // 3)


def solve(size=12345):
    total = 0
    for n in range(3, size + 1):
        total += hexagons(n)
    return total


def main():
    assert hexagons(3) == 1
    assert hexagons(6) == 12
    assert hexagons(20) == 966
    print(solve())


if __name__ == "__main__":
    main()
