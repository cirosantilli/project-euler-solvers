#!/usr/bin/env python3
"""
Project Euler 456: Triangles containing the origin II

Compute C(n): the number of triangles with vertices among the first n generated points
that contain the origin strictly in their interior.

No external libraries are used.
"""

import math


# Bit-packing parameters for counting points on each *undirected* line through the origin.
# We store counts as: packed = a + (b << SHIFT)
# where a = number of points on the canonical direction, b = number on the opposite direction.
SHIFT = 21  # enough because n <= 2,000,000 < 2^21
MASK = (1 << SHIFT) - 1


def _comb3(k: int) -> int:
    """k choose 3."""
    return k * (k - 1) * (k - 2) // 6 if k >= 3 else 0


def _pack_point(x: int, y: int) -> int:
    """Pack two signed 32-bit ints into one Python int."""
    return ((x & 0xFFFFFFFF) << 32) | (y & 0xFFFFFFFF)


def _unpack_point(p: int) -> tuple[int, int]:
    """Unpack a point packed by _pack_point()."""
    x = (p >> 32) & 0xFFFFFFFF
    y = p & 0xFFFFFFFF
    if x >= 0x80000000:
        x -= 0x100000000
    if y >= 0x80000000:
        y -= 0x100000000
    return x, y


def solve(n: int) -> int:
    """
    Return C(n) for the point set P_n defined in the problem statement.
    """
    # Generate points and, at the same time, count points on each undirected line through the origin.
    modx, mody = 32323, 30103
    ax, ay = 1248, 8421
    x, y = 1, 1

    vecs: list[int] = []  # packed (x,y) for each point (excluding origin)
    line_counts: dict[int, int] = {}  # key -> packed counts (a + (b<<SHIFT))

    gcd = math.gcd
    for _ in range(n):
        x = (x * ax) % modx
        y = (y * ay) % mody
        px = x - 16161
        py = y - 15051

        # Points at the origin can never contribute to triangles containing the origin in the interior.
        if px == 0 and py == 0:
            continue

        vecs.append(_pack_point(px, py))

        g = gcd(abs(px), abs(py))
        dx = px // g
        dy = py // g

        # Canonical direction for the *undirected* line: (dx,dy) in the half-plane
        # dx > 0 or (dx == 0 and dy > 0).
        # side0=True means point lies on the canonical direction, else on the opposite direction.
        if dx > 0 or (dx == 0 and dy > 0):
            key_dx, key_dy = dx, dy
            side0 = True
        else:
            key_dx, key_dy = -dx, -dy
            side0 = False

        # Pack (key_dx, key_dy) into one int (both fit in 16 bits after constraints).
        key = (key_dx << 16) | ((key_dy + 32768) & 0xFFFF)

        prev = line_counts.get(key, 0)
        if side0:
            line_counts[key] = prev + 1
        else:
            line_counts[key] = prev + (1 << SHIFT)

    m = len(vecs)
    if m < 3:
        return 0

    total_triples = _comb3(m)

    # Sort by polar angle around the origin.
    atan2 = math.atan2

    def angle_key(p: int) -> float:
        xx = (p >> 32) & 0xFFFFFFFF
        yy = p & 0xFFFFFFFF
        if xx >= 0x80000000:
            xx -= 0x100000000
        if yy >= 0x80000000:
            yy -= 0x100000000
        return atan2(yy, xx)

    vecs.sort(key=angle_key)

    # Count triples contained in some open semicircle (< pi), i.e., triangles that do NOT
    # contain the origin in their convex hull.
    #
    # Standard two-pointer scan over the circularly-sorted directions:
    # For each i, find maximal j such that angle(i -> j) < pi (strict).
    # Then any choice of two points among the k = (j-i-1) points in that window,
    # together with i, forms a "bad" triple.
    open_semicircle_triples = 0
    j = 1

    for i in range(m):
        if j < i + 1:
            j = i + 1

        xi, yi = _unpack_point(vecs[i])

        while j < i + m:
            xj, yj = _unpack_point(vecs[j % m])

            # cross > 0  => CCW angle in (0, pi)
            # cross == 0 and dot > 0 => same ray (angle 0)
            cross = xi * yj - yi * xj
            if cross > 0:
                j += 1
                continue
            if cross == 0:
                dot = xi * xj + yi * yj
                if dot > 0:
                    j += 1
                    continue
            break

        k = j - i - 1
        open_semicircle_triples += k * (k - 1) // 2

    # Boundary triples: origin lies on an edge <=> the triple contains an antipodal pair
    # (two points on the same line through the origin, on opposite sides).
    antipodal_triples = 0
    for packed in line_counts.values():
        a = packed & MASK
        b = packed >> SHIFT
        if a == 0 or b == 0:
            continue
        t = a + b
        antipodal_triples += a * b * (m - t) + (_comb3(t) - _comb3(a) - _comb3(b))

    # Triangles with origin strictly inside = total - outside(hull doesn't contain) - boundary
    return total_triples - open_semicircle_triples - antipodal_triples


def main() -> None:
    # Test values from the problem statement
    assert solve(8) == 20
    assert solve(600) == 8950634
    assert solve(40_000) == 2666610948988

    print(solve(2_000_000))


if __name__ == "__main__":
    main()
