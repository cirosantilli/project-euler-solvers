#!/usr/bin/env python3
"""
Project Euler 292: Pythagorean Polygons

We count convex lattice polygons whose edges have integer length ("Pythagorean polygons"),
up to translation, with perimeter <= n.

Given in the problem:
P(4)  = 1
P(30) = 3655
P(60) = 891045
We must compute P(120).
"""

from __future__ import annotations

from math import gcd, isqrt
from typing import Dict, List, Tuple


def _primitive_pythagorean_triples(max_c: int) -> List[Tuple[int, int, int]]:
    """
    Generate all primitive Pythagorean triples (a,b,c) with c <= max_c using Euclid's formula.
    a, b > 0, gcd(a,b)=1, a^2 + b^2 = c^2.
    """
    triples: List[Tuple[int, int, int]] = []
    max_m = isqrt(max_c - 1) + 2  # since c = m^2 + n^2 >= m^2 + 1
    for m in range(2, max_m + 1):
        mm = m * m
        for n in range(1, m):
            if ((m - n) & 1) == 0:
                continue  # same parity => not primitive
            if gcd(m, n) != 1:
                continue
            a = mm - n * n
            b = 2 * m * n
            c = mm + n * n
            if c <= max_c:
                triples.append((a, b, c))
    return triples


def _upper_half_direction_groups(max_perim: int) -> List[Tuple[int, int, int]]:
    """
    Build all *directed* primitive lattice directions in the upper half-plane (y>0),
    plus the +x axis, whose lengths are integer.

    Each group is (dx, dy, c) where gcd(|dx|,|dy|)=1 and sqrt(dx^2+dy^2)=c (an integer).
    Choosing a scale s>=1 yields edge vector (s*dx, s*dy) with length s*c.
    """
    groups: List[Tuple[int, int, int]] = [(1, 0, 1), (0, 1, 1)]  # +x and +y axes
    for a, b, c in _primitive_pythagorean_triples(max_perim):
        # The 4 directions with dy>0 (upper half-plane)
        groups.extend([(a, b, c), (-a, b, c), (b, a, c), (-b, a, c)])
    return groups


def _build_half_dp(
    max_perim: int,
) -> Tuple[List[Dict[int, int]], List[Tuple[int, int, int]], int, int, int]:
    """
    DP over the *upper* half-plane directions only.

    dp[p][key] = number of ways to choose one scaled vector from some directions (or none),
                with total length p and total displacement encoded by `key`.

    Key packing:
      key = (x + O) * W + (y + O), where O=max_perim and W=2*max_perim+1,
      so x,y are safely in [-max_perim, +max_perim].

    We later use symmetry: the lower half-plane choices correspond to negating displacements,
    and because we only ever need to match displacement vectors, we can reuse the same dp.
    """
    groups = _upper_half_direction_groups(max_perim)

    O = max_perim
    W = 2 * max_perim + 1
    origin = O * W + O

    dp: List[Dict[int, int]] = [{} for _ in range(max_perim + 1)]
    dp[0][origin] = 1

    # For each direction group, we may select at most one scale s>=1 (or skip).
    # To enforce "at most one", we freeze the current dp states (base) once per group,
    # then add each scale choice based only on the frozen base.
    for dx, dy, c in groups:
        max_scale = max_perim // c
        lens = [c * s for s in range(1, max_scale + 1)]
        deltas = [dx * s * W + dy * s for s in range(1, max_scale + 1)]

        base: List[List[Tuple[int, int]] | None] = [None] * (max_perim + 1)
        for p in range(max_perim + 1):
            if dp[p]:
                base[p] = list(dp[p].items())

        for length, delta in zip(lens, deltas):
            limit = max_perim - length
            for p in range(limit + 1):
                items = base[p]
                if not items:
                    continue
                dest = dp[p + length]
                get = dest.get
                for key, cnt in items:
                    k2 = key + delta
                    dest[k2] = get(k2, 0) + cnt

    return dp, groups, O, W, origin


def _count_polygons_from_half_dp(
    n: int, dp: List[Dict[int, int]], groups: List[Tuple[int, int, int]]
) -> int:
    """
    Use the half-plane dp to count full polygons with perimeter <= n.

    Let U be the multiset of chosen upper-half edges (displacement vector v, perimeter p1),
    and L be chosen lower-half edges (displacement -v, perimeter p2).
    Then p1+p2 <= n and v must match.

    Symmetry:
      the lower-half direction set is exactly the negation of the upper-half set, so the
      number of ways to reach a vector v in the upper half equals the number of ways to
      reach -v in the lower half. Therefore we can reuse the same dp and just match keys.

    We subtract invalid degenerate "polygons":
      - the empty selection (0 edges),
      - 2-edge back-and-forth segments (v and -v).
    """
    total = 0

    for p1 in range(n + 1):
        d1 = dp[p1]
        if not d1:
            continue
        for p2 in range(n + 1 - p1):
            d2 = dp[p2]
            if not d2:
                continue

            # Iterate the smaller dict for speed.
            if len(d1) <= len(d2):
                for key, c1 in d1.items():
                    c2 = d2.get(key)
                    if c2:
                        total += c1 * c2
            else:
                for key, c2 in d2.items():
                    c1 = d1.get(key)
                    if c1:
                        total += c1 * c2

    # Remove the empty selection (not a polygon).
    total -= 1

    # Remove 2-edge degenerates: choose one directed edge v in the upper half and -v in the lower.
    # For a direction with primitive length c, there are floor(n/(2c)) valid scales s with 2*s*c <= n.
    total -= sum(n // (2 * c) for _dx, _dy, c in groups)

    return total


def solve(n: int = 120) -> int:
    """
    Return P(n).

    The original problem asks for P(120).
    """
    # Build DP once for max_perim >= max(n, 60) so we can assert the provided test values.
    max_perim = max(n, 60)
    dp, groups, _O, _W, _origin = _build_half_dp(max_perim)

    # Problem statement checks
    assert _count_polygons_from_half_dp(4, dp, groups) == 1
    assert _count_polygons_from_half_dp(30, dp, groups) == 3655
    assert _count_polygons_from_half_dp(60, dp, groups) == 891045

    return _count_polygons_from_half_dp(n, dp, groups)


if __name__ == "__main__":
    print(solve(120))
