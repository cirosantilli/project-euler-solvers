#!/usr/bin/env python3
"""
Project Euler 438 - Integer part of polynomial equation's solutions

We enumerate all monic integer polynomials of degree n:
    p(x) = x^n + a1*x^(n-1) + ... + an
whose n real roots x1 <= x2 <= ... <= xn satisfy:
    floor(xi) = i  for i = 1..n.

Let S(t) = sum(|a_i|) over coefficients, and the task is:
    sum S(t) over all valid tuples t for n=7.

Key approach:
 1) Use forward-difference / Newton (binomial/falling factorial) basis.
 2) Enumerate possible integer values p(1),...,p(n) using tight bounds.
 3) Enforce integrality of power-basis coefficients via factorial divisibility.
 4) Compute p(n+1) from the condition leading coefficient = 1.
 5) Filter candidates via Sturm sequence root counting (exact, no floating point).
"""

from fractions import Fraction
from math import factorial


# ---------------- Polynomial utilities (exact arithmetic) ---------------- #

def poly_trim(p):
    """Trim leading zeros (descending representation)."""
    i = 0
    while i < len(p) and p[i] == 0:
        i += 1
    return p[i:] if i < len(p) else [0]


def poly_mul_int(a, b):
    """Multiply integer polynomials in descending coefficient order."""
    a = poly_trim(a)
    b = poly_trim(b)
    if a == [0] or b == [0]:
        return [0]
    res = [0] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            res[i + j] += ca * cb
    return poly_trim(res)


def poly_add_int(a, b):
    """Add integer polynomials (descending order)."""
    a = poly_trim(a)
    b = poly_trim(b)
    if len(a) < len(b):
        a = [0] * (len(b) - len(a)) + a
    elif len(b) < len(a):
        b = [0] * (len(a) - len(b)) + b
    return poly_trim([x + y for x, y in zip(a, b)])


def poly_deriv_int(p):
    """Derivative of integer polynomial (descending)."""
    p = poly_trim(p)
    deg = len(p) - 1
    if deg <= 0:
        return [0]
    res = []
    for i, coef in enumerate(p[:-1]):
        power = deg - i
        res.append(coef * power)
    return poly_trim(res)


def poly_eval_frac(p, x):
    """Evaluate polynomial (Fraction coefficients or int) at Fraction x."""
    v = Fraction(0, 1)
    for c in p:
        v = v * x + c
    return v


def poly_divmod_frac(a, b):
    """Polynomial division over Fractions. Returns (q, r) in descending lists."""
    a = poly_trim(a)
    b = poly_trim(b)
    if b == [0]:
        raise ZeroDivisionError("division by zero polynomial")
    da = len(a) - 1
    db = len(b) - 1
    if da < db:
        return [Fraction(0)], a[:]
    q = [Fraction(0)] * (da - db + 1)
    r = a[:]
    while r != [0] and (len(r) - 1) >= db:
        dr = len(r) - 1
        lead = r[0] / b[0]
        shift = dr - db
        q[shift] = lead
        sub = [Fraction(0)] * shift + [lead * bc for bc in b]
        if len(sub) < len(r):
            sub += [Fraction(0)] * (len(r) - len(sub))
        r = [rc - sc for rc, sc in zip(r, sub)]
        r = poly_trim(r)
    return poly_trim(q), r


def poly_gcd_over_Q(p_int, q_int):
    """GCD of integer polys over Q, returned monic (Fractions)."""
    a = [Fraction(c) for c in poly_trim(p_int)]
    b = [Fraction(c) for c in poly_trim(q_int)]
    while b != [0]:
        _, r = poly_divmod_frac(a, b)
        a, b = b, r
    if a == [0]:
        return [Fraction(0)]
    lc = a[0]
    a = [c / lc for c in a]
    return poly_trim(a)


# ---------------- Sturm sequence & root counting ---------------- #

def sturm_sequence(p_int):
    """Compute Sturm sequence using exact Fraction division."""
    p0 = [Fraction(c) for c in poly_trim(p_int)]
    p1 = [Fraction(c) for c in poly_trim(poly_deriv_int(p_int))]
    seq = [p0, p1]
    while seq[-1] != [0]:
        _, r = poly_divmod_frac(seq[-2], seq[-1])
        r = poly_trim(r)
        if r == [0]:
            break
        seq.append([-c for c in r])
    return seq


def sign_variations_at(seq, x_int):
    """
    Compute V(x) = number of sign changes ignoring zeros at integer x.
    """
    x = Fraction(x_int, 1)
    signs = []
    for p in seq:
        v = poly_eval_frac(p, x)
        if v == 0:
            continue
        signs.append(1 if v > 0 else -1)
    vcount = 0
    for i in range(1, len(signs)):
        if signs[i] != signs[i - 1]:
            vcount += 1
    return vcount


def count_roots_open_closed(seq, a, b):
    """
    Sturm theorem: number of distinct real roots in (a, b] equals V(a) - V(b),
    where V ignores zeros. Works for square-free polynomials.
    """
    return sign_variations_at(seq, a) - sign_variations_at(seq, b)


def satisfies_floor_conditions(p_int, n):
    """
    Check the exact condition: the n real roots satisfy floor(x_i)=i.
    Equivalent to: exactly 1 root in [i, i+1) for i=1..n, with no multiplicities.
    Uses Sturm counting and a square-free check.
    """
    # Ensure square-free
    g = poly_gcd_over_Q(p_int, poly_deriv_int(p_int))
    if len(g) > 1:  # degree >= 1 => repeated root
        return False

    seq = sturm_sequence(p_int)

    # Helper for endpoint root check
    def is_root(k):
        return poly_eval_frac([Fraction(c) for c in p_int], Fraction(k, 1)) == 0

    # For each interval [i, i+1):
    for i in range(1, n + 1):
        # count roots in (i, i+1]
        c = count_roots_open_closed(seq, i, i + 1)
        # exclude root at i+1 (belongs to next interval)
        if is_root(i + 1):
            c -= 1
        # include root at i (belongs to this interval)
        if is_root(i):
            c += 1
        if c != 1:
            return False

    return True


# ---------------- Main enumeration using forward differences ---------------- #

def poly_from_forward_differences(n, b_list):
    """
    Given b0..b_{n-1} where b_k = Δ^k p(1), and monic => b_n = n!,
    build the polynomial in standard power basis.

    Use falling factorial basis:
    p(x) = sum_{k=0}^n c_k * (x-1)(x-2)...(x-k)
    where c_k = b_k / k!  (must be integer for integer coefficients).
    """
    fact = [factorial(i) for i in range(n + 1)]
    c = [0] * (n + 1)
    for k in range(n):
        c[k] = b_list[k] // fact[k]
    c[n] = 1  # b_n / n! = 1

    # basis[k] = Π_{t=1..k} (x - t)
    basis = [[1]]
    for k in range(1, n + 1):
        basis.append(poly_mul_int(basis[-1], [1, -k]))

    poly = [0]
    for k in range(n + 1):
        if c[k] == 0:
            continue
        term = [coef * c[k] for coef in basis[k]]
        poly = poly_add_int(poly, term)

    # Ensure exact degree n (pad if needed)
    poly = poly_trim(poly)
    if len(poly) < n + 1:
        poly = [0] * (n + 1 - len(poly)) + poly
    return poly


def solve_for_n(n):
    """
    Returns (count, sum_S).
    """
    fact = [factorial(i) for i in range(n + 1)]

    # binomial coefficients C[m][k] for 0<=m<=n
    C = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        C[i][0] = C[i][i] = 1
        for j in range(1, i):
            C[i][j] = C[i - 1][j - 1] + C[i - 1][j]

    # bounds for y_k = p(k) for k=1..n+1:
    # |p(k)| <= (k-1)! * (n-k+1)!
    y_lo = [0] * (n + 2)
    y_hi = [0] * (n + 2)
    for k in range(1, n + 2):
        M = factorial(k - 1) * factorial(n - k + 1) if (n - k + 1) >= 0 else 0
        s = -1 if ((n - k + 1) % 2 == 1) else 1  # (-1)^(n-k+1)
        if s == 1:
            y_lo[k], y_hi[k] = 0, M
        else:
            y_lo[k], y_hi[k] = -M, 0

    # monic constraint (Δ^n p(1) = n!) gives:
    # y_{n+1} = n! + sum_{i=1..n} coeff[i] * y_i
    coeff = [0] * (n + 1)
    for i in range(1, n + 1):
        coeff[i] = (-1 if ((n - i) % 2 == 1) else 1) * C[n][i - 1]

    # contribution suffix min/max for pruning y_{n+1} into [0,n!]
    contrib_min = [0] * (n + 2)
    contrib_max = [0] * (n + 2)
    for i in range(1, n + 1):
        a = coeff[i] * y_lo[i]
        b = coeff[i] * y_hi[i]
        contrib_min[i] = min(a, b)
        contrib_max[i] = max(a, b)

    suffix_min = [0] * (n + 3)
    suffix_max = [0] * (n + 3)
    for i in range(n, 0, -1):
        suffix_min[i] = suffix_min[i + 1] + contrib_min[i]
        suffix_max[i] = suffix_max[i + 1] + contrib_max[i]

    def iter_congruent(lo, hi, mod, rem):
        """Yield integers y in [lo,hi] with y ≡ rem (mod mod)."""
        if mod == 1:
            return range(lo, hi + 1)
        start = lo + ((rem - lo) % mod)
        return range(start, hi + 1, mod)

    total_count = 0
    total_sumS = 0

    y_vals = [0] * (n + 1)  # y_vals[i] = y_{i+1}
    b_vals = []

    def dfs(m, partial_y_np1):
        """
        m is order of difference being determined (0..n-1).
        We choose y_{m+1} and compute b_m = y_{m+1} - base.
        Also prune based on possible y_{n+1} range.
        """
        nonlocal total_count, total_sumS

        k = m + 1  # selecting y_k

        # compute base = sum_{j=0..m-1} b_j * C(m, j)
        base = 0
        for j in range(m):
            base += b_vals[j] * C[m][j]

        mod = fact[m]
        for y in iter_congruent(y_lo[k], y_hi[k], mod, base):
            bm = y - base
            if bm % fact[m] != 0:
                continue

            y_vals[k - 1] = y
            b_vals.append(bm)

            new_partial = partial_y_np1 + coeff[k] * y
            cur = fact[n] + new_partial

            # Remaining y contributions can only move y_{n+1} within suffix range
            lo_possible = cur + suffix_min[k + 1]
            hi_possible = cur + suffix_max[k + 1]

            if hi_possible < 0 or lo_possible > fact[n]:
                b_vals.pop()
                continue

            if k == n:
                # Determine y_{n+1} exactly from monic constraint
                y_np1 = fact[n] + new_partial
                if not (0 <= y_np1 <= fact[n]):
                    b_vals.pop()
                    continue

                # Build polynomial from differences and validate via Sturm
                poly = poly_from_forward_differences(n, b_vals)

                # Must be monic and correct degree
                if len(poly) != n + 1 or poly[0] != 1:
                    b_vals.pop()
                    continue

                if satisfies_floor_conditions(poly, n):
                    total_count += 1
                    total_sumS += sum(abs(c) for c in poly[1:])

                b_vals.pop()
                continue

            dfs(m + 1, new_partial)
            b_vals.pop()

    dfs(0, 0)
    return total_count, total_sumS


def main():
    # Test case from the problem statement:
    c4, s4 = solve_for_n(4)
    assert c4 == 12, (c4, s4)
    assert s4 == 2087, (c4, s4)

    # Final answer:
    c7, s7 = solve_for_n(7)
    print(s7)


if __name__ == "__main__":
    main()

