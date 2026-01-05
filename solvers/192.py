#!/usr/bin/env python3
import math


def best_approx_fraction_sqrt(n: int, bound: int):
    a0 = math.isqrt(n)
    if a0 * a0 == n:
        return None

    m, d, a = 0, 1, a0

    p_m2, p_m1 = 0, 1
    q_m2, q_m1 = 1, 0

    # first term a0
    p = a * p_m1 + p_m2
    q = a * q_m1 + q_m2
    p_m2, p_m1 = p_m1, p
    q_m2, q_m1 = q_m1, q

    while True:
        m = d * a - m
        d = (n - m * m) // d
        a = (a0 + m) // d

        p = a * p_m1 + p_m2
        q = a * q_m1 + q_m2

        if q > bound:
            pC, qC = p_m1, q_m1
            pP, qP = p_m2, q_m2

            t = (bound - qP) // qC
            if t <= 0:
                return (pC, qC)

            pS = t * pC + pP
            qS = t * qC + qP

            sC = pC * pC - n * qC * qC
            sS = pS * pS - n * qS * qS

            if sC < 0 and sS < 0:
                return (pS, qS) if pS * qC > pC * qS else (pC, qC)
            if sC > 0 and sS > 0:
                return (pS, qS) if pS * qC < pC * qS else (pC, qC)

            # opposite sides: compare midpoint
            if pC * qS < pS * qC:
                pL, qL = pC, qC
                pH, qH = pS, qS
            else:
                pL, qL = pS, qS
                pH, qH = pC, qC

            num = pL * qH + pH * qL
            den = 2 * qL * qH
            if n * den * den <= num * num:
                return (pL, qL)
            else:
                return (pH, qH)

        p_m2, p_m1 = p_m1, p
        q_m2, q_m1 = q_m1, q


def best_denom_sqrt(n: int, bound: int) -> int:
    frac = best_approx_fraction_sqrt(n, bound)
    return frac[1]


def solve(limit=100000, bound=10**12):
    s = 0
    for n in range(2, limit + 1):
        r = math.isqrt(n)
        if r * r == n:
            continue
        s += best_denom_sqrt(n, bound)
    return s


if __name__ == "__main__":
    assert best_approx_fraction_sqrt(13, 20) == (18, 5)
    assert best_approx_fraction_sqrt(13, 30) == (101, 28)
    print(solve())
