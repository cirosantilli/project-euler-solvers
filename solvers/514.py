#!/usr/bin/env python3
"""
Project Euler 514 - Geoboard Shapes

A geoboard (of order N) is a square board with pins at integer lattice points
0 <= x,y <= N. Each pin is independently placed with probability p = 1/(N+1).
Let S be the convex hull of the selected pins. Let E(N) be the expected area of S.

This program prints E(100) rounded to 5 decimal places.

No external libraries are used.
"""
from math import gcd


def expected_area(N: int) -> float:
    """
    Compute E(N) as a float.

    Outline of the method:
    - Use the shoelace/Green theorem form: Area = 1/2 * sum cross(v_i, v_{i+1})
    - By linearity of expectation, sum expected cross-contributions of hull edges
      over all primitive edge directions.
    - For a primitive direction u=(a,b), hull edges lie on supporting lines
      b*x - a*y = t. For each such line we can compute:
        P(no selected points on lines with larger t) * P(at least one selected point
        on lines with smaller t) * E(contribution from consecutive selected points on the line)
    - The expected contribution on a line depends only on L = number of lattice points
      on that line segment inside the square, and can be precomputed for L=0..N+1.
    - Exploit D4 (8-fold) symmetry: enumerate primitive directions in one octant and
      multiply by 8 (or 4 for axes/diagonals).
    """
    if N < 0:
        raise ValueError("N must be non-negative")

    M = N + 1
    if M == 1:
        return 0.0

    p = 1.0 / M
    q = 1.0 - p
    total_points = M * M

    # q^k and (1 - q^k)
    qpow = [1.0] * (total_points + 1)
    for k in range(1, total_points + 1):
        qpow[k] = qpow[k - 1] * q
    one_minus_qpow = [0.0] * (total_points + 1)
    for k in range(total_points + 1):
        one_minus_qpow[k] = 1.0 - qpow[k]

    # Precompute floor divisions needed for line-length clamps.
    ky_table = [None] * (N + 1)
    ky_table[0] = [10**9] * M  # dummy for b=0
    for b in range(1, N + 1):
        ky = [0] * M
        for y in range(M):
            ky[y] = (N - y) // b
        ky_table[b] = ky

    kx_table = [None] * (N + 1)
    ayoff_table = [None] * (N + 1)
    for a in range(1, N + 1):
        kx = [0] * M
        ayoff = [0] * M
        for x in range(M):
            kx[x] = (N - x) // a
        for y in range(M):
            ayoff[y] = a * (N - y)
        kx_table[a] = kx
        ayoff_table[a] = ayoff

    # Precompute p^2 * S(L), where S(L)=sum_{d=1..L-1} d*(L-d)*q^{d-1}.
    qpow_small = [1.0] * (M + 1)
    for k in range(1, M + 1):
        qpow_small[k] = qpow_small[k - 1] * q
    p2 = p * p
    p2S = [0.0] * (M + 1)
    for L in range(2, M + 1):
        s = 0.0
        for d in range(1, L):
            s += d * (L - d) * qpow_small[d - 1]
        p2S[L] = p2 * s

    # Accumulate expected cross-sum using centered coordinates scaled by 2.
    # Final area = total_cross_scaled / 8.
    total_cross_scaled = 0.0

    # Local bindings
    qpow_local = qpow
    omq_local = one_minus_qpow
    p2S_local = p2S
    ky_tab = ky_table
    kx_tab = kx_table
    ay_tab = ayoff_table
    M_local = M
    N_local = N
    total_points_local = total_points

    # Primitive directions in one octant: a >= b >= 0, gcd(a,b)=1.
    for a in range(1, N_local + 1):
        kx_a = kx_tab[a]
        ay_a = ay_tab[a]
        for b in range(0, a + 1):
            if gcd(a, b) != 1:
                continue
            if b == 0 and a != 1:
                continue  # only primitive axis direction is (1,0)

            mult = 4 if (b == 0 or a == b) else 8

            # Special-case horizontal direction (1,0): each line has L=M points.
            if b == 0:
                above = 0
                dir_sum = 0.0
                min_t = -a * N_local  # t = -a*y, min at y=N
                k0 = 4 * min_t - 2 * N_local * (b - a)
                K = 4 * (N_local - 0) + k0  # for y=0, idx=N
                L = M_local
                coeff_L = p2S_local[L]
                for _y in range(M_local):
                    below = total_points_local - above - L
                    dir_sum += qpow_local[above] * omq_local[below] * (K * coeff_L)
                    above += L
                    K -= 4
                total_cross_scaled += mult * dir_sum
                continue

            # General b>0
            R = N_local * (a + b) + 1  # number of distinct t values
            counts = [0] * R
            ky_b = ky_tab[b]

            # Unique start-points: x<a strip and y<b strip (for x>=a)
            for x0 in range(a):
                kx_base = kx_a[x0]
                bx = b * x0
                for y0 in range(M_local):
                    ky = ky_b[y0]
                    L = 1 + (kx_base if ky > kx_base else ky)
                    counts[bx + ay_a[y0]] = L

            for x0 in range(a, M_local):
                kx_base = kx_a[x0]
                bx = b * x0
                for y0 in range(b):
                    ky = ky_b[y0]
                    L = 1 + (kx_base if ky > kx_base else ky)
                    counts[bx + ay_a[y0]] = L

            # Sweep from outside to inside (descending idx)
            above = 0
            k0 = 4 * (-a * N_local) - 2 * N_local * (b - a)
            K = 4 * (R - 1) + k0
            dir_sum = 0.0
            for idx in range(R - 1, -1, -1):
                cnt = counts[idx]
                if cnt:
                    below = total_points_local - above - cnt
                    dir_sum += (
                        qpow_local[above] * omq_local[below] * (K * p2S_local[cnt])
                    )
                    above += cnt
                K -= 4

            total_cross_scaled += mult * dir_sum

    return total_cross_scaled / 8.0


def solve() -> None:
    # Test values given in the problem statement (rounded to 5 decimals there)
    assert f"{expected_area(1):.5f}" == "0.18750"
    assert f"{expected_area(2):.5f}" == "0.94335"
    assert f"{expected_area(10):.5f}" == "55.03013"

    ans = expected_area(100)
    print(f"{ans:.5f}")


if __name__ == "__main__":
    solve()
