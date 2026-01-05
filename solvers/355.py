#!/usr/bin/env python3
"""
Project Euler 355 - Maximal Coprime Subset

Compute Co(n): the maximal possible sum of a set of mutually coprime elements
from {1,2,...,n}.

No external libraries are used.
"""

from __future__ import annotations

import math
import heapq
from typing import List, Tuple


def primes_upto(n: int) -> List[int]:
    """Sieve of Eratosthenes, returns all primes <= n."""
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    r = int(math.isqrt(n))
    for p in range(2, r + 1):
        if sieve[p]:
            start = p * p
            step = p
            sieve[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i in range(2, n + 1) if sieve[i]]


def max_power_leq(p: int, limit: int) -> int:
    """Largest power p^k (k>=1) such that p^k <= limit."""
    x = p
    while x * p <= limit:
        x *= p
    return x


class MinCostMaxFlow:
    """
    Successive shortest augmenting path (with potentials) min-cost flow.
    Works well here because we only send a small amount of flow (<= #small primes),
    and all capacities are 0/1.
    """

    __slots__ = ("n", "g")

    def __init__(self, n: int):
        self.n = n
        # edge: [to, cap, cost, rev_index]
        self.g: List[List[List[int]]] = [[] for _ in range(n)]

    def add_edge(self, fr: int, to: int, cap: int, cost: int) -> None:
        self.g[fr].append([to, cap, cost, len(self.g[to])])
        self.g[to].append([fr, 0, -cost, len(self.g[fr]) - 1])

    def min_cost_flow(self, s: int, t: int, f: int) -> Tuple[int, int]:
        n = self.n
        g = self.g
        INF = 10**30

        pot = [0] * n  # potentials
        prev_v = [0] * n
        prev_e = [0] * n

        flow = 0
        cost_total = 0

        while flow < f:
            dist = [INF] * n
            dist[s] = 0
            pq = [(0, s)]

            while pq:
                d, v = heapq.heappop(pq)
                if d != dist[v]:
                    continue
                for ei, e in enumerate(g[v]):
                    to, cap, cost, _rev = e
                    if cap <= 0:
                        continue
                    nd = d + cost + pot[v] - pot[to]
                    if nd < dist[to]:
                        dist[to] = nd
                        prev_v[to] = v
                        prev_e[to] = ei
                        heapq.heappush(pq, (nd, to))

            if dist[t] >= INF:
                break  # cannot send more

            # Update potentials
            for v in range(n):
                if dist[v] < INF:
                    pot[v] += dist[v]

            # Augment (all caps are 1, but keep generic)
            add = f - flow
            v = t
            while v != s:
                u = prev_v[v]
                ei = prev_e[v]
                add = min(add, g[u][ei][1])
                v = u

            v = t
            while v != s:
                u = prev_v[v]
                ei = prev_e[v]
                e = g[u][ei]
                e[1] -= add
                rev = e[3]
                g[v][rev][1] += add
                cost_total += add * e[2]
                v = u

            flow += add

        return flow, cost_total


def co(n: int) -> int:
    """
    Compute Co(n).

    Key reduction used here (sufficient for this Euler problem):
    Any product of two distinct primes <= n must include a prime <= sqrt(n).
    We treat primes <= sqrt(n) as the "small" side, and allow pairing each small prime
    with at most one prime > sqrt(n) (and <= n/2), maximizing total improvement over
    the baseline set of prime powers.
    """
    primes = primes_upto(n)
    if not primes:
        return 1 if n >= 1 else 0

    # Baseline: take the largest prime power for each prime; they are mutually coprime.
    v = {p: max_power_leq(p, n) for p in primes}
    baseline = 1 + sum(v.values())

    sqrt_n = int(math.isqrt(n))
    small = [p for p in primes if p <= sqrt_n]
    big = [
        p for p in primes if p > sqrt_n and p <= n // 2
    ]  # primes > n/2 can't pair with any >=2

    s = len(small)
    t = len(big)
    if s == 0 or t == 0:
        return baseline

    # Precompute powers for each small prime to query max p^k <= limit quickly.
    small_pows: List[List[int]] = []
    for p in small:
        pw = [p]
        while pw[-1] * p <= n:
            pw.append(pw[-1] * p)
        small_pows.append(pw)

    # Collect all positive-gain edges and determine a shift C to keep costs non-negative.
    edges: List[Tuple[int, int, int]] = []
    max_gain = 0

    for j, q in enumerate(big):
        limit = n // q
        # Only small primes <= limit can pair with q.
        for i, p in enumerate(small):
            if p > limit:
                break
            pw = small_pows[i]

            # Largest p^k <= limit (pw is increasing and very short)
            pa = pw[-1]
            if pa > limit:
                for val in reversed(pw):
                    if val <= limit:
                        pa = val
                        break

            m = pa * q
            gain = m - v[p] - q  # improvement over taking p^* and q separately
            if gain > 0:
                edges.append((i, j, gain))
                if gain > max_gain:
                    max_gain = gain

    if max_gain == 0:
        return baseline

    C = max_gain  # cost shift: cost = C-gain (>=0), unmatched cost = C

    # Build min-cost flow network to find max-gain matching.
    # Nodes: SRC, small nodes, big nodes, SNK
    SRC = 0
    offset_small = 1
    offset_big = offset_small + s
    SNK = offset_big + t
    mcmf = MinCostMaxFlow(SNK + 1)

    # SRC -> small (cap 1)
    # small -> SNK (cap 1, cost C)  means "leave small prime unpaired"
    for i in range(s):
        mcmf.add_edge(SRC, offset_small + i, 1, 0)
        mcmf.add_edge(offset_small + i, SNK, 1, C)

    # big -> SNK (cap 1, cost 0) ensures each big prime is used at most once
    for j in range(t):
        mcmf.add_edge(offset_big + j, SNK, 1, 0)

    # small -> big edges (cap 1, cost C-gain)
    for i, j, gain in edges:
        mcmf.add_edge(offset_small + i, offset_big + j, 1, C - gain)

    flow, min_cost = mcmf.min_cost_flow(SRC, SNK, s)
    # We always can send all s units because each small has an edge to SNK.
    # Total min_cost = C*s - total_gain
    total_gain = C * s - min_cost
    return baseline + total_gain


def solve() -> None:
    print(co(200000))


if __name__ == "__main__":
    # Test values from the problem statement
    assert co(10) == 30
    assert co(30) == 193
    assert co(100) == 1356

    solve()
