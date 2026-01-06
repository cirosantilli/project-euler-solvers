from __future__ import annotations

import bisect
import heapq
import math
from typing import Dict, List, Tuple


def build_spf(limit: int) -> List[int]:
    spf = list(range(limit + 1))
    for i in range(2, int(limit**0.5) + 1):
        if spf[i] == i:
            for j in range(i * i, limit + 1, i):
                if spf[j] == j:
                    spf[j] = i
    return spf


def factor_small(n: int, spf: List[int]) -> Dict[int, int]:
    res: Dict[int, int] = {}
    while n > 1:
        p = spf[n]
        cnt = 0
        while n % p == 0:
            n //= p
            cnt += 1
        res[p] = cnt
    return res


def prime_representation(p: int) -> Tuple[int, int]:
    limit = int(math.isqrt(p))
    for a in range(1, limit + 1):
        b2 = p - a * a
        b = int(math.isqrt(b2))
        if b * b == b2:
            return a, b
    raise ValueError("prime is not a sum of two squares")


def mul_gaussian(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[int, int]:
    (x, y), (u, v) = a, b
    return x * u - y * v, x * v + y * u


def two_square_reps(
    n: int, factors: Dict[int, int], rep_cache: Dict[int, Tuple[int, int]]
) -> List[Tuple[int, int]]:
    if n == 0:
        return [(0, 0)]
    for p, e in factors.items():
        if p % 4 == 3 and e % 2 == 1:
            return []
    reps = {(1, 0)}
    for p, e in factors.items():
        if p % 4 == 3:
            scale = p ** (e // 2)
            reps = {(x * scale, y * scale) for x, y in reps}
            continue
        if p == 2:
            a, b = 1, 1
        else:
            a, b = rep_cache[p]
        g_pows = [(1, 0)]
        c_pows = [(1, 0)]
        for _ in range(1, e + 1):
            g_pows.append(mul_gaussian(g_pows[-1], (a, b)))
            c_pows.append(mul_gaussian(c_pows[-1], (a, -b)))
        opts = [mul_gaussian(g_pows[k], c_pows[e - k]) for k in range(e + 1)]
        new_reps = set()
        for x in reps:
            for y in opts:
                new_reps.add(mul_gaussian(x, y))
        reps = new_reps

    out: List[Tuple[int, int]] = []
    seen = set()
    for a, b in reps:
        for sa in (-1, 1):
            for sb in (-1, 1):
                x = sa * a
                y = sb * b
                if (x, y) not in seen:
                    out.append((x, y))
                    seen.add((x, y))
                if (y, x) not in seen:
                    out.append((y, x))
                    seen.add((y, x))
    return out


def generate_points(r: int) -> List[Tuple[int, int, int]]:
    spf = build_spf(2 * r)
    rep_cache: Dict[int, Tuple[int, int]] = {2: (1, 1)}
    for p in range(3, 2 * r + 1):
        if spf[p] == p and p % 4 == 1:
            rep_cache[p] = prime_representation(p)

    pts: List[Tuple[int, int, int]] = []
    for z in range(0, r + 1):
        a = r - z
        b = r + z
        n = a * b
        if n == 0:
            pairs = [(0, 0)]
        else:
            fac = factor_small(a, spf)
            fac2 = factor_small(b, spf)
            for p, e in fac2.items():
                fac[p] = fac.get(p, 0) + e
            pairs = two_square_reps(n, fac, rep_cache)
        for x, y in pairs:
            pts.append((x, y, z))
            if z != 0:
                pts.append((x, y, -z))
    return list(set(pts))


def minimal_risk(r: int, z_window: int, k_neighbors: int, k_max: int) -> float:
    pts = generate_points(r)
    n = len(pts)
    x = [p[0] for p in pts]
    y = [p[1] for p in pts]
    z = [p[2] for p in pts]
    idx = {p: i for i, p in enumerate(pts)}
    start = idx[(0, 0, r)]
    target = idx[(0, 0, -r)]

    by_z: Dict[int, List[int]] = {}
    angles_by_z: Dict[int, List[float]] = {}
    indices_by_z: Dict[int, List[int]] = {}
    phi = [math.atan2(y[i], x[i]) for i in range(n)]
    for i in range(n):
        by_z.setdefault(z[i], []).append(i)
    for zz, indices in by_z.items():
        indices.sort(key=lambda i: phi[i])
        indices_by_z[zz] = indices
        angles_by_z[zz] = [phi[i] for i in indices]

    z_levels = sorted(by_z.keys())
    dist = [1e100] * n
    dist[start] = 0.0
    heap: List[Tuple[float, int]] = [(0.0, start)]
    r2 = r * r
    inv_r2 = 1.0 / r2
    inv_pi = 1.0 / math.pi
    risk_cache: Dict[int, float] = {}

    while heap:
        d, i = heapq.heappop(heap)
        if d != dist[i]:
            continue
        if i == target:
            return d
        zi = z[i]
        min_z = zi - z_window
        max_z = zi + z_window
        start_idx = bisect.bisect_left(z_levels, min_z)
        end_idx = bisect.bisect_right(z_levels, max_z)
        phi_i = phi[i]
        xi = x[i]
        yi = y[i]
        for zz in z_levels[start_idx:end_idx]:
            indices = indices_by_z[zz]
            angles = angles_by_z[zz]
            m = len(indices)
            if zz == zi or m <= 2 * k_neighbors + 1:
                candidates = indices
            else:
                k = max(k_neighbors, m // 16)
                if k > k_max:
                    k = k_max
                pos = bisect.bisect_left(angles, phi_i)
                candidates = [
                    indices[(pos + offset) % m]
                    for offset in range(-k, k + 1)
                ]
            for j in candidates:
                if j == i:
                    continue
                dot = xi * x[j] + yi * y[j] + zi * z[j]
                w = risk_cache.get(dot)
                if w is None:
                    cosv = dot * inv_r2
                    if cosv > 1.0:
                        cosv = 1.0
                    elif cosv < -1.0:
                        cosv = -1.0
                    w = (math.acos(cosv) * inv_pi) ** 2
                    risk_cache[dot] = w
                nd = d + w
                if nd < dist[j]:
                    dist[j] = nd
                    heapq.heappush(heap, (nd, j))
    return dist[target]


def main() -> None:
    k_neighbors = 6
    k_max = 16
    r_test = 7
    z_window_test = max(10, 4 * math.isqrt(r_test) + 4)
    m7 = minimal_risk(r_test, z_window_test, k_neighbors, k_max)
    assert f"{m7:.10f}" == "0.1784943998"

    total = 0.0
    for n in range(1, 16):
        r = (1 << n) - 1
        z_window = max(10, 4 * math.isqrt(r) + 4)
        total += minimal_risk(r, z_window, k_neighbors, k_max)
    print(f"{total:.10f}")


if __name__ == "__main__":
    main()
