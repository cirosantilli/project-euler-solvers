#!/usr/bin/env python
'''Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0315.cpp'''
SEGMENTS = [
    (1 << 0) | (1 << 1) | (1 << 2) | (0 << 3) | (1 << 4) | (1 << 5) | (1 << 6),
    (0 << 0) | (0 << 1) | (1 << 2) | (0 << 3) | (0 << 4) | (1 << 5) | (0 << 6),
    (1 << 0) | (0 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (0 << 5) | (1 << 6),
    (1 << 0) | (0 << 1) | (1 << 2) | (1 << 3) | (0 << 4) | (1 << 5) | (1 << 6),
    (0 << 0) | (1 << 1) | (1 << 2) | (1 << 3) | (0 << 4) | (1 << 5) | (0 << 6),
    (1 << 0) | (1 << 1) | (0 << 2) | (1 << 3) | (0 << 4) | (1 << 5) | (1 << 6),
    (1 << 0) | (1 << 1) | (0 << 2) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 6),
    (1 << 0) | (1 << 1) | (1 << 2) | (0 << 3) | (0 << 4) | (1 << 5) | (0 << 6),
    (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3) | (1 << 4) | (1 << 5) | (1 << 6),
    (1 << 0) | (1 << 1) | (1 << 2) | (1 << 3) | (0 << 4) | (1 << 5) | (1 << 6),
]

sieve = []


def is_prime(x):
    if (x & 1) == 0:
        return x == 2
    return sieve[x >> 1]


def fill_sieve(size):
    global sieve
    half = (size >> 1) + 1
    sieve = [True] * half
    if half > 0:
        sieve[0] = False

    i = 1
    while 2 * i * i < half:
        if sieve[i]:
            current = 3 * i + 1
            step = 2 * i + 1
            while current < half:
                sieve[current] = False
                current += step
        i += 1


def digit_sum(x):
    result = 0
    while x > 0:
        result += x % 10
        x //= 10
    return result


def get_segments(x):
    result = 0
    shift = 0
    while x > 0:
        current = SEGMENTS[x % 10]
        result |= current << shift
        x //= 10
        shift += 8
    return result


def popcnt(x):
    return x.bit_count()


def sam(x, cache):
    if x < len(cache) and cache[x] > 0:
        return cache[x]

    segments = get_segments(x)
    result = 2 * popcnt(segments)
    if x > 9:
        result += sam(digit_sum(x), cache)

    if x < len(cache):
        cache[x] = result
    return result


def max_transitions(x, previous_segments=0):
    segments = get_segments(x)
    transitions = segments ^ previous_segments
    result = popcnt(transitions)

    if x > 9:
        result += max_transitions(digit_sum(x), segments)
    else:
        result += popcnt(segments)

    return result


def transitions_for_sequence(values: list[int]) -> tuple[int, int]:
    cache = [0] * 100
    sam_total = 0
    max_total = 0
    for value in values:
        sam_total += sam(value, cache)
        max_total += max_transitions(value)
    return sam_total, max_total


def solve(start: int, end: int) -> int:
    if start > end:
        return 0

    fill_sieve(end)

    sum_sam = 0
    sum_max = 0
    cache = [0] * 100
    for i in range(start | 1, end + 1, 2):
        if not is_prime(i):
            continue
        sum_sam += sam(i, cache)
        sum_max += max_transitions(i)

    return sum_sam - sum_max


if __name__ == "__main__":
    assert transitions_for_sequence([137, 11, 2]) == (40, 30)
    print(solve(10000000, 20000000))
