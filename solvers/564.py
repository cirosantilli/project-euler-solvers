#!/usr/bin/env python3
"""
Project Euler 564 - Maximal Polygons
https://projecteuler.net/problem=564

Compute S(50) to 6 decimal places.

No external libraries are used.
"""
from __future__ import annotations

import math


def build_factorials(n: int) -> list[int]:
    fact = [1] * (n + 1)
    for i in range(2, n + 1):
        fact[i] = fact[i - 1] * i
    return fact


def comb(n: int, k: int, fact: list[int]) -> int:
    if k < 0 or k > n:
        return 0
    if k > n - k:
        k = n - k
    return fact[n] // (fact[k] * fact[n - k])


def maximal_area(groups: list[tuple[int, int]]) -> float:
    """
    Given side-length multiplicities (length, count), return the maximal area
    of a convex polygon with those side lengths.

    The maximal polygon is cyclic. There are two possibilities:
      - circumcenter inside polygon: all central angles are "minor" angles
      - circumcenter outside: exactly one side (necessarily the unique longest)
        uses the "major" central angle

    We detect feasibility of the 'all minor' case and otherwise solve the
    'one major (longest) side' case.

    Let r = 2R (circle diameter), chord length l = r * sin(theta/2).

    All-minor closure:
        sum asin(l/r) = pi
    One-major (longest side L, with multiplicity 1) closure:
        sum asin(l/r) = 2 * asin(L/r)

    Area (signed via central angles) becomes:
        A = 1/4 * sum s_i * l_i * sqrt(r^2 - l_i^2)
    where s_i is +1 for minor edges, -1 for the major edge.
    """
    asin = math.asin
    sqrt = math.sqrt
    pi = math.pi

    maxL = 0
    sum_len = 0.0
    # compute max length and perimeter
    for l, c in groups:
        if l > maxL:
            maxL = l
        sum_len += l * c

    # feasibility test for all-minor at r = maxL
    inv0 = 1.0 / maxL
    sum_asin_at_min = 0.0
    for l, c in groups:
        u = l * inv0
        if u > 1.0:
            u = 1.0
        sum_asin_at_min += c * asin(u)

    # if sum_asin(maxL) >= pi then all-minor closure has a solution (possibly at boundary)
    all_minor = sum_asin_at_min >= pi - 1e-15

    if all_minor:
        # solve f(r) = sum c*asin(l/r) - pi = 0, with r in [maxL, +inf)
        f_at_lo = sum_asin_at_min - pi
        if abs(f_at_lo) < 1e-15:
            r = float(maxL)  # boundary solution (some side is a diameter)
        else:
            eps = 1e-15
            lo = maxL * (1.0 + eps)
            # find hi such that f(hi) < 0
            hi = lo * 2.0

            def eval_f_df(r: float) -> tuple[float, float]:
                inv = 1.0 / r
                r2 = r * r
                f = -pi
                df = 0.0
                for l, c in groups:
                    u = l * inv
                    t = 1.0 - u * u
                    if t <= 0.0:
                        t = 0.0
                    s = sqrt(t)
                    # keep away from division by zero; boundary roots are handled above
                    if s < 1e-18:
                        s = 1e-18
                    f += c * asin(u)
                    df -= c * l / (r2 * s)
                return f, df

            f_hi, _ = eval_f_df(hi)
            while f_hi > 0.0:
                hi *= 2.0
                f_hi, _ = eval_f_df(hi)

            # good initial guess for large n: r ≈ perimeter / pi
            r = sum_len / pi
            if r <= lo or r >= hi:
                r = 0.5 * (lo + hi)

            # bracketed Newton
            for _ in range(24):
                f, df = eval_f_df(r)
                if abs(f) < 1e-15:
                    break
                if f > 0.0:
                    lo = r
                else:
                    hi = r
                rn = r - f / df
                if rn <= lo or rn >= hi or not math.isfinite(rn):
                    rn = 0.5 * (lo + hi)
                r = rn
                if hi - lo < 1e-14 * hi:
                    break

        # area
        inv = 1.0 / r
        area_sum = 0.0
        for l, c in groups:
            u = l * inv
            t = 1.0 - u * u
            if t <= 0.0:
                continue
            area_sum += c * l * (r * sqrt(t))
        return 0.25 * area_sum

    # one-major case: major side must be the (unique) longest side
    L = maxL

    eps = 1e-15
    lo = L * (1.0 + eps)
    hi = lo * 2.0

    def eval_f_df_major(r: float) -> tuple[float, float]:
        inv = 1.0 / r
        r2 = r * r
        f = 0.0
        df = 0.0
        for l, c in groups:
            u = l * inv
            t = 1.0 - u * u
            if t <= 0.0:
                t = 0.0
            s = sqrt(t)
            if s < 1e-18:
                s = 1e-18
            f += c * asin(u)
            df -= c * l / (r2 * s)
        uL = L * inv
        tL = 1.0 - uL * uL
        if tL <= 0.0:
            tL = 0.0
        sL = sqrt(tL)
        if sL < 1e-18:
            sL = 1e-18
        f -= 2.0 * asin(uL)
        df += 2.0 * L / (r2 * sL)
        return f, df

    f_lo, _ = eval_f_df_major(lo)
    f_hi, _ = eval_f_df_major(hi)
    while f_hi < 0.0:
        hi *= 2.0
        f_hi, _ = eval_f_df_major(hi)

    r = lo * 1.1
    if r >= hi:
        r = 0.5 * (lo + hi)

    for _ in range(24):
        f, df = eval_f_df_major(r)
        if abs(f) < 1e-15:
            break
        if f > 0.0:
            hi = r
        else:
            lo = r
        rn = r - f / df
        if rn <= lo or rn >= hi or not math.isfinite(rn):
            rn = 0.5 * (lo + hi)
        r = rn
        if hi - lo < 1e-14 * hi:
            break

    inv = 1.0 / r
    area_sum = 0.0
    max_term = 0.0
    for l, c in groups:
        u = l * inv
        t = 1.0 - u * u
        if t <= 0.0:
            continue
        term = c * l * (r * sqrt(t))
        area_sum += term
        if l == L:
            # in the one-major case, the longest side must be unique (c == 1)
            max_term = l * (r * sqrt(t))
    area_sum -= 2.0 * max_term
    return 0.25 * area_sum


def expected_area(n: int, fact: list[int]) -> float:
    """
    E(n): Expected maximal area for a random integer split of 2n-3 into n parts.
    We sum over multisets (integer partitions of k=n-3) and weight by the number
    of compositions that correspond to that multiset.
    """
    k = n - 3
    total = comb(2 * n - 4, n - 1, fact)
    total_inv = 1.0 / total
    fact_n = fact[n]

    parts: list[int] = []
    # Kahan summation
    s = 0.0
    c = 0.0

    def dfs(rem: int, max_p: int) -> None:
        nonlocal s, c
        if rem == 0:
            t = len(parts)
            m0 = n - t  # number of zeros in the partition of k -> length 1 segments
            denom = fact[m0]

            groups: list[tuple[int, int]] = [(1, m0)]
            i = 0
            while i < t:
                v = parts[i]
                j = i + 1
                while j < t and parts[j] == v:
                    j += 1
                cnt = j - i
                groups.append((v + 1, cnt))  # extra v -> length 1+v
                denom *= fact[cnt]
                i = j

            weight = fact_n // denom  # multinomial coefficient
            area = maximal_area(groups)
            contrib = area * (weight * total_inv)

            y = contrib - c
            tt = s + y
            c = (tt - s) - y
            s = tt
            return

        for p in range(min(rem, max_p), 0, -1):
            parts.append(p)
            dfs(rem - p, p)
            parts.pop()

    dfs(k, k)
    return s


def solve(limit: int = 50) -> float:
    # We need factorials up to 2*limit (for binomials up to 2n-4)
    fact = build_factorials(2 * limit + 10)

    S = 0.0
    E_cache = {}

    for n in range(3, limit + 1):
        e = expected_area(n, fact)
        E_cache[n] = e
        S += e

    # Asserts for test values given in the problem statement
    assert round(E_cache[3], 6) == 0.433013
    assert round(E_cache[4], 6) == 1.299038

    S3 = E_cache[3]
    S4 = E_cache[3] + E_cache[4]
    S5 = S4 + E_cache[5]
    S10 = sum(E_cache[i] for i in range(3, 11))

    assert round(S3, 6) == 0.433013
    assert round(S4, 6) == 1.732051
    assert round(S5, 6) == 4.604767
    assert round(S10, 6) == 66.955511

    return S


if __name__ == "__main__":
    ans = solve(50)
    print(f"{ans:.6f}")
