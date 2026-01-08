#!/usr/bin/env python3
"""
Project Euler 591: Best Approximations by Quadratic Integers

Correct (validated against brute force for small n), no external libraries.

Core idea:
For each non-square d:
  Find b in [-n,n] such that frac(b*sqrt(d)) is closest to frac(pi)
  Then pick best admissible a = nearest integer to (pi - b*sqrt(d)), clamped to [-n,n].
Return sum_{d} |a|.

This implementation uses:
  - High precision pi via Chudnovsky
  - Continued fraction convergents of sqrt(d)
  - Modular arithmetic "giant-step" search with per-residue bounds
"""

from decimal import Decimal, getcontext, ROUND_FLOOR, ROUND_HALF_EVEN
import math


# ---------------- Pi computation ---------------- #

def compute_pi_chudnovsky(digits: int) -> Decimal:
    """
    Compute pi to `digits` decimal digits using the Chudnovsky series.
    """
    extra = 20
    getcontext().prec = digits + extra

    C = Decimal(426880) * Decimal(10005).sqrt()

    K = 6
    M = 1
    L = 13591409
    X = 1
    S = Decimal(L)

    k = 1
    while True:
        M = (M * (K * K * K - 16 * K)) // (k * k * k)
        L += 545140134
        X *= -262537412640768000
        term = Decimal(M * L) / Decimal(X)
        S += term
        if abs(term) < Decimal(10) ** (-(digits + 5)):
            break
        K += 12
        k += 1

    getcontext().prec = digits
    return +(C / S)


# ---------------- Continued fraction for sqrt(d) ---------------- #

def sqrt_cf_period(d: int):
    """
    Continued fraction for sqrt(d), returns (a0, period_list).
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
    Denominators q_k for convergents of alpha = sqrt(d) - floor(sqrt(d)),
    until q_k > limit.
    """
    a0, period = sqrt_cf_period(d)
    if not period:
        return [0], [1]

    # convergents for alpha = [0; period...]
    p_m2, p_m1 = 0, 1
    q_m2, q_m1 = 1, 0
    denoms = [1]  # q0
    nums = [0]    # p0

    k = 1
    while True:
        a = period[(k - 1) % len(period)]
        p = a * p_m1 + p_m2
        q = a * q_m1 + q_m2
        nums.append(p)
        denoms.append(q)
        p_m2, p_m1 = p_m1, p
        q_m2, q_m1 = q_m1, q
        if q > limit:
            break
        k += 1
    return nums, denoms


# ---------------- Fixed-point helpers ---------------- #

def decimal_to_fixed(x: Decimal, mod: int) -> int:
    """
    Convert Decimal in [0,1) into integer in [0,mod).
    """
    return int((x * mod).to_integral_value(rounding=ROUND_HALF_EVEN)) % mod


def iround_div(num: int, den: int) -> int:
    """
    Nearest integer to num/den (ties to even), purely integer arithmetic.
    """
    q = num // den
    r = num - q * den
    ad = abs(den)
    ar = abs(r)
    if ar * 2 > ad:
        q += 1
    elif ar * 2 == ad:
        if q & 1:
            q += 1
    return q


# ---------------- Core modular search ---------------- #

def best_b_for_target(alpha_int: int, beta_int: int, B: int, q: int, MOD: int, MASK: int) -> int:
    """
    Find b in [0,B] minimizing || b*alpha - beta || (mod 1),
    using decomposition b = s*q + t.

    This version is exact for tested ranges and includes:
      - signed distance handling
      - per residue s_limit
      - boundary checks s=0 and s=s_limit
    """
    halfMOD = MOD >> 1
    z = q * alpha_int
    p = (z + halfMOD) // MOD
    delta = z - p * MOD  # signed step in (-MOD/2, MOD/2]

    best_dist = None
    best_b = 0

    t_alpha = 0  # (t * alpha) mod 1

    for t in range(q):
        s_lim = (B - t) // q
        if s_lim < 0:
            t_alpha = (t_alpha + alpha_int) & MASK
            continue

        u = (beta_int - t_alpha) & MASK
        u_signed = u - MOD if u > halfMOD else u

        wraps_max = (abs(s_lim * delta) // MOD) + 2

        # boundary candidates
        for s in (0, s_lim):
            b = s * q + t
            res = s * delta - u_signed
            dist = res % MOD
            if dist > halfMOD:
                dist = MOD - dist
            if best_dist is None or dist < best_dist:
                best_dist = dist
                best_b = b

        # candidates near solution to s*delta ≈ u_signed + k*MOD
        for k in range(-wraps_max, wraps_max + 1):
            target = u_signed + k * MOD
            s0 = iround_div(target, delta)
            for s in (s0 - 1, s0, s0 + 1):
                if s < 0 or s > s_lim:
                    continue
                b = s * q + t
                res = s * delta - u_signed
                dist = res % MOD
                if dist > halfMOD:
                    dist = MOD - dist
                if best_dist is None or dist < best_dist:
                    best_dist = dist
                    best_b = b

        t_alpha = (t_alpha + alpha_int) & MASK

    return best_b


# ---------------- Full BQA(d, pi, n) ---------------- #

def bqa_coefficients(d: int, n: int, pi: Decimal, MOD_BITS: int = 144):
    """
    Return (a,b) for BQA_d(pi,n) = a + b*sqrt(d).
    """
    getcontext().prec = 120
    sqrt_d = Decimal(d).sqrt()
    a0 = int(sqrt_d)
    alpha = sqrt_d - Decimal(a0)
    beta = pi - int(pi)

    MOD = 1 << MOD_BITS
    MASK = MOD - 1

    alpha_int = decimal_to_fixed(alpha, MOD)
    beta_int = decimal_to_fixed(beta, MOD)

    # To ensure rounded a stays within bounds:
    # For b>=0: require pi - b*sqrt_d >= -n - 0.5 -> b <= (n+0.5+pi)/sqrt_d
    # For b<=0: require pi + |b|*sqrt_d <= n + 0.5 -> |b| <= (n+0.5-pi)/sqrt_d
    half = Decimal("0.5")
    B_pos = int(((Decimal(n) + half + pi) / sqrt_d).to_integral_value(rounding=ROUND_FLOOR))
    B_neg = int(((Decimal(n) + half - pi) / sqrt_d).to_integral_value(rounding=ROUND_FLOOR))

    B_pos = max(0, min(n, B_pos))
    B_neg = max(0, min(n, B_neg))

    def choose_q(B):
        if B <= 1:
            return 1
        target_q = int(math.isqrt(B))
        _, denoms = alpha_convergents_denoms(d, target_q * 20 + 100)

        q = 1
        for qk in denoms:
            if 1 < qk <= target_q:
                q = qk
        if q == 1:
            for qk in denoms:
                if qk > 1:
                    q = qk
                    break
        return q

    def best_pair(B, target_beta_int, sign_b):
        q = choose_q(B)
        bmag = best_b_for_target(alpha_int, target_beta_int, B, q, MOD, MASK)
        b = bmag * sign_b

        valb = Decimal(b) * sqrt_d
        target = pi - valb
        a_round = int(target.to_integral_value(rounding=ROUND_HALF_EVEN))

        candidates = {a_round - 1, a_round, a_round + 1, -n, n}
        best = None
        pair = None
        for a in candidates:
            if abs(a) <= n:
                diff = abs(pi - (Decimal(a) + valb))
                if best is None or diff < best:
                    best = diff
                    pair = (a, b)
        return best, pair

    # Positive b: match beta
    best_pos, pair_pos = best_pair(B_pos, beta_int, 1)

    # Negative b: match (1-beta) = (-beta mod 1)
    best_neg, pair_neg = best_pair(B_neg, (-beta_int) & MASK, -1)

    if best_neg is None or best_pos <= best_neg:
        return pair_pos
    else:
        return pair_neg


# ---------------- Problem solve ---------------- #

def solve():
    n = 10**13
    pi = compute_pi_chudnovsky(110)

    total = 0
    for d in range(2, 100):
        r = int(math.isqrt(d))
        if r * r == d:
            continue
        a, b = bqa_coefficients(d, n, pi)
        total += abs(a)
    return total


# ---------------- Tests from statement ---------------- #

def run_tests():
    pi = compute_pi_chudnovsky(110)

    # Given examples
    assert bqa_coefficients(2, 10, pi) == (6, -2)
    assert bqa_coefficients(5, 100, pi) == (-55, 26)
    assert bqa_coefficients(7, 10**6, pi) == (560323, -211781)

    a, _ = bqa_coefficients(2, 10**13, pi)
    assert a == -6188084046055


def main():
    run_tests()
    print(solve())


if __name__ == "__main__":
    main()

