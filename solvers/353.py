#!/usr/bin/env python3
"""
Project Euler 353 - Risky Moon

We have a sphere of radius r. Stations are integer-coordinate points on the sphere.
All stations are fully connected by shortest great-circle arcs.

Risk of an arc of central angle θ is (θ/π)^2.
Goal: minimal total risk from North Pole (0,0,r) to South Pole (0,0,-r).

This implementation treats the problem as a shortest-path search on an implicit graph:
nodes are lattice points on the sphere, edges are allowed between "nearby" nodes
(found by scanning a bounded window in (x,y) and solving for z via the sphere equation).

To remain practical for r up to 32767, we do not build the complete graph.
Instead we expand a local neighborhood radius (smax = max allowed squared chord length),
and iteratively enlarge until the answer stabilizes.

No external libraries are used.
"""

import math
import heapq


PI = math.pi


def is_square(n: int) -> int:
    """Return sqrt(n) if n is a perfect square, else -1."""
    if n < 0:
        return -1
    s = int(math.isqrt(n))
    return s if s * s == n else -1


def edge_risk_from_chord_sq(s: int, r: int, cache: dict) -> float:
    """
    Points p,q on sphere radius r satisfy:
        chord length d = |p-q|, d^2 = s
        central angle θ = 2 asin(d/(2r))
        risk = (θ/π)^2
    """
    v = cache.get(s)
    if v is None:
        # d/(2r) in [0,1]
        theta = 2.0 * math.asin(math.sqrt(s) / (2.0 * r))
        v = (theta / PI) ** 2
        cache[s] = v
    return v


def gen_offsets_xy(smax: int):
    """
    Precompute (dx,dy,dx^2+dy^2) for all integer offsets with dx^2+dy^2 <= smax,
    excluding (0,0) (handled separately by z-flip).
    """
    B = int(math.isqrt(smax))
    offsets = []
    for dx in range(-B, B + 1):
        dx2 = dx * dx
        for dy in range(-B, B + 1):
            if dx == 0 and dy == 0:
                continue
            ds = dx2 + dy * dy
            if ds <= smax:
                offsets.append((dx, dy, ds))
    return offsets


def neighbors(point, r: int, r2: int, smax: int, offsets):
    """
    Generate neighbors by changing x,y by small offsets and recomputing z from
    x'^2 + y'^2 + z'^2 = r^2.
    """
    x, y, z = point

    # Allow pure z-flip (same x,y) if within smax:
    if z != 0:
        s_flip = (2 * z) * (2 * z)
        if s_flip <= smax:
            yield (x, y, -z), s_flip

    for dx, dy, dsxy in offsets:
        x2 = x + dx
        y2 = y + dy

        # sphere equation -> z'^2
        t = r2 - x2 * x2 - y2 * y2
        if t < 0:
            continue
        zabs = is_square(t)
        if zabs < 0:
            continue

        # Both signs possible (unless zero)
        if zabs == 0:
            dz = -z
            s = dsxy + dz * dz
            if s <= smax:
                yield (x2, y2, 0), s
        else:
            # z' = +zabs
            dz = zabs - z
            s = dsxy + dz * dz
            if s <= smax:
                yield (x2, y2, zabs), s
            # z' = -zabs
            dz = -zabs - z
            s = dsxy + dz * dz
            if s <= smax:
                yield (x2, y2, -zabs), s


def bidirectional_dijkstra(r: int, smax: int) -> float:
    """
    Bidirectional Dijkstra on the implicit sparse graph (edges limited by smax).
    Returns minimal risk between poles, or inf if disconnected.
    """
    r2 = r * r
    start = (0, 0, r)
    goal = (0, 0, -r)

    offsets = gen_offsets_xy(smax)
    w_cache = {}  # chord_sq -> risk

    # Distances from both ends
    dist_f = {start: 0.0}
    dist_b = {goal: 0.0}
    pq_f = [(0.0, start)]
    pq_b = [(0.0, goal)]

    best = float("inf")

    # Helper for expanding one step
    def expand(pq, dist_this, dist_other):
        nonlocal best
        d, u = heapq.heappop(pq)
        if d != dist_this.get(u):
            return
        # If met
        other = dist_other.get(u)
        if other is not None:
            total = d + other
            if total < best:
                best = total

        # Relax neighbors
        for v, s in neighbors(u, r, r2, smax, offsets):
            nd = d + edge_risk_from_chord_sq(s, r, w_cache)
            if nd + 1e-18 < dist_this.get(v, float("inf")):
                dist_this[v] = nd
                heapq.heappush(pq, (nd, v))

    # Main loop
    while pq_f and pq_b:
        # Termination condition:
        if best < float("inf"):
            if pq_f[0][0] + pq_b[0][0] >= best - 1e-18:
                break

        # Expand the side with smaller frontier key
        if pq_f[0][0] <= pq_b[0][0]:
            expand(pq_f, dist_f, dist_b)
        else:
            expand(pq_b, dist_b, dist_f)

    return best


def compute_M(r: int) -> float:
    """
    Compute M(r) by growing neighborhood radius smax until the result stabilizes.

    Strategy:
      - Start with a modest smax.
      - Double until a path is found.
      - Then keep doubling while the best value improves noticeably.
    """
    smax = 256  # starting chord^2 window
    last = float("inf")

    # first ensure connectivity
    while True:
        val = bidirectional_dijkstra(r, smax)
        if val < float("inf"):
            last = val
            break
        smax *= 2

    # then enlarge until no meaningful improvement
    while True:
        smax *= 2
        val = bidirectional_dijkstra(r, smax)
        # if improvement is negligible, stop
        if not (val + 1e-13 < last):
            return last
        last = val


def main():
    # Problem test value:
    m7 = compute_M(7)
    # given: M(7)=0.1784943998 (rounded to 10 digits)
    assert f"{m7:.10f}" == "0.1784943998", (m7, f"{m7:.10f}")

    total = 0.0
    for n in range(1, 16):
        r = (1 << n) - 1
        total += compute_M(r)

    print(f"{total:.10f}")


if __name__ == "__main__":
    main()

