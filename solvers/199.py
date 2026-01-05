#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0199.cpp"""
import math


def get_area(radius: float) -> float:
    return radius * radius * math.pi / 4


def evaluate(k1: float, k2: float, k3: float, depth: int) -> float:
    k4 = k1 + k2 + k3 + 2 * math.sqrt(k1 * k2 + k2 * k3 + k1 * k3)
    radius = 1 / k4
    area = get_area(radius)
    if depth == 1:
        return area

    return (
        area
        + evaluate(k1, k2, k4, depth - 1)
        + evaluate(k2, k3, k4, depth - 1)
        + evaluate(k1, k3, k4, depth - 1)
    )


def solve(depth: int) -> float:
    outer_k = 3 - 2 * math.sqrt(3)
    outer_radius = -1 / outer_k

    inner_radius = 1.0
    inner_k = 1 / inner_radius

    initial = 3 * get_area(inner_radius)
    v_shaped = evaluate(outer_k, inner_k, inner_k, depth)
    middle = evaluate(inner_k, inner_k, inner_k, depth)

    covered = initial + 3 * v_shaped + middle
    covered /= get_area(outer_radius)
    return 1 - covered


if __name__ == "__main__":
    assert f"{solve(3):.8f}" == "0.06790342"
    print(f"{solve(10):.8f}")
