#!/usr/bin/env python3
"""
Project Euler 576: Irrational Jumps

We have a circle of circumference 1. Starting at 0, a point jumps by a fixed
irrational length l (counterclockwise), landing at x_k = frac(k*l).

A gap (an interval) of length g starts at position d (with 0 <= d < 1-g).
The point "falls into the gap" when x_k lies in [d, d+g).

For irrational l the hitting time is finite for all d; S(l,g,d) is the total
distance traveled until the first hit:
    S(l,g,d) = l * min{k>=1 : frac(k*l) in [d, d+g)}.

For M(n,g), we use l_p = sqrt(1/p) = 1/sqrt(p) for primes p<=n and choose d to
maximize sum_p S(l_p,g,d).

This program computes M(100, 0.00002) and prints it rounded to 4 decimals.
No external libraries are used.
"""

from __future__ import annotations

import math
import bisect
import heapq
from array import array


# ----------------------------
# Helpers: primes
# ----------------------------


def primes_up_to(n: int) -> list[int]:
    """Simple sieve of Eratosthenes."""
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    r = int(n**0.5)
    for i in range(2, r + 1):
        if sieve[i]:
            step = i
            start = i * i
            sieve[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i in range(2, n + 1) if sieve[i]]


# ----------------------------
# Core math
# ----------------------------


def S_slow(l: float, g: float, d: float, limit: int = 5_000_000) -> float:
    """
    Direct simulation for S(l,g,d). Used only for problem-statement asserts.
    Assumes d+g < 1.
    """
    x = 0.0
    for k in range(1, limit + 1):
        x += l
        x -= int(x)  # mod 1
        if d <= x < d + g:
            return k * l
    raise RuntimeError("S_slow: did not hit gap within limit")


def _build_piecewise_S_for_l(
    l: float, g: float, initial_factor: float = 1.5, max_k: int = 4_000_000
) -> tuple[array, array]:
    """
    Build the piecewise-constant function d -> S(l,g,d) on d in [0, 1-g).

    Representation:
        seg_ends[i] = end coordinate of segment i (strictly increasing),
        seg_vals[i] = constant value of S on that segment.
    Segment i covers [seg_ends[i-1], seg_ends[i]) (with seg_ends[-1] = 1-g).

    Technique:
    - For each jump k we form an interval of d values for which the k-th landing
      point lies in the gap: d in (x_k - g, x_k].
    - For fixed d, the hitting time K(d) is the minimum k whose interval contains d.
    - We discretize the d-axis by all interval endpoints, then assign each small cell
      its minimum k via a DSU "next-unassigned" structure (interval painting).

    We increase K until all d-cells are assigned (coverage is complete).
    """
    domain_end = 1.0 - g
    # Start with a modest multiple of 1/g; increase if needed.
    K = max(10, int(initial_factor / g))

    bl = bisect.bisect_left

    while True:
        if K > max_k:
            raise RuntimeError("Exceeded max_k while trying to cover domain")

        # Store interval endpoints and labels for k=1..K
        starts: list[float] = []
        ends: list[float] = []
        labels: list[int] = []
        endpoints: list[float] = [0.0, domain_end]

        x = 0.0
        for k in range(1, K + 1):
            x += l
            x -= int(x)  # mod 1, keep in [0,1)

            s = x - g
            e = x
            # Clip to d-domain [0, 1-g)
            if e <= 0.0 or s >= domain_end:
                continue
            if s < 0.0:
                s = 0.0
            if e > domain_end:
                e = domain_end
            if s < e:
                starts.append(s)
                ends.append(e)
                labels.append(k)
                endpoints.append(s)
                endpoints.append(e)

        endpoints.sort()
        # Unique endpoints (exact equality is enough here; duplicates are rare)
        pts: list[float] = [endpoints[0]]
        for v in endpoints[1:]:
            if v != pts[-1]:
                pts.append(v)

        num_cells = len(pts) - 1
        # DSU structure: next unassigned cell index
        parent = list(range(num_cells + 1))
        # Using an array for values reduces memory footprint notably for large cells.
        values = array("I", [0]) * num_cells

        def find(i: int) -> int:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        # Assign minimal k to each cell
        for s, e, k in zip(starts, ends, labels):
            i = bl(pts, s)
            j = bl(pts, e)
            idx = find(i)
            while idx < j:
                values[idx] = k
                parent[idx] = idx + 1
                idx = find(idx)

        # If all cells assigned, we have K(d) for all d and thus S(d)=l*K(d)
        if find(0) == num_cells:
            seg_ends = array("d")
            seg_vals = array("d")
            curr = values[0]
            for i in range(1, num_cells):
                if values[i] != curr:
                    seg_ends.append(pts[i])
                    seg_vals.append(curr * l)
                    curr = values[i]
            seg_ends.append(domain_end)
            seg_vals.append(curr * l)
            return seg_ends, seg_vals

        # Not fully covered: increase K and retry.
        K *= 2


def _merge_max_sum(
    seg_ends_list: list[array], seg_vals_list: list[array], domain_end: float
) -> float:
    """
    Given multiple piecewise-constant functions (all starting at 0 and ending at domain_end),
    compute the maximum of their sum over d.

    We merge the segment boundaries with a min-heap over current segment ends.
    """
    P = len(seg_ends_list)
    idx = [0] * P
    cur_val = [seg_vals_list[i][0] for i in range(P)]
    total = float(sum(cur_val))

    heap: list[tuple[float, int]] = []
    for i in range(P):
        heapq.heappush(heap, (seg_ends_list[i][0], i))

    cur_pos = 0.0
    best = total
    eps = 1e-15

    while heap:
        boundary = heap[0][0]

        # The sum is constant on [cur_pos, boundary)
        if boundary > cur_pos + 1e-18 and total > best:
            best = total

        affected: list[int] = []
        while heap and abs(heap[0][0] - boundary) <= eps:
            affected.append(heapq.heappop(heap)[1])

        cur_pos = boundary
        if cur_pos >= domain_end - 1e-15:
            break

        for i in affected:
            old = cur_val[i]
            idx[i] += 1
            new = seg_vals_list[i][idx[i]]
            cur_val[i] = new
            total += new - old
            new_end = seg_ends_list[i][idx[i]]
            heapq.heappush(heap, (new_end, i))

    return best


def M(n: int, g: float) -> float:
    """Compute M(n,g) as defined in the problem statement."""
    ps = primes_up_to(n)
    seg_ends_list: list[array] = []
    seg_vals_list: list[array] = []

    for p in ps:
        l = 1.0 / math.sqrt(p)  # sqrt(1/p)
        ends, vals = _build_piecewise_S_for_l(l, g)
        seg_ends_list.append(ends)
        seg_vals_list.append(vals)

    return _merge_max_sum(seg_ends_list, seg_vals_list, 1.0 - g)


# ----------------------------
# Problem-statement checks
# ----------------------------


def _assert_close(a: float, b: float, tol: float = 1e-4) -> None:
    assert abs(a - b) <= tol, (a, b)


def run_asserts() -> None:
    # Examples for S:
    l2 = math.sqrt(1.0 / 2.0)
    _assert_close(S_slow(l2, 0.06, 0.7), l2, 1e-4)
    _assert_close(S_slow(l2, 0.06, 0.3543), 2.0 * l2, 1e-4)
    _assert_close(S_slow(l2, 0.06, 0.2427), 16.2634559673, 1e-4)

    # Examples for M:
    _assert_close(M(3, 0.06), 29.5425121587, 1e-4)
    _assert_close(M(10, 0.01), 266.9010041160, 1e-4)


def main() -> None:
    run_asserts()
    ans = M(100, 0.00002)
    print(f"{ans:.4f}")


if __name__ == "__main__":
    main()
