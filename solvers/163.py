#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0163.cpp"""
import math

EPSILON = 1e-7
HEIGHT = math.sqrt(3.0) / 2


def points_equal(a, b) -> bool:
    return abs(a[0] - b[0]) < EPSILON and abs(a[1] - b[1]) < EPSILON


def inside_hull(p, A, B, C) -> bool:
    def determinant(p1, p2, p3) -> float:
        return (p2[0] - p1[0]) * (p3[1] - p1[1]) - (p2[1] - p1[1]) * (p3[0] - p1[0])

    if determinant(A, B, p) < -EPSILON:
        return False
    if determinant(B, C, p) < -EPSILON:
        return False
    if determinant(C, A, p) < -EPSILON:
        return False
    return True


def line_from(p1, p2):
    a = p1[1] - p2[1]
    b = p2[0] - p1[0]
    c = p2[0] * p1[1] - p1[0] * p2[1]
    return (a, b, c)


def intersect(l1, l2):
    a1, b1, c1 = l1
    a2, b2, c2 = l2
    det = a1 * b2 - a2 * b1
    if abs(det) < EPSILON:
        return None
    x = (c1 * b2 - c2 * b1) / det
    y = (a1 * c2 - a2 * c1) / det
    return (x, y)


def is_valid_triangle(l1, l2, l3, A, B, C) -> bool:
    ab = intersect(l1, l2)
    if ab is None:
        return False
    bc = intersect(l2, l3)
    if bc is None:
        return False
    ac = intersect(l1, l3)
    if ac is None:
        return False
    if points_equal(ab, bc):
        return False
    return (
        inside_hull(ab, A, B, C)
        and inside_hull(bc, A, B, C)
        and inside_hull(ac, A, B, C)
    )


def solve(size: int) -> int:
    A = [0.0, 0.0]
    B = [1.0, 0.0]
    C = [0.5, HEIGHT]

    AB = [(A[0] + B[0]) / 2, (A[1] + B[1]) / 2]
    AC = [(A[0] + C[0]) / 2, (A[1] + C[1]) / 2]
    BC = [(B[0] + C[0]) / 2, (B[1] + C[1]) / 2]

    lines = []
    for i in range(size):
        lines.append(line_from([A[0], i * HEIGHT], [B[0], i * HEIGHT]))

    for i in range(size):
        lines.append(line_from([i, A[1]], [BC[0] + i, BC[1]]))
        if i > 0:
            lines.append(line_from([-i, A[1]], [BC[0] - i, BC[1]]))

    for i in range(size):
        lines.append(line_from([i, A[1]], [C[0] + i, C[1]]))

    for i in range(size):
        lines.append(line_from([i + 1, B[1]], [C[0] + i, C[1]]))

    for i in range(2 * size - 1):
        lines.append(line_from([i + 1, B[1]], [AC[0] + i, AC[1]]))

    for i in range(1, 2 * size):
        lines.append(line_from([i * C[0], 0.0], [i * C[0], HEIGHT]))

    A[0] *= size
    A[1] *= size
    B[0] *= size
    B[1] *= size
    C[0] *= size
    C[1] *= size

    count = 0
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            first = intersect(lines[i], lines[j])
            if first is None or not inside_hull(first, A, B, C):
                continue
            for k in range(j + 1, len(lines)):
                if is_valid_triangle(lines[i], lines[j], lines[k], A, B, C):
                    count += 1

    return count


def main() -> None:
    assert solve(1) == 16
    assert solve(2) == 104
    print(solve(36))


if __name__ == "__main__":
    main()
