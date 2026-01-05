from __future__ import annotations

import math
from typing import Dict, List, Tuple, Union


def egcd(a: int, b: int) -> Tuple[int, int, int]:
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)


def t_interval(
    u: int,
    v: int,
    ax: int,
    ay: int,
    r2: int,
    x0: int,
    y0: int,
) -> Union[Tuple[int, int], None]:
    s = u * u + v * v
    dx = x0 - ax
    dy = y0 - ay
    a = s
    b = 2 * (u * dx + v * dy)
    c = dx * dx + dy * dy - r2
    d = b * b - 4 * a * c
    if d <= 0:
        return None
    sqrt_d = int(math.isqrt(d))
    q2 = 2 * a
    p1 = -b - sqrt_d
    p2 = -b + sqrt_d
    # strict inequality: t in (root1, root2)
    t_min = -((-p1) // q2)  # ceil
    t_max = (p2 - 1) // q2  # strict upper bound
    if t_min > t_max:
        return None
    return (t_min, t_max)


def line_has_point(u: int, v: int, m: int, k: int, p: int, q: int) -> bool:
    s = u * u + v * v
    ax = (u - m * v) // 2
    ay = (v + m * u) // 2
    bx = (u + m * v) // 2
    by = (v - m * u) // 2
    r2 = s * (1 + m * m) // 4
    x0 = -k * q
    y0 = k * p
    ia = t_interval(u, v, ax, ay, r2, x0, y0)
    if ia is None:
        return False
    ib = t_interval(u, v, bx, by, r2, x0, y0)
    if ib is None:
        return False
    t_min = max(ia[0], ib[0])
    t_max = min(ia[1], ib[1])
    return t_min <= t_max


def min_m_for_rep(u: int, v: int, m_max: int) -> Union[int, None]:
    s = u * u + v * v
    g, p, q = egcd(u, v)
    if g != 1:
        return None
    # p, q satisfy u * p + v * q = 1
    m = 1
    while m <= m_max:
        k_max = int(math.floor(s / (2.0 * (math.sqrt(1 + m * m) + m))))
        if k_max == 0:
            return m
        ok = True
        for k in range(1, k_max + 1):
            if line_has_point(u, v, m, k, p, q):
                ok = False
                break
        if ok:
            return m
        m += 2
    return None


def add_s(mapping: Dict[int, Union[int, Tuple[int, ...]]], r2: int, s: int) -> None:
    val = mapping.get(r2)
    if val is None:
        mapping[r2] = s
        return
    if isinstance(val, int):
        if val == s:
            return
        if val < s:
            mapping[r2] = (val, s)
        else:
            mapping[r2] = (s, val)
        return
    # val is a tuple
    if s in val:
        return
    mapping[r2] = val + (s,)


def intersects(a: Tuple[int, ...], b: Tuple[int, ...]) -> bool:
    i = 0
    j = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            return True
        if a[i] < b[j]:
            i += 1
        else:
            j += 1
    return False


def compute_l(N: int) -> int:
    # Conservative upper bound for s; m0 grows at least like sqrt(s), so s above 4N
    # cannot fit m0 <= m_max in practice. This keeps the search finite.
    s_limit = 4 * N
    max_uv = int(math.isqrt(s_limit))

    s_to_reps: Dict[int, List[Tuple[int, int]]] = {}
    for u in range(1, max_uv + 1, 2):
        u2 = u * u
        v_limit = int(math.isqrt(s_limit - u2))
        for v in range(1, v_limit + 1, 2):
            if math.gcd(u, v) != 1:
                continue
            s = u2 + v * v
            if s > s_limit:
                continue
            s_to_reps.setdefault(s, []).append((u, v))

    r_map: Dict[int, Union[int, Tuple[int, ...]]] = {}

    for s, reps in s_to_reps.items():
        m_max_sq = (4 * N * N) // s - 1
        if m_max_sq < 1:
            continue
        m_max = int(math.isqrt(m_max_sq))
        if m_max < 1:
            continue
        m0 = None
        for u, v in reps:
            m_rep = min_m_for_rep(u, v, m_max)
            if m_rep is None:
                continue
            if m0 is None or m_rep < m0:
                m0 = m_rep
        if m0 is None:
            continue
        for m in range(m0, m_max + 1, 2):
            r2 = s * (1 + m * m) // 4
            add_s(r_map, r2, s)

    single_count: Dict[int, int] = {}
    multi_count: Dict[Tuple[int, ...], int] = {}
    for val in r_map.values():
        if isinstance(val, int):
            single_count[val] = single_count.get(val, 0) + 1
            continue
        sset = tuple(sorted(val))
        multi_count[sset] = multi_count.get(sset, 0) + 1

    total = 0
    for c in single_count.values():
        total += c * (c + 1) // 2
    for c in multi_count.values():
        total += c * (c + 1) // 2

    for sset, c in multi_count.items():
        sum_single = 0
        for s in sset:
            sum_single += single_count.get(s, 0)
        total += c * sum_single

    multi_items = list(multi_count.items())
    for i in range(len(multi_items)):
        sset_i, c_i = multi_items[i]
        for j in range(i + 1, len(multi_items)):
            sset_j, c_j = multi_items[j]
            if intersects(sset_i, sset_j):
                total += c_i * c_j

    return total


def main() -> None:
    assert compute_l(10) == 30
    assert compute_l(100) == 3442
    result = compute_l(100000)
    print(result)


if __name__ == "__main__":
    main()
