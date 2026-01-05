#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0165.cpp"""
import math


def next_value() -> int:
    next_value.seed = (next_value.seed * next_value.seed) % 50515093
    return next_value.seed % 500


next_value.seed = 290797


def intersect(segment1, segment2):
    (ax, ay), (bx, by) = segment1
    (cx, cy), (dx, dy) = segment2

    slope1 = (bx - ax, by - ay)
    slope2 = (dx - cx, dy - cy)

    det = slope1[0] * slope2[1] - slope2[0] * slope1[1]
    if det == 0:
        return None

    s = (slope1[0] * (ay - cy) - slope1[1] * (ax - cx)) / det
    t = (slope2[0] * (ay - cy) - slope2[1] * (ax - cx)) / det

    if s <= 0 or s >= 1 or t <= 0 or t >= 1:
        return None

    x = ax + t * slope1[0]
    y = ay + t * slope1[1]

    precision = 1e-8
    x = round(x / precision) * precision
    y = round(y / precision) * precision

    return (x, y)


def count_intersections(segments: list[tuple[tuple[int, int], tuple[int, int]]]) -> int:
    intersections = []
    for i, segment in enumerate(segments):
        for other in segments[:i]:
            hit = intersect(segment, other)
            if hit is not None:
                intersections.append(hit)

    intersections.sort()
    unique = []
    last = None
    for point in intersections:
        if last is None or point != last:
            unique.append(point)
            last = point
    return len(unique)


def solve(limit: int) -> int:
    segments = []
    for _ in range(limit):
        segment = ((next_value(), next_value()), (next_value(), next_value()))
        segments.append(segment)
    return count_intersections(segments)


def main() -> None:
    next_value.seed = 290797
    first_values = [next_value(), next_value(), next_value(), next_value()]
    assert first_values == [27, 144, 12, 232]

    segments = [
        ((27, 44), (12, 32)),
        ((46, 53), (17, 62)),
        ((46, 70), (22, 40)),
    ]
    assert count_intersections(segments) == 1

    next_value.seed = 290797
    print(solve(5000))


if __name__ == "__main__":
    main()
