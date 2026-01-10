#!/usr/bin/env python3
"""
Project Euler 591: Best Approximations by Quadratic Integers

We compute BQA_d(pi, n) = a + b*sqrt(d) with |a|,|b| <= n that minimizes |a + b*sqrt(d) - pi|
for each non-square d < 100, then sum |a|.

Key idea (Ostrowski / α-numeration):
Let alpha = frac(sqrt(d)) in (0,1) and beta = frac(pi) in [0,1).
For b in range where |a|<=n is feasible, the best a for a given b is the nearest integer to pi - b*sqrt(d),
and the error is the circular distance between {b*alpha} and beta (or 1-beta for negative b).
The best b can be found using Ostrowski-style α-numeration of beta and a characterization of best left/right
α-approximations (Cabanillas-López & Labbé, 2019 arXiv:1904.01874).

No external libraries are used.
"""
from __future__ import annotations

from decimal import Decimal, getcontext, ROUND_FLOOR, ROUND_CEILING, ROUND_HALF_EVEN
from math import isqrt
from typing import List, Tuple


# ---------- Decimal helpers ----------


def frac_dec(x: Decimal) -> Decimal:
    """Fractional part in [0,1) for Decimal x."""
    return x - x.to_integral_value(rounding=ROUND_FLOOR)


def ceil_int_dec(x: Decimal) -> int:
    """Ceiling of Decimal x as int."""
    return int(x.to_integral_value(rounding=ROUND_CEILING))


def nearest_int_dec(x: Decimal) -> int:
    """Nearest integer to Decimal x (ties don't occur in this problem)."""
    return int(x.to_integral_value(rounding=ROUND_HALF_EVEN))


# ---------- High-precision pi (Chudnovsky) ----------


def chudnovsky_pi(digits: int) -> Decimal:
    """
    Compute pi to `digits` significant decimal digits using the Chudnovsky series.
    Each term adds ~14 digits; the loop count is small for our needs.
    """
    # extra guard digits for intermediate rounding
    getcontext().prec = digits + 30

    C = Decimal(426880) * Decimal(10005).sqrt()
    n_terms = digits // 14 + 3

    M = 1
    L = 13591409
    X = 1
    K = 6
    S = Decimal(L)

    for i in range(1, n_terms):
        # M_i = M_{i-1} * (K^3 - 16K) / i^3  with exact integer arithmetic
        M = (M * (K * K * K - 16 * K)) // (i * i * i)
        L += 545140134
        X *= -262537412640768000
        S += Decimal(M * L) / Decimal(X)
        K += 12

    pi = C / S

    getcontext().prec = digits
    return +pi


# ---------- Continued fraction of sqrt(d) ----------


def is_square(n: int) -> bool:
    r = isqrt(n)
    return r * r == n


def sqrt_cf_period(D: int) -> Tuple[int, List[int]]:
    """
    Continued fraction for sqrt(D) (D non-square):
      sqrt(D) = [a0; (a1, ..., a_period) repeating]
    Returns (a0, period_list).
    Standard termination: the period ends when a == 2*a0.
    """
    a0 = isqrt(D)
    if a0 * a0 == D:
        raise ValueError("D is a perfect square")

    m = 0
    d = 1
    a = a0
    period: List[int] = []
    while True:
        m = d * a - m
        d = (D - m * m) // d
        a = (a0 + m) // d
        period.append(a)
        if a == 2 * a0:
            break
    return a0, period


# ---------- Best b via α-numeration (Ostrowski-like) ----------


def best_b_positive(alpha: Decimal, beta: Decimal, B: int, period: List[int]) -> int:
    """
    Return b in [0,B] that minimizes the circular distance between {b*alpha} and beta.
    alpha in (0,1), beta in [0,1).

    Uses α-numeration digits (b_k) of beta and characterizations of best right/left
    α-approximations (Propositions 9 & 10 in arXiv:1904.01874).
    """
    if B <= 0:
        return 0

    # Build partial quotients a_k (from the periodic CF of sqrt(d), but alpha=[0;a1,a2,...]),
    # denominators q_k, and deltas δ_k = (-1)^k(q_k*alpha - p_k) > 0 via recurrence:
    #   q_k = a_k q_{k-1} + q_{k-2}  with q_{-1}=0, q_0=1
    #   δ_k = -a_k δ_{k-1} + δ_{k-2} with δ_{-1}=1, δ_0=alpha
    #
    # We compute a few extra terms beyond the first q_k > B so we can evaluate candidate prefixes.
    a: List[int] = [0]  # 1-indexed
    q: List[int] = [1]  # q[0]=q_0
    q_minus1 = 0  # q_{-1}

    delta: List[Decimal] = [alpha]  # delta[0]=δ_0
    delta_minus1 = Decimal(1)  # δ_{-1}

    k = 1
    extra = 6
    while True:
        ak = period[(k - 1) % len(period)]
        a.append(ak)

        qk = ak * q[k - 1] + q_minus1
        q_minus1 = q[k - 1]
        q.append(qk)

        if k == 1:
            delta_k = -Decimal(ak) * delta[0] + delta_minus1
        else:
            delta_k = -Decimal(ak) * delta[k - 1] + delta[k - 2]
        delta.append(delta_k)

        if qk > B:
            extra -= 1
            if extra <= 0:
                break

        k += 1
        # should never happen for our bounds, but keeps the function total.
        if k > 500:
            break

    max_i = len(a) - 1  # number of digits we will compute for beta's α-numeration

    # α-numeration of beta (Algorithm 3(ii) in arXiv:1904.01874):
    #   b_k = min(a_k, ceil(beta_{k-1}/δ_{k-1}))
    #   beta_k = b_k δ_{k-1} - beta_{k-1}
    b_digits: List[int] = [0]  # 1-indexed
    beta_rem = beta
    for i in range(1, max_i + 1):
        ratio = beta_rem / delta[i - 1]
        bi = ceil_int_dec(ratio)
        if bi > a[i]:
            bi = a[i]
        if bi < 0:
            bi = 0
        b_digits.append(bi)
        beta_rem = Decimal(bi) * delta[i - 1] - beta_rem

    # prefix sums: N_i = Σ_{j=1..i} b_j * q_{j-1}
    prefix: List[int] = [0]
    s = 0
    for i in range(1, len(b_digits)):
        s += b_digits[i] * q[i - 1]
        prefix.append(s)

    # Candidate indices for best right/left α-approximations (Propositions 9 & 10).
    # We enumerate them and pick the smallest right gap / left gap.
    candidates_right = {0}
    for k2 in range(1, (len(b_digits) - 1) // 2 + 1):
        idx_even = 2 * k2
        idx_odd = 2 * k2 - 1
        if idx_even >= len(b_digits):
            break
        P = prefix[idx_odd]
        step = q[idx_odd]
        for j in range(b_digits[idx_even]):
            n = P + j * step
            if 0 <= n <= B:
                candidates_right.add(n)

    candidates_left = {0}
    for k2 in range(0, (len(b_digits) - 2) // 2 + 1):
        idx = 2 * k2
        idx_next = idx + 1
        if idx_next >= len(b_digits):
            break
        P = prefix[idx]
        step = q[idx]
        for j in range(b_digits[idx_next]):
            n = P + j * step
            if 0 <= n <= B:
                candidates_left.add(n)

    best_r_n = 0
    best_r_gap = Decimal(1)  # {n*alpha - beta} in [0,1)
    for n in candidates_right:
        x = frac_dec(alpha * Decimal(n))
        gap = x - beta
        if gap < 0:
            gap += 1
        if gap < best_r_gap:
            best_r_gap = gap
            best_r_n = n

    best_l_n = 0
    best_l_gap = Decimal(1)  # {beta - n*alpha} in [0,1)
    for n in candidates_left:
        x = frac_dec(alpha * Decimal(n))
        gap = beta - x
        if gap < 0:
            gap += 1
        if gap < best_l_gap:
            best_l_gap = gap
            best_l_n = n

    # Closer on the circle is the smaller of left/right gaps.
    return best_r_n if best_r_gap < best_l_gap else best_l_n


def bqa_pi_d(d: int, n: int, pi: Decimal, beta_pi: Decimal) -> Tuple[int, int]:
    """
    Compute BQA_d(pi, n) and return integer pair (a,b).
    """
    sqrt_d = Decimal(d).sqrt()
    a0, period = sqrt_cf_period(d)

    # alpha = frac(sqrt(d)) is [0; a1, a2, ...] where the a_i are from sqrt(d)'s CF.
    alpha = sqrt_d - Decimal(a0)

    # Feasible b bounds for keeping a in [-n,n] when choosing nearest a:
    # a ≈ pi - b*sqrt(d)  => need |a|<=n, so b*sqrt(d) must be within roughly [-n, n] around pi.
    Bpos = int(((Decimal(n) + pi) / sqrt_d).to_integral_value(rounding=ROUND_FLOOR))
    Bpos = min(max(Bpos, 0), n)

    Bneg = int(((Decimal(n) - pi) / sqrt_d).to_integral_value(rounding=ROUND_FLOOR))
    Bneg = min(max(Bneg, 0), n)

    # Best b >= 0 approximating frac(pi)
    b_pos = best_b_positive(alpha, beta_pi, Bpos, period)

    # Best b <= 0 via t=-b >= 0 approximating frac(-pi)=1-frac(pi)
    t = best_b_positive(alpha, Decimal(1) - beta_pi, Bneg, period)
    b_neg = -t

    def candidate_ab(b: int) -> Tuple[int, int, Decimal]:
        a_real = pi - Decimal(b) * sqrt_d
        a = nearest_int_dec(a_real)
        if a > n:
            a = n
        elif a < -n:
            a = -n
        err = abs(Decimal(a) + Decimal(b) * sqrt_d - pi)
        return a, b, err

    a1, b1, e1 = candidate_ab(b_pos)
    a2, b2, e2 = candidate_ab(b_neg)
    return (a2, b2) if e2 < e1 else (a1, b1)


# ---------- Solve & tests ----------


def solve(n: int = 10**13) -> int:
    # Precision: enough to reliably compute α-numeration digits and compare gaps (~1e-13 scale).
    getcontext().prec = 140
    pi = chudnovsky_pi(130)
    beta_pi = frac_dec(pi)

    total = 0
    for d in range(2, 100):
        if is_square(d):
            continue
        a, _b = bqa_pi_d(d, n, pi, beta_pi)
        total += abs(a)
    return total


def run_tests() -> None:
    getcontext().prec = 140
    pi = chudnovsky_pi(130)
    beta_pi = frac_dec(pi)

    # Test values from the problem statement.
    assert bqa_pi_d(2, 10, pi, beta_pi) == (6, -2)
    assert bqa_pi_d(5, 100, pi, beta_pi) == (-55, 26)
    assert bqa_pi_d(7, 10**6, pi, beta_pi) == (560323, -211781)

    a2, _b2 = bqa_pi_d(2, 10**13, pi, beta_pi)
    assert a2 == -6188084046055


def main() -> None:
    run_tests()
    print(solve(10**13))


if __name__ == "__main__":
    main()
