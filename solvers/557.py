#!/usr/bin/env python3
"""
Project Euler 557 - Cutting triangles
Pure Python, no external libraries.

We use a rational-parameter construction of the two cevians, which yields
integer areas after scaling. Each valid configuration corresponds to two
reduced fractions u/(u+v) and p/(p+q).

For each reduced parameter pair we compute the minimal integer scale
(using gcd/lcm only), producing a primitive (a,b,c,d). All other solutions
are integer multiples of the primitive one. We sum totals up to n.

The official Project Euler result is:
S(10000) = 2699929328
"""

from math import gcd


def lcm(a: int, b: int) -> int:
    return a // gcd(a, b) * b


def primitive_from_params(u, v, p, q):
    """
    Given coprime pairs (u,v) and (p,q), return the minimal integer quadruple
    (a,b,c,d) and total area T, or None if something is invalid.
    """
    U = u + v
    P = p + q

    # K is the numerator of (1 - st) when s = u/U and t = p/P in the affine model
    K = u * q + v * p + v * q

    vq = v * q
    g1 = gcd(K, vq)          # factor already in a's denominator that can be cancelled
    A = K // g1              # remaining factor needed in total area

    Ug = U * g1
    Pg = P * g1

    # minimal scale t0 to make b and c integral
    need1 = Ug // gcd(Ug, p * v * v)
    need2 = Pg // gcd(Pg, u * q * q)
    t0 = lcm(need1, need2)

    T = A * t0
    a = t0 * (vq // g1)
    b = t0 * (p * v * v) // Ug
    c = t0 * (u * q * q) // Pg
    d = T - a - b - c

    if a <= 0 or b <= 0 or c <= 0 or d <= 0:
        return None

    if b > c:
        b, c = c, b

    return (a, b, c, d), T


def S(n: int) -> int:
    """
    Compute S(n) = sum of total areas of all valid quadruples with total <= n.
    We enumerate primitive quadruples using coprime parameter pairs and then
    add contributions of all multiples.
    """

    seen = set()
    total_sum = 0

    # Adaptive search bound:
    # Increase max parameter sum in steps until no new primitives appear.
    step = 40
    max_sum = step

    while True:
        new_found = False

        # Enumerate all reduced pairs (u,v) and (p,q) with u+v<=max_sum, p+q<=max_sum.
        # This is the dominant cost; adaptive expansion limits wasted work.
        for U in range(2, max_sum + 1):
            for u in range(1, U):
                v = U - u
                if gcd(u, v) != 1:
                    continue
                for P in range(2, max_sum + 1):
                    for p in range(1, P):
                        q = P - p
                        if gcd(p, q) != 1:
                            continue

                        res = primitive_from_params(u, v, p, q)
                        if res is None:
                            continue
                        quad, T0 = res

                        if T0 > n:
                            continue

                        if quad in seen:
                            continue

                        seen.add(quad)
                        new_found = True

                        m = n // T0
                        total_sum += T0 * m * (m + 1) // 2

        # If expanding the boundary yielded no new primitives <= n, stop.
        if not new_found:
            break

        max_sum += step

        # Safety cap (should never be reached for n=10000)
        if max_sum > 5000:
            break

    return total_sum


def all_quads_with_total(total_area: int):
    """
    For testing statement claim: collect all valid quadruples with total exactly total_area.
    We do this by computing S(total_area) primitives and filtering.
    """
    res = []
    # brute by scanning parameters enough for such small total
    seen = set()
    for U in range(2, total_area + 1):
        for u in range(1, U):
            v = U - u
            if gcd(u, v) != 1:
                continue
            for P in range(2, total_area + 1):
                for p in range(1, P):
                    q = P - p
                    if gcd(p, q) != 1:
                        continue
                    tmp = primitive_from_params(u, v, p, q)
                    if tmp is None:
                        continue
                    quad, T0 = tmp
                    if total_area % T0 != 0:
                        continue
                    k = total_area // T0
                    scaled = (quad[0] * k, quad[1] * k, quad[2] * k, quad[3] * k)
                    if scaled in seen:
                        continue
                    if sum(scaled) == total_area:
                        seen.add(scaled)
                        res.append(scaled)
    return sorted(res)


def main():
    # --- Statement tests ---
    assert S(20) == 259

    # Only two quadruples with total area 55:
    quads_55 = all_quads_with_total(55)
    assert quads_55 == [(20, 2, 24, 9), (22, 8, 11, 14)]

    # --- Solve ---
    print(S(10000))


if __name__ == "__main__":
    main()

