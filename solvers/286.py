#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0286.cpp"""
threshold = 20
MAX_DISTANCE = 50
CHANCE_HIT_EXACTLY = 0.02


def probability(q, made=0, distance=1, cache=None):
    if made > threshold:
        return 0.0

    if distance > MAX_DISTANCE:
        return 1.0 if made == threshold else 0.0

    if cache is None:
        cache = {}

    key = (made * (MAX_DISTANCE + 1) + distance, q)
    if key in cache:
        return cache[key]

    chance_hit = 1.0 - distance / q
    chance_miss = 1.0 - chance_hit

    distance += 1
    result = chance_hit * probability(
        q, made + 1, distance, cache
    ) + chance_miss * probability(q, made, distance, cache)

    cache[key] = result
    return result


def solve(target: int) -> float:
    global threshold
    threshold = target
    low = MAX_DISTANCE
    high = 100.0
    accuracy = 1e-10
    while high - low > accuracy:
        mid = (high + low) / 2.0
        if probability(mid) < CHANCE_HIT_EXACTLY:
            high = mid
        else:
            low = mid

    return low if low > 50 else 0.0


if __name__ == "__main__":
    print(f"{solve(20):.10f}")
