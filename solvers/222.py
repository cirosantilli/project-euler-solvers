#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0222.cpp'''
import math

WORST_CASE = 999999999.0

minRadius = 0.0
maxRadius = 0.0
pipeRadius = 0.0


def getDistanceY(r1, r2):
    return math.sqrt((r1 + r2) * (r1 + r2) - (r1 - r2) * (r1 - r2))


def search(remaining, first_ball, memo):
    if remaining == 0:
        return 0.0
    if remaining in memo:
        return memo[remaining]

    best = WORST_CASE
    idx = 1
    current = remaining
    while current:
        if current & 1:
            radius = minRadius + idx
            if radius != first_ball:
                alt = search(remaining ^ (1 << (idx - 1)), first_ball, memo)
                distance = getDistanceY(radius, first_ball)
                value = distance + alt
                if value < best:
                    best = value
        idx += 1
        current >>= 1

    memo[remaining] = best
    return best


def solve(pipe_radius: float, min_radius: float, max_radius: float) -> int:
    global minRadius, maxRadius, pipeRadius
    pipeRadius = pipe_radius
    minRadius = min_radius
    maxRadius = max_radius

    num_balls = int(maxRadius - minRadius + 1)
    remaining = 0
    for i in range(num_balls):
        remaining |= (1 << i)

    memo = {}
    first_ball = maxRadius
    remaining ^= (1 << (num_balls - 1))
    second_ball = maxRadius - 1.0
    remaining ^= (1 << (num_balls - 2))

    best = getDistanceY(first_ball, second_ball) + search(remaining, first_ball, memo)
    return int(round(1000.0 * best))


def main() -> None:
    print(solve(50.0, 30.0, 50.0))


if __name__ == "__main__":
    main()
