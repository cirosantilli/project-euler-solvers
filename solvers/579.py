#!/usr/bin/env python3
"""
Project Euler 579: Lattice Points in Lattice Cubes

We count all lattice cubes whose vertices lie in [0,n]^3 and compute:
  C(n) = number of such cubes
  S(n) = sum of lattice points contained in each cube

We use quaternion parametrization (Euler-Rodrigues) to enumerate primitive cube
orientations uniquely via primary quaternions (Kiss-Kutas definition).
Then we sum over integer scale factors using polynomial summation with precomputed
power sums.
"""

from math import gcd, isqrt


MOD = 10**9


def _power_sums(N, K):
    """
    Returns sums[k][t] = sum_{i=1..t} i^k for k=0..K, t=0..N.
    sums[0][t] = t.
    """
    sums = [[0] * (N + 1) for _ in range(K + 1)]
    for t in range(1, N + 1):
        sums[0][t] = t
        p = t
        sums[1][t] = sums[1][t - 1] + p
        for k in range(2, K + 1):
            p *= t
            sums[k][t] = sums[k][t - 1] + p
    return sums


def solve(n, mod=None):
    """
    Returns (C(n), S(n)) if mod is None (exact integer),
    otherwise returns (C(n) % mod, S(n) % mod).
    """
    # Degree: translation polynomial is degree 3, lattice-point polynomial is degree 3,
    # product degree is 6 => need power sums up to 6.
    K = 6
    sums = _power_sums(n, K)

    A = n + 1
    A2 = A * A
    A3 = A2 * A

    totalC = 0
    totalS = 0

    B = isqrt(n)  # max abs coordinate for quaternion component

    # Correct even/odd ranges in [-B..B]
    start_even = -B if (B & 1) == 0 else -B + 1
    start_odd = -B if (B & 1) == 1 else -B + 1
    even_vals = list(range(start_even, B + 1, 2))
    odd_vals = list(range(start_odd, B + 1, 2))

    # Precompute all candidate 'a' values by:
    # - parity (0 even, 1 odd)
    # - residue mod 4
    # - max absolute value
    maxA = B
    a_lists = [[[[] for _ in range(maxA + 1)] for _ in range(4)] for _ in range(2)]
    for max_a in range(0, maxA + 1):
        for a in range(-max_a, max_a + 1):
            a_lists[a & 1][a & 3][max_a].append(a)

    abs_ = abs

    def gcd3(x, y, z):
        return gcd(gcd(abs_(x), abs_(y)), abs_(z))

    # Enumerate primary quaternions in S1:
    # Case 1: a odd, b,c,d even (N ≡ 1 mod 4)
    # Case 2: a even, b,c,d odd (N ≡ 3 mod 4)
    cases = (
        (even_vals, 1, n - 1),  # bcd even, a odd, need s <= n-1 because a^2>=1
        (odd_vals, 0, n),  # bcd odd, a even
    )

    for bcd_vals, a_parity, s_limit in cases:
        for b in bcd_vals:
            bb = b * b
            for c in bcd_vals:
                cc = c * c
                bc2 = bb + cc
                for d in bcd_vals:
                    dd = d * d
                    s = bc2 + dd
                    if s > s_limit:
                        continue

                    rem = n - s
                    max_a = isqrt(rem)

                    # primary condition: a + b + c + d ≡ 1 (mod 4)
                    sum_bcd_mod4 = (b + c + d) & 3
                    a_res = (1 - sum_bcd_mod4) & 3

                    g_bcd = gcd3(b, c, d)

                    for a in a_lists[a_parity][a_res][max_a]:
                        if gcd(g_bcd, abs_(a)) != 1:
                            continue

                        aa = a * a
                        m = (
                            aa + s
                        )  # quaternion norm = cube side length for primitive orientation

                        # Euler-Rodrigues / Euler matrix columns (u,v,w):
                        # (same as rotating i,j,k by quaternion)
                        u0 = aa + bb - cc - dd
                        u1 = 2 * (b * c - a * d)
                        u2 = 2 * (b * d + a * c)

                        v0 = 2 * (b * c + a * d)
                        v1 = aa - bb + cc - dd
                        v2 = 2 * (c * d - a * b)

                        w0 = 2 * (b * d - a * c)
                        w1 = 2 * (c * d + a * b)
                        w2 = aa - bb - cc + dd

                        # coordinate spans (extent along each axis is sum of abs components)
                        sx = abs_(u0) + abs_(v0) + abs_(w0)
                        sy = abs_(u1) + abs_(v1) + abs_(w1)
                        sz = abs_(u2) + abs_(v2) + abs_(w2)

                        T = n // sx
                        ty = n // sy
                        if ty < T:
                            T = ty
                        tz = n // sz
                        if tz < T:
                            T = tz
                        if T == 0:
                            continue

                        # Translation count polynomial:
                        # (A - sx*t)(A - sy*t)(A - sz*t)
                        s1 = sx + sy + sz
                        s2 = sx * sy + sy * sz + sz * sx
                        s3 = sx * sy * sz

                        t0 = A3
                        t1 = -A2 * s1
                        t2 = A * s2
                        t3 = -s3

                        # Lattice point count inside a parallelepiped has Ehrhart polynomial:
                        # L(t) = 1 + t*sum(gcd(edges)) + t^2*sum(gcd(face normals)) + t^3*det
                        # For cubes produced by Euler matrices:
                        # det = m^3 and sum(gcd(face normals)) = m * sum(gcd(edges)).
                        gU = gcd(abs_(u0), gcd(abs_(u1), abs_(u2)))
                        gV = gcd(abs_(v0), gcd(abs_(v1), abs_(v2)))
                        gW = gcd(abs_(w0), gcd(abs_(w1), abs_(w2)))
                        G1 = gU + gV + gW

                        p0 = 1
                        p1 = G1
                        p2 = m * G1
                        p3 = m * m * m

                        s0 = T
                        S1p = sums[1][T]
                        S2p = sums[2][T]
                        S3p = sums[3][T]
                        S4p = sums[4][T]
                        S5p = sums[5][T]
                        S6p = sums[6][T]

                        if mod is None:
                            # Count cubes
                            totalC += t0 * s0 + t1 * S1p + t2 * S2p + t3 * S3p

                            # Sum lattice points: convolution of degree 3 polynomials => degree 6
                            D0 = t0
                            D1 = t0 * p1 + t1
                            D2 = t0 * p2 + t1 * p1 + t2
                            D3 = t0 * p3 + t1 * p2 + t2 * p1 + t3
                            D4 = t1 * p3 + t2 * p2 + t3 * p1
                            D5 = t2 * p3 + t3 * p2
                            D6 = t3 * p3

                            totalS += (
                                D0 * s0
                                + D1 * S1p
                                + D2 * S2p
                                + D3 * S3p
                                + D4 * S4p
                                + D5 * S5p
                                + D6 * S6p
                            )
                        else:
                            M = mod

                            # reduce coefficients mod M
                            t0m = t0 % M
                            t1m = t1 % M
                            t2m = t2 % M
                            t3m = t3 % M

                            totalC = (
                                totalC
                                + t0m * (s0 % M)
                                + t1m * (S1p % M)
                                + t2m * (S2p % M)
                                + t3m * (S3p % M)
                            ) % M

                            p1m = p1 % M
                            p2m = p2 % M
                            p3m = p3 % M

                            D0 = t0m
                            D1 = (t0m * p1m + t1m) % M
                            D2 = (t0m * p2m + t1m * p1m + t2m) % M
                            D3 = (t0m * p3m + t1m * p2m + t2m * p1m + t3m) % M
                            D4 = (t1m * p3m + t2m * p2m + t3m * p1m) % M
                            D5 = (t2m * p3m + t3m * p2m) % M
                            D6 = (t3m * p3m) % M

                            totalS = (
                                totalS
                                + D0 * (s0 % M)
                                + D1 * (S1p % M)
                                + D2 * (S2p % M)
                                + D3 * (S3p % M)
                                + D4 * (S4p % M)
                                + D5 * (S5p % M)
                                + D6 * (S6p % M)
                            ) % M

    return totalC, totalS


def _run_asserts():
    # Given test values from problem statement
    testC = {1: 1, 2: 9, 4: 100, 5: 229, 10: 4469, 50: 8154671}
    testS = {1: 8, 2: 91, 4: 1878, 5: 5832, 10: 387003, 50: 29948928129}

    for n in sorted(testC.keys()):
        Cn, Sn = solve(n)
        assert Cn == testC[n], (n, Cn, testC[n])
        assert Sn == testS[n], (n, Sn, testS[n])


def main():
    _run_asserts()
    print(solve(5000, mod=MOD)[1])


if __name__ == "__main__":
    main()
