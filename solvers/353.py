#!/usr/bin/env python3
"""
Project Euler 353 - Risky Moon

Optimizations applied:
- Efficient generation of integer lattice points on the sphere using Hurwitz quaternions
  (primitive points) plus scaling by divisors of r.
- Sparse shortest-path: only consider edges between stations within a chord-distance
  threshold D (found via 3D bucket hashing).
- Bounded Dijkstra: maintain an upper bound "best" (found quickly via a small best-first
  search), and prune any relaxations/expansions with distance >= best.

No external libraries are used.
"""

import math
import heapq


PI = math.pi

# ------------------------------------------------------------
# Precompute (a,b) pairs for sums of two squares up to 4*MAX_R
# (used to build 4-square decompositions efficiently).
# ------------------------------------------------------------

MAX_R = (1 << 15) - 1
MAX_S = 4 * MAX_R
ROOT = int(math.isqrt(MAX_S))

pairs_all = [[] for _ in range(MAX_S + 1)]
pairs_odd = [[] for _ in range(MAX_S + 1)]

for a in range(-ROOT, ROOT + 1):
    a2 = a * a
    a_odd = a & 1
    for b in range(-ROOT, ROOT + 1):
        s = a2 + b * b
        if s <= MAX_S:
            pairs_all[s].append((a, b))
            if a_odd and (b & 1):
                pairs_odd[s].append((a, b))

sums_all = [i for i in range(MAX_S + 1) if pairs_all[i]]
sums_odd = [i for i in range(MAX_S + 1) if pairs_odd[i]]


# ------------------------------------------------------------
# Small helpers
# ------------------------------------------------------------

def gcd3(x, y, z):
    return math.gcd(math.gcd(abs(x), abs(y)), abs(z))


def factorize(n):
    f = {}
    x = n
    p = 2
    while p * p <= x:
        if x % p == 0:
            e = 0
            while x % p == 0:
                x //= p
                e += 1
            f[p] = e
        p += 1 if p == 2 else 2
    if x > 1:
        f[x] = 1
    return f


def divisors_from_factors(factors):
    ds = [1]
    for p, e in factors.items():
        base = ds[:]
        mul = 1
        for _ in range(e):
            mul *= p
            ds += [d * mul for d in base]
    return ds


# ------------------------------------------------------------
# Hurwitz quaternion parameterization of integer points on x^2+y^2+z^2=r^2
# ------------------------------------------------------------

def add_points_from_quaternion_int(a, b, c, d, out):
    aa = a * a
    bb = b * b
    cc = c * c
    dd = d * d
    # q i q̄
    out.add((aa + bb - cc - dd, 2 * (b * c + a * d), 2 * (b * d - a * c)))
    # q j q̄
    out.add((2 * (b * c - a * d), aa - bb + cc - dd, 2 * (c * d + a * b)))
    # q k q̄
    out.add((2 * (b * d + a * c), 2 * (c * d - a * b), aa + dd - bb - cc))


def add_points_from_quaternion_half(a, b, c, d, out):
    # Here a,b,c,d are odd; actual quaternion components are halves.
    aa = a * a
    bb = b * b
    cc = c * c
    dd = d * d
    out.add(((aa + bb - cc - dd) // 4, (b * c + a * d) // 2, (b * d - a * c) // 2))
    out.add(((b * c - a * d) // 2, (aa - bb + cc - dd) // 4, (c * d + a * b) // 2))
    out.add(((b * d + a * c) // 2, (c * d - a * b) // 2, (aa + dd - bb - cc) // 4))


primitive_cache = {}


def primitive_points(r):
    """All primitive integer points on x^2+y^2+z^2=r^2 (gcd(x,y,z)=1)."""
    hit = primitive_cache.get(r)
    if hit is not None:
        return hit

    pts = set()
    r2 = r * r

    # Integer quaternions: a^2+b^2+c^2+d^2 = r
    for s in sums_all:
        if s > r:
            break
        t = r - s
        L2 = pairs_all[t]
        if not L2:
            continue
        for a, b in pairs_all[s]:
            for c, d in L2:
                add_points_from_quaternion_int(a, b, c, d, pts)

    # Half-integer (Hurwitz) quaternions: odd a,b,c,d with a^2+b^2+c^2+d^2 = 4r
    target = 4 * r
    for s in sums_odd:
        if s > target:
            break
        t = target - s
        L2 = pairs_odd[t]
        if not L2:
            continue
        for a, b in pairs_odd[s]:
            for c, d in L2:
                add_points_from_quaternion_half(a, b, c, d, pts)

    prim = []
    for x, y, z in pts:
        if x * x + y * y + z * z == r2 and gcd3(x, y, z) == 1:
            prim.append((x, y, z))

    primitive_cache[r] = prim
    return prim


def all_points_on_sphere(r):
    """
    Any point has gcd g dividing r. Divide by g to get a primitive point on radius r/g.
    Therefore, for each d|r, scale primitive points on sphere(d) by r/d.
    """
    divs = divisors_from_factors(factorize(r))
    seen = set()
    pts = []
    for d in divs:
        scale = r // d
        for x, y, z in primitive_points(d):
            p = (x * scale, y * scale, z * scale)
            if p not in seen:
                seen.add(p)
                pts.append(p)
    return pts


# ------------------------------------------------------------
# Sparse bounded Dijkstra using 3D bucket hashing
# ------------------------------------------------------------

NEIGHBOR_OFFSETS_27 = [(dx, dy, dz)
                       for dx in (-1, 0, 1)
                       for dy in (-1, 0, 1)
                       for dz in (-1, 0, 1)]


def dijkstra_sparse_bounded(points, r, D):
    """
    Dijkstra over the neighbor graph where edges exist if chord length <= D.
    Uses:
      - 3D buckets (cell size D) to find neighbor candidates
      - bounded search: prune anything with distance >= current best
      - a quick best-first pass to find an initial feasible path and tighten 'best'
    """
    n = len(points)
    idx = {p: i for i, p in enumerate(points)}
    start = idx[(0, 0, r)]
    goal = idx[(0, 0, -r)]

    # Separate coordinate arrays for speed
    X = [0] * n
    Y = [0] * n
    Z = [0] * n
    for i, (x, y, z) in enumerate(points):
        X[i] = x
        Y[i] = y
        Z[i] = z

    r2 = r * r
    D2 = D * D

    # dot = p·q, and chord^2 = 2r^2 - 2dot
    # so chord^2 <= D^2 implies dot >= r^2 - D^2/2
    dot_min = r2 - (D2 // 2) - 1  # slightly loose, then exact check below

    # Buckets
    cell = D
    buckets = {}
    kx = [0] * n
    ky = [0] * n
    kz = [0] * n
    for i in range(n):
        bx = X[i] // cell
        by = Y[i] // cell
        bz = Z[i] // cell
        kx[i] = bx
        ky[i] = by
        kz[i] = bz
        buckets.setdefault((bx, by, bz), []).append(i)

    acos = math.acos
    risk_cache = {}

    def risk_from_dot(dot):
        w = risk_cache.get(dot)
        if w is None:
            c = dot / r2
            if c > 1.0:
                c = 1.0
            elif c < -1.0:
                c = -1.0
            theta = acos(c)
            w = (theta / PI) ** 2
            risk_cache[dot] = w
        return w

    gx, gy, gz = X[goal], Y[goal], Z[goal]

    # Quick best-first search to get an initial upper bound within this sparse graph.
    # Heuristic is direct arc risk to goal (not admissible; just for speed to find *a* path).
    def initial_upper_bound(max_expand=20000):
        bestg = {start: 0.0}
        dot0 = X[start] * gx + Y[start] * gy + Z[start] * gz
        heap = [(risk_from_dot(dot0), 0.0, start)]  # (f, g, node)
        pop = heapq.heappop
        push = heapq.heappush
        expanded = 0

        while heap and expanded < max_expand:
            f, g, u = pop(heap)
            if g != bestg.get(u):
                continue
            if u == goal:
                return g
            expanded += 1

            x1, y1, z1 = X[u], Y[u], Z[u]
            ux, uy, uz = kx[u], ky[u], kz[u]

            for ox, oy, oz in NEIGHBOR_OFFSETS_27:
                cand = buckets.get((ux + ox, uy + oy, uz + oz))
                if not cand:
                    continue
                for v in cand:
                    if v == u:
                        continue
                    dot = x1 * X[v] + y1 * Y[v] + z1 * Z[v]
                    if dot < dot_min:
                        continue
                    if 2 * r2 - 2 * dot > D2:
                        continue
                    g2 = g + risk_from_dot(dot)
                    prev = bestg.get(v)
                    if prev is None or g2 < prev - 1e-15:
                        bestg[v] = g2
                        dotg = X[v] * gx + Y[v] * gy + Z[v] * gz
                        h = risk_from_dot(dotg)
                        push(heap, (g2 + h, g2, v))

        return float("inf")

    best = initial_upper_bound()

    dist = [float("inf")] * n
    dist[start] = 0.0
    pq = [(0.0, start)]
    pop = heapq.heappop
    push = heapq.heappush

    while pq:
        d, u = pop(pq)
        if d != dist[u]:
            continue

        # Bound: if the smallest unsettled distance is already >= best, we are done.
        if d >= best:
            break

        if u == goal:
            return d

        x1, y1, z1 = X[u], Y[u], Z[u]
        ux, uy, uz = kx[u], ky[u], kz[u]

        for ox, oy, oz in NEIGHBOR_OFFSETS_27:
            cand = buckets.get((ux + ox, uy + oy, uz + oz))
            if not cand:
                continue
            for v in cand:
                if v == u:
                    continue
                dot = x1 * X[v] + y1 * Y[v] + z1 * Z[v]
                if dot < dot_min:
                    continue
                if 2 * r2 - 2 * dot > D2:
                    continue

                nd = d + risk_from_dot(dot)
                if nd >= best:
                    continue

                if nd < dist[v] - 1e-15:
                    dist[v] = nd
                    if v == goal and nd < best:
                        best = nd
                    push(pq, (nd, v))

    return best


def M(r):
    """
    Compute M(r) by choosing a neighbor threshold D large enough for connectivity
    and then refining slightly.

    Note: Increasing D can only decrease the sparse-graph optimum. We refine with
    a small factor to avoid very expensive runs at overly-large D.
    """
    pts = all_points_on_sphere(r)
    # Ensure poles are present
    if (0, 0, r) not in pts:
        pts.append((0, 0, r))
    if (0, 0, -r) not in pts:
        pts.append((0, 0, -r))

    # Start with a "local" threshold; increase until connected.
    D = max(6, int(2 * math.isqrt(r) + 4))
    val = dijkstra_sparse_bounded(pts, r, D)
    while val == float("inf"):
        D = int(D * 1.3) + 1
        val = dijkstra_sparse_bounded(pts, r, D)

    # Light refinement: small growth factor keeps runs cheap.
    refine_factor = 1.10
    while True:
        D2 = int(D * refine_factor) + 1
        val2 = dijkstra_sparse_bounded(pts, r, D2)
        if val2 < val - 1e-12:
            val, D = val2, D2
        else:
            break

    return val


def main():
    # Test value given in the problem statement:
    m7 = M(7)
    assert f"{m7:.10f}" == "0.1784943998", (m7, f"{m7:.10f}")

    total = 0.0
    for n in range(1, 16):
        r = (1 << n) - 1
        total += M(r)

    print(f"{total:.10f}")


if __name__ == "__main__":
    main()
