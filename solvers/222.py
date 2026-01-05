#!/usr/bin/env python3
"""
Project Euler 222: Sphere Packing

Pipe internal radius R=50mm, spheres radii 30..50mm.

Model reduction: consider a cross-section plane through the cylinder axis. Each sphere becomes a circle
between two parallel lines (pipe walls). For two tangent spheres of radii a and b placed on opposite
walls, the transverse separation of centers is:

    x = (R-a) + (R-b) = 2R - (a+b)

Since the center-to-center distance is (a+b), the axial separation is:

    y = sqrt((a+b)^2 - x^2) = sqrt(4R((a+b) - R))

Total pipe length for an order r0..rN-1 is:

    L = r0 + rN-1 + sum_i y(ri, r(i+1))

For this problem, the optimal order for consecutive radii with R=max is:
descending evens then ascending odds, i.e.
    50,48,46,...,30,31,33,...,49

We compute L precisely using Decimal and output round(L*1000) in micrometres (1mm=1000µm).
"""

from __future__ import annotations

from decimal import Decimal, ROUND_HALF_UP, getcontext
from itertools import permutations
from typing import List, Sequence


def axial_distance_mm(R: int, a: int, b: int) -> Decimal:
    """Axial distance between centers (mm) when balls a,b are tangent and touch opposite pipe walls."""
    s = Decimal(a + b)
    return (Decimal(4 * R) * (s - Decimal(R))).sqrt()


def construct_optimal_order(min_r: int, max_r: int) -> List[int]:
    """Descending evens then ascending odds for consecutive radii [min_r..max_r]."""
    evens_desc = list(range(max_r if max_r % 2 == 0 else max_r - 1, min_r - 1, -2))
    odds_asc = list(range(min_r if min_r % 2 == 1 else min_r + 1, max_r + 1, 2))
    return evens_desc + odds_asc


def pipe_length_mm(R: int, order: Sequence[int]) -> Decimal:
    if not order:
        return Decimal(0)
    total = Decimal(order[0] + order[-1])
    for a, b in zip(order, order[1:]):
        total += axial_distance_mm(R, a, b)
    return total


def brute_force_best_mm(R: int, radii: Sequence[int]) -> Decimal:
    """Brute-force minimum for tiny instances (internal self-check only)."""
    best = None
    for perm in permutations(radii):
        L = pipe_length_mm(R, perm)
        if best is None or L < best:
            best = L
    assert best is not None
    return best


def _self_checks() -> None:
    # No explicit sample/test values are provided in the Project Euler 222 statement.
    # These are internal checks to guard against implementation mistakes.

    getcontext().prec = 60

    # 1) Distance identity check
    def y_alt(R: int, a: int, b: int) -> Decimal:
        s = Decimal(a + b)
        return (s * s - (Decimal(2 * R) - s) ** 2).sqrt()

    for a, b in [(50, 48), (30, 50), (31, 49), (40, 41)]:
        assert abs(axial_distance_mm(50, a, b) - y_alt(50, a, b)) < Decimal("1e-45")

    # 2) Construction is optimal on a few tiny consecutive ranges (brute force)
    for min_r, max_r in [(5, 10), (6, 11), (7, 12)]:
        R = max_r
        radii = list(range(min_r, max_r + 1))
        order = construct_optimal_order(min_r, max_r)
        assert abs(pipe_length_mm(R, order) - brute_force_best_mm(R, radii)) < Decimal(
            "1e-30"
        )

    # 3) Feasibility: no overlaps in the final arrangement under alternating-wall placement
    R = 50
    order = construct_optimal_order(30, 50)

    x = []
    z = []
    curz = 0.0
    sign = 1.0
    for i, r in enumerate(order):
        x.append(sign * (R - r))
        z.append(curz)
        sign *= -1.0
        if i + 1 < len(order):
            curz += float(axial_distance_mm(R, r, order[i + 1]))

    # inside pipe
    for xi, ri in zip(x, order):
        assert abs(xi) <= (R - ri) + 1e-9

    # no intersections
    for i in range(len(order)):
        for j in range(i + 1, len(order)):
            dx = x[i] - x[j]
            dz = z[i] - z[j]
            dist2 = dx * dx + dz * dz
            min_dist = order[i] + order[j]
            assert dist2 + 1e-7 >= min_dist * min_dist


def solve() -> int:
    getcontext().prec = 80
    R = 50
    order = construct_optimal_order(30, 50)
    L_mm = pipe_length_mm(R, order)
    um = (L_mm * Decimal(1000)).quantize(Decimal(1), rounding=ROUND_HALF_UP)
    return int(um)


def main() -> None:
    _self_checks()
    print(solve())


if __name__ == "__main__":
    main()
