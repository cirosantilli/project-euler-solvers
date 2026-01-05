#!/usr/bin/env python3
import math
from collections import defaultdict
from functools import cmp_to_key
from math import isqrt


def comb3(n: int) -> int:
    return n * (n - 1) * (n - 2) // 6 if n >= 3 else 0


def half(v):
    x, y = v
    return 0 if (y > 0 or (y == 0 and x > 0)) else 1


def polar_cmp(a, b):
    ha, hb = half(a), half(b)
    if ha != hb:
        return -1 if ha < hb else 1
    ax, ay = a
    bx, by = b
    cross = ax * by - ay * bx
    if cross > 0:
        return -1
    if cross < 0:
        return 1
    da = ax * ax + ay * ay
    db = bx * bx + by * by
    return -1 if da < db else (1 if da > db else 0)


def angle_lt_pi(a, b) -> bool:
    ax, ay = a
    bx, by = b
    cross = ax * by - ay * bx
    if cross > 0:
        return True
    if cross < 0:
        return False
    dot = ax * bx + ay * by
    return dot > 0  # allow angle 0, exclude exactly π


def count_triangles(r: int) -> int:
    r2 = r * r
    ray = defaultdict(int)
    total_points = 0

    for x in range(-(r - 1), r):
        maxy2 = r2 - 1 - x * x
        if maxy2 < 0:
            continue
        ylim = isqrt(maxy2)
        for y in range(-ylim, ylim + 1):
            if x == 0 and y == 0:
                continue
            g = math.gcd(abs(x), abs(y))
            dx, dy = x // g, y // g
            ray[(dx, dy)] += 1
            total_points += 1

    vecs = list(ray.keys())
    weights = [ray[v] for v in vecs]

    order = sorted(
        range(len(vecs)), key=cmp_to_key(lambda i, j: polar_cmp(vecs[i], vecs[j]))
    )
    vecs = [vecs[i] for i in order]
    weights = [weights[i] for i in order]

    m = len(vecs)
    vecs2 = vecs + vecs
    weights2 = weights + weights

    pref = [0]
    for w in weights2:
        pref.append(pref[-1] + w)

    bad_open = 0
    j = 0
    for i in range(m):
        if j < i:
            j = i
        while j < i + m and angle_lt_pi(vecs[i], vecs2[j]):
            j += 1
        W = pref[j] - pref[i]
        wi = weights[i]
        bad_open += comb3(W) - comb3(W - wi)

    total = comb3(total_points)

    # subtract boundary cases (origin on an edge: opposite-direction pair)
    line_pos = defaultdict(int)
    line_neg = defaultdict(int)

    for (dx, dy), w in ray.items():
        if dx < 0 or (dx == 0 and dy < 0):
            line_neg[(-dx, -dy)] += w
        else:
            line_pos[(dx, dy)] += w

    boundary = 0
    for key in set(line_pos) | set(line_neg):
        P = line_pos.get(key, 0)
        Q = line_neg.get(key, 0)
        S = P + Q
        if P and Q:
            boundary += P * Q * (total_points - S)
            boundary += comb3(S) - comb3(P) - comb3(Q)

    return total - bad_open - boundary


def solve():
    return count_triangles(105)


if __name__ == "__main__":
    assert count_triangles(2) == 8
    assert count_triangles(3) == 360
    assert count_triangles(5) == 10600
    print(solve())
