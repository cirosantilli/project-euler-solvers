#!/usr/bin/env python3
"""
Project Euler 591 — Best Approximations by Quadratic Integers
https://projecteuler.net/problem=591

We need, for every non-square d < 100, the quadratic integer a + b*sqrt(d)
(with |a|,|b| <= n) closest to pi, then sum |a| (integral part).

No external libraries used (only Python standard library).
"""

from decimal import Decimal, getcontext, ROUND_HALF_EVEN, ROUND_FLOOR
import math


# -------------------------
# High-precision pi (Chudnovsky)
# -------------------------

def compute_pi_chudnovsky(digits: int) -> Decimal:
    """
    Compute pi to 'digits' decimal digits using the Chudnovsky series.
    """
    extra = 20
    getcontext().prec = digits + extra

    C = Decimal(426880) * Decimal(10005).sqrt()

    # Chudnovsky terms (integer recurrence)
    K = 6
    M = 1
    L = 13591409
    X = 1
    S = Decimal(L)

    k = 1
    while True:
        M = (M * (K**3 - 16*K)) // (k**3)
        L += 545140134
        X *= -262537412640768000  # (-640320)^3
        term = Decimal(M * L) / Decimal(X)
        S += term
        if abs(term) < Decimal(10) ** (-(digits + 5)):
            break
        K += 12
        k += 1

    pi = C / S
    getcontext().prec = digits
    return +pi


# -------------------------
# Continued fraction period of sqrt(d)
# -------------------------

def sqrt_cf_period(d: int):
    """
    Continued fraction of sqrt(d) (d non-square):
    sqrt(d) = [a0; period repeating]
    Returns (a0, period_list)
    """
    a0 = int(math.isqrt(d))
    if a0 * a0 == d:
        return a0, []

    m = 0
    denom = 1
    a = a0
    period = []

    while True:
        m = denom * a - m
        denom = (d - m * m) // denom
        a = (a0 + m) // denom
        period.append(a)
        if a == 2 * a0:
            break

    return a0, period


def alpha_convergents_denoms(d: int, limit: int):
    """
    alpha = frac(sqrt(d)) = sqrt(d) - floor(sqrt(d))
    If sqrt(d) = [a0; a1,a2,...] periodic, then:
        alpha = [0; a1,a2,...] periodic
    Generate convergent denominators q_k up to > limit.
    """
    a0, period = sqrt_cf_period(d)
    # alpha's continued fraction is [0; period repeating]

    # Standard convergent recurrence:
    p_minus2, p_minus1 = 0, 1
    q_minus2, q_minus1 = 1, 0

    denoms = []
    nums = []

    for k in range(20000):
        if k == 0:
            a = 0
        else:
            a = period[(k - 1) % len(period)]

        p = a * p_minus1 + p_minus2
        q = a * q_minus1 + q_minus2

        nums.append(p)
        denoms.append(q)

        p_minus2, p_minus1 = p_minus1, p
        q_minus2, q_minus1 = q_minus1, q

        if q > limit:
            break

    return nums, denoms


# -------------------------
# Fixed-point helper
# -------------------------

def decimal_to_fixed(x: Decimal, mod: int) -> int:
    return int((x * mod).to_integral_value(rounding=ROUND_HALF_EVEN)) % mod


# -------------------------
# Core search using convergent decomposition b = s*q + t
# -------------------------

def best_b_for_target(alpha_int: int, beta_int: int, B: int, q: int, MOD: int, MASK: int) -> int:
    """
    Find b in [0,B] minimizing circular distance between frac(b*alpha) and beta.
    Uses decomposition b = s*q + t where q is a convergent denominator making
    delta = q*alpha - nearest_int(q*alpha) small.

    Runs in O(q) time with a tiny constant factor.
    """
    # delta_scaled = q*alpha_int - p*MOD (signed remainder)
    z = q * alpha_int
    p = (z + MOD // 2) // MOD  # nearest integer to z/MOD
    delta_scaled = z - p * MOD

    if delta_scaled == 0:
        return 0

    sign = 1
    delta = delta_scaled
    if delta_scaled < 0:
        sign = -1
        delta = -delta_scaled

    s_max = B // q
    # how many wraps can s*delta have
    wraps_max = (s_max * delta) // MOD + 1
    delta_half = delta // 2

    best_dist = None
    best_b = 0

    t_alpha = 0
    halfMOD = MOD // 2

    for t in range(q):
        # u = (beta - t_alpha) mod MOD
        u = (beta_int - t_alpha) & MASK
        if sign < 0:
            u = (-u) & MASK

        # Try possible wrap counts (small!)
        for k in range(wraps_max + 1):
            target = u + k * MOD
            s0 = (target + delta_half) // delta
            for s in (s0 - 1, s0, s0 + 1):
                if s < 0 or s > s_max:
                    continue
                b = s * q + t
                if b > B:
                    continue

                # val = t_alpha + sign*(s*delta) mod MOD
                prod = (s * delta) & MASK
                if sign < 0:
                    val = (t_alpha - prod) & MASK
                else:
                    val = (t_alpha + prod) & MASK

                diff = (val - beta_int) & MASK
                if diff > halfMOD:
                    diff = MOD - diff

                if best_dist is None or diff < best_dist:
                    best_dist = diff
                    best_b = b

        # increment t_alpha = (t_alpha + alpha) mod MOD
        t_alpha = (t_alpha + alpha_int) & MASK

    return best_b


def bqa_coefficients(d: int, n: int, pi: Decimal, MOD_BITS: int = 160):
    """
    Compute (a,b) such that a + b*sqrt(d) is closest to pi with |a|,|b| <= n.
    Returns integers (a,b).
    """
    getcontext().prec = 110
    sqrt_d = Decimal(d).sqrt()
    a0 = int(sqrt_d)
    alpha = sqrt_d - Decimal(a0)
    beta = pi - int(pi)  # frac(pi)

    MOD = 1 << MOD_BITS
    MASK = MOD - 1

    alpha_int = decimal_to_fixed(alpha, MOD)
    beta_int = decimal_to_fixed(beta, MOD)

    # allowable b is restricted by both |b|<=n and |a|<=n (a ~ pi - b*sqrt(d))
    # safe bound: b <= floor((n + pi)/sqrt(d))
    B = int(((Decimal(n) + pi) / sqrt_d).to_integral_value(rounding=ROUND_FLOOR))
    if B > n:
        B = n
    if B < 0:
        B = 0

    # pick q = largest convergent denominator <= sqrt(B)
    target_q = int(math.isqrt(B)) if B > 0 else 1
    _, denoms = alpha_convergents_denoms(d, target_q * 10 + 50)
    q = 1
    for qk in denoms:
        if 1 < qk <= target_q:
            q = qk
    if q == 1:
        # fallback: pick first > 1
        for qk in denoms:
            if qk > 1:
                q = qk
                break

    # search for best positive b for beta and for (1-beta) (handles negative b)
    b_pos = best_b_for_target(alpha_int, beta_int, B, q, MOD, MASK)

    beta2_int = (-beta_int) & MASK  # 1-beta in mod arithmetic
    b_pos2 = best_b_for_target(alpha_int, beta2_int, B, q, MOD, MASK)

    # compute real errors quickly to decide sign
    # error for negative b: compare to 1-beta target -> choose -b_pos2
    # evaluate fixed-point distance:
    def fp_distance(b, target_int):
        # frac(b*alpha) using high precision decimal for final sign choice only
        # but still cheap once per candidate:
        val = Decimal(b) * alpha
        val = val - int(val)
        x = decimal_to_fixed(val, MOD)
        diff = (x - target_int) & MASK
        if diff > MOD // 2:
            diff = MOD - diff
        return diff

    dist1 = fp_distance(b_pos, beta_int)
    dist2 = fp_distance(b_pos2, beta2_int)
    if dist2 < dist1:
        b = -b_pos2
    else:
        b = b_pos

    # compute best a = nearest integer to pi - b*sqrt(d)
    a = int((pi - Decimal(b) * sqrt_d).to_integral_value(rounding=ROUND_HALF_EVEN))

    # If rounding leads to outside bounds, clamp (rare, but safe)
    if a > n:
        a = n
    elif a < -n:
        a = -n
    if b > n:
        b = n
    elif b < -n:
        b = -n

    return a, b


# -------------------------
# Solve problem
# -------------------------

def solve(n: int = 10**13) -> int:
    # Pi precision: we need safe rounding at ~1e-13 scale; use ~80 digits.
    pi = compute_pi_chudnovsky(90)

    total = 0
    for d in range(2, 100):
        r = int(math.isqrt(d))
        if r * r == d:
            continue
        a, b = bqa_coefficients(d, n, pi)
        total += abs(a)

    return total


# -------------------------
# Problem statement tests (asserts)
# -------------------------

def run_tests():
    pi = compute_pi_chudnovsky(90)

    # Given examples in problem statement:
    # BQA_2(pi, 10) = 6 - 2*sqrt(2)
    a, b = bqa_coefficients(2, 10, pi)
    assert (a, b) == (6, -2)

    # BQA_5(pi, 100) = 26*sqrt(5) - 55
    a, b = bqa_coefficients(5, 100, pi)
    assert (a, b) == (-55, 26)

    # BQA_7(pi, 10^6) = 560323 - 211781*sqrt(7)
    a, b = bqa_coefficients(7, 10**6, pi)
    assert (a, b) == (560323, -211781)

    # The inequality example implies this exact best (it matches known BQA for n=1e13)
    a, b = bqa_coefficients(2, 10**13, pi)
    assert a == -6188084046055 and b == 4375636191520


def main():
    run_tests()
    ans = solve(10**13)
    print(ans)


if __name__ == "__main__":
    main()

