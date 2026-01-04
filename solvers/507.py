#!/usr/bin/env python3
"""
Project Euler 507: Shortest Lattice Vector

Let V_n and W_n be the two lattice basis vectors defined from the tribonacci residues r_i in the problem
statement. For each n, define S(n) as the minimum Manhattan length (L1 norm) among all non-zero lattice
vectors k*V_n + l*W_n with k,l integers.

This program computes:
    sum_{n=1..20_000_000} S(n)

No external libraries are used.
"""

MOD = 10_000_000
N = 20_000_000


def _best_m(a1: int, a2: int, a3: int, b1: int, b2: int, b3: int, nb: int) -> int:
    """
    Choose integer m that minimizes ||(b1,b2,b3) - m*(a1,a2,a3)||_1.

    For real m, this is a weighted median of the three ratios b_i/a_i with weights |a_i|.
    We use that (in almost all calls) a1,a2,a3 are non-zero, and find the weighted median among 3 fractions
    with a tiny sorting network. The integer minimizer is among floor/ceil of the median ratio (and possibly
    the adjacent ratio in the rare tie case).
    """
    bestm = 0
    bestv = nb  # value at m=0

    # Fast path: all three denominators non-zero (overwhelmingly common).
    if a1 and a2 and a3:
        # Normalize each fraction so denominator is positive.
        n0, d0 = b1, a1
        if d0 < 0:
            d0 = -d0
            n0 = -n0

        n1, d1 = b2, a2
        if d1 < 0:
            d1 = -d1
            n1 = -n1

        n2, d2 = b3, a3
        if d2 < 0:
            d2 = -d2
            n2 = -n2

        # Sort by ratio n/d using a 3-item sorting network.
        if n1 * d0 < n0 * d1:
            n0, n1 = n1, n0
            d0, d1 = d1, d0
        if n2 * d1 < n1 * d2:
            n1, n2 = n2, n1
            d1, d2 = d2, d1
            if n1 * d0 < n0 * d1:
                n0, n1 = n1, n0
                d0, d1 = d1, d0

        # Here weights are |a_i|, and after normalization those equal the denominators d0,d1,d2.
        tot = d0 + d1 + d2

        # Identify the weighted median ratio (and the adjacent one if we land exactly on half).
        candn1 = n0
        candd1 = d0
        candn2 = 0
        candd2 = 0

        cum = d0
        if cum * 2 > tot:
            candn1, candd1 = n0, d0
        elif cum * 2 == tot:
            candn1, candd1 = n0, d0
            candn2, candd2 = n1, d1
        else:
            cum += d1
            if cum * 2 > tot:
                candn1, candd1 = n1, d1
            elif cum * 2 == tot:
                candn1, candd1 = n1, d1
                candn2, candd2 = n2, d2
            else:
                candn1, candd1 = n2, d2

        # Evaluate candidate integers around the median ratio.
        q = candn1 // candd1
        if q:
            v = abs(b1 - q * a1) + abs(b2 - q * a2) + abs(b3 - q * a3)
            if v < bestv:
                bestv = v
                bestm = q
        qp = q + 1
        if qp:
            v = abs(b1 - qp * a1) + abs(b2 - qp * a2) + abs(b3 - qp * a3)
            if v < bestv:
                bestv = v
                bestm = qp

        if candd2:
            q2 = candn2 // candd2
            if q2 != q:
                if q2:
                    v = abs(b1 - q2 * a1) + abs(b2 - q2 * a2) + abs(b3 - q2 * a3)
                    if v < bestv:
                        bestv = v
                        bestm = q2
                q2p = q2 + 1
                if q2p:
                    v = abs(b1 - q2p * a1) + abs(b2 - q2p * a2) + abs(b3 - q2p * a3)
                    if v < bestv:
                        bestv = v
                        bestm = q2p

        return bestm

    # Rare fallback: one or more a_i are zero. Just test floor/ceil of each defined ratio.
    if a1:
        q = b1 // a1
        if q:
            v = abs(b1 - q * a1) + abs(b2 - q * a2) + abs(b3 - q * a3)
            if v < bestv:
                bestv = v
                bestm = q
        qp = q + 1
        if qp:
            v = abs(b1 - qp * a1) + abs(b2 - qp * a2) + abs(b3 - qp * a3)
            if v < bestv:
                bestv = v
                bestm = qp

    if a2:
        q = b2 // a2
        if q:
            v = abs(b1 - q * a1) + abs(b2 - q * a2) + abs(b3 - q * a3)
            if v < bestv:
                bestv = v
                bestm = q
        qp = q + 1
        if qp:
            v = abs(b1 - qp * a1) + abs(b2 - qp * a2) + abs(b3 - qp * a3)
            if v < bestv:
                bestv = v
                bestm = qp

    if a3:
        q = b3 // a3
        if q:
            v = abs(b1 - q * a1) + abs(b2 - q * a2) + abs(b3 - q * a3)
            if v < bestv:
                bestv = v
                bestm = q
        qp = q + 1
        if qp:
            v = abs(b1 - qp * a1) + abs(b2 - qp * a2) + abs(b3 - qp * a3)
            if v < bestv:
                bestv = v
                bestm = qp

    return bestm


def _shortest_l1(v1: int, v2: int, v3: int, w1: int, w2: int, w3: int) -> int:
    """
    Compute S(n) for a single pair of basis vectors using 2D lattice reduction in the L1 norm.
    """
    a1, a2, a3 = v1, v2, v3
    b1, b2, b3 = w1, w2, w3

    # Degenerate safety (extremely unlikely for this construction, but harmless).
    if (a1 | a2 | a3) == 0:
        return abs(b1) + abs(b2) + abs(b3)
    if (b1 | b2 | b3) == 0:
        return abs(a1) + abs(a2) + abs(a3)

    # L1-analog of Lagrange/Minkowski reduction for rank-2 lattices.
    # In practice, this converges in just a few iterations.
    for _ in range(12):
        na = abs(a1) + abs(a2) + abs(a3)
        nb = abs(b1) + abs(b2) + abs(b3)

        if nb < na:
            a1, a2, a3, b1, b2, b3 = b1, b2, b3, a1, a2, a3
            na, nb = nb, na

        m = _best_m(a1, a2, a3, b1, b2, b3, nb)
        if m == 0:
            break

        b1 -= m * a1
        b2 -= m * a2
        b3 -= m * a3

    # In a reduced 2D basis, the shortest vector is among a, b, a+b, a-b.
    s = abs(a1) + abs(a2) + abs(a3)
    t = abs(b1) + abs(b2) + abs(b3)
    if t and t < s:
        s = t

    p1, p2, p3 = a1 + b1, a2 + b2, a3 + b3
    t = abs(p1) + abs(p2) + abs(p3)
    if t and t < s:
        s = t

    p1, p2, p3 = a1 - b1, a2 - b2, a3 - b3
    t = abs(p1) + abs(p2) + abs(p3)
    if t and t < s:
        s = t

    return s


def solve(limit: int = N) -> int:
    # Generate tribonacci residues r_i modulo MOD, streaming without storing.
    # Residues always satisfy 0 <= r_i < MOD, so each next value is in [0, 3*MOD).
    x0, x1, x2 = 0, 0, 1  # r0, r1, r2

    total = 0
    sum10 = 0
    s1 = None

    # First block uses r1 and r2 that already exist.
    r1 = x1
    r2 = x2

    # Generate r3..r12 (10 steps). Use subtraction instead of % because sum < 3*MOD.
    def step():
        nonlocal x0, x1, x2
        t = x0 + x1 + x2
        if t >= MOD:
            t -= MOD
            if t >= MOD:
                t -= MOD
        x0, x1, x2 = x1, x2, t
        return t

    r3 = step()
    r4 = step()
    r5 = step()
    r6 = step()
    r7 = step()
    r8 = step()
    r9 = step()
    r10 = step()
    r11 = step()
    r12 = step()

    s = _shortest_l1(r1 - r2, r3 + r4, r5 * r6, r7 - r8, r9 + r10, r11 * r12)
    total += s
    sum10 += s
    s1 = s

    # Remaining blocks. Each block needs 12 new residues.
    for n in range(2, limit + 1):
        r1 = step()
        r2 = step()
        r3 = step()
        r4 = step()
        r5 = step()
        r6 = step()
        r7 = step()
        r8 = step()
        r9 = step()
        r10 = step()
        r11 = step()
        r12 = step()

        s = _shortest_l1(r1 - r2, r3 + r4, r5 * r6, r7 - r8, r9 + r10, r11 * r12)
        total += s
        if n <= 10:
            sum10 += s

    # Problem statement checks
    assert s1 == 32
    assert sum10 == 130762273722

    return total


if __name__ == "__main__":
    print(solve())
