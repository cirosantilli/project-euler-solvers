#!/usr/bin/env python3
"""
Project Euler 438 - Integer part of polynomial equation's solutions

We enumerate all monic integer polynomials of degree n:
    p(x) = x^n + a1*x^(n-1) + ... + an
whose n real roots x1 <= x2 <= ... <= xn satisfy:
    floor(xi) = i  for i = 1..n.

Let S(t) = sum(|a_i|) over the (non-leading) coefficients.
Task: compute sum S(t) over all valid tuples t for n=7.

Core enumeration strategy:
  - Work with integer values y_k = p(k) at integer points k=1..n, bounded by
        |p(k)| <= (k-1)! * (n-k+1)!,
    with a known sign pattern.
  - Use forward differences b_m = Δ^m p(1) and the Newton (falling-factorial) basis:
        p(x) = Σ c_m (x-1)(x-2)...(x-m),  where c_m = b_m / m!.
    Integrality of power-basis coefficients implies b_m ≡ 0 (mod m!) for m<n.
  - Monic constraint fixes the nth forward difference: Δ^n p(1) = n!.
    That gives y_{n+1} = p(n+1) as a linear form in y_1..y_n, enabling pruning.

Exact validation:
  - Candidate polynomials are verified with Sturm's theorem to ensure
    exactly one real root in each interval [i, i+1) for i=1..n.
  - This file uses an integer-only Sturm chain built with a *pseudo-remainder sequence* (PRS),
    avoiding Fractions for speed.

No external libraries are used.
"""

from math import factorial, gcd


# ---------------- Integer polynomial helpers (descending coefficient order) ---------------- #

def poly_trim(p):
    i = 0
    while i < len(p) and p[i] == 0:
        i += 1
    return p[i:] if i < len(p) else [0]


def poly_degree(p):
    p = poly_trim(p)
    return len(p) - 1 if p != [0] else -1


def poly_add_int(a, b):
    a = poly_trim(a)
    b = poly_trim(b)
    if len(a) < len(b):
        a = [0] * (len(b) - len(a)) + a
    elif len(b) < len(a):
        b = [0] * (len(a) - len(b)) + b
    return poly_trim([x + y for x, y in zip(a, b)])


def poly_mul_int(a, b):
    a = poly_trim(a)
    b = poly_trim(b)
    if a == [0] or b == [0]:
        return [0]
    res = [0] * (len(a) + len(b) - 1)
    for i, ca in enumerate(a):
        for j, cb in enumerate(b):
            res[i + j] += ca * cb
    return poly_trim(res)


def poly_deriv_int(p):
    p = poly_trim(p)
    d = len(p) - 1
    if d <= 0:
        return [0]
    return poly_trim([p[i] * (d - i) for i in range(len(p) - 1)])


def poly_eval_int(p, x):
    v = 0
    for c in p:
        v = v * x + c
    return v


def poly_content_gcd(p):
    g = 0
    for c in p:
        g = gcd(g, abs(c))
    return g


def poly_primitive_by_content(p):
    """
    Divide by the gcd of coefficients (a positive integer).
    IMPORTANT: we do NOT flip sign here; multiplying a single Sturm-chain element by -1
    would change sign-variation counts.
    """
    p = poly_trim(p)
    if p == [0]:
        return [0]
    g = poly_content_gcd(p)
    if g > 1:
        p = [c // g for c in p]
    return p


# ---------------- Integer pseudo-remainder (PRS) ---------------- #

def poly_prem_pos(A, B):
    """
    Pseudo-remainder of A by B, using a *positive* leading-coefficient factor.

    Let deg(A)=da, deg(B)=db, m = da - db + 1.
    Over Q, A = Q*B + R. The classical pseudo-remainder is lc(B)^m * R (integer coefficients).
    If lc(B) is negative, lc(B)^m may be negative and would spoil Sturm scaling.

    This function instead computes |lc(B)|^m * R (always a *positive* scaling of R),
    which is safe for Sturm sequences (allowed: multiply remainders by positive constants).
    """
    A = poly_trim(A)
    B = poly_trim(B)
    if B == [0]:
        raise ZeroDivisionError("division by zero polynomial")

    da = poly_degree(A)
    db = poly_degree(B)
    if da < db:
        return A

    lc = B[0]
    L = abs(lc)
    s = 1 if lc > 0 else -1  # sign(lc)

    R = A[:]
    while R != [0] and poly_degree(R) >= db:
        R = poly_trim(R)
        dr = poly_degree(R)
        t = dr - db
        lead = R[0]

        # R = L*R - lead*s * x^t * B
        R = [c * L for c in R]
        sub = [lead * s * c for c in B] + [0] * t  # multiply B by x^t (append zeros)

        # length-align
        if len(sub) < len(R):
            sub += [0] * (len(R) - len(sub))
        elif len(R) < len(sub):
            R += [0] * (len(sub) - len(R))

        R = [rc - sc for rc, sc in zip(R, sub)]
        R = poly_trim(R)

    return R


def poly_gcd_degree_over_Q(p, q):
    """
    Degree of gcd(p, q) over Q[x], using a primitive PRS (integer-only).
    For square-free checking we only need to know whether degree >= 1.
    """
    a = poly_primitive_by_content(p)
    b = poly_primitive_by_content(q)
    while b != [0]:
        r = poly_prem_pos(a, b)
        r = poly_primitive_by_content(r)
        a, b = b, r
    return poly_degree(a)


# ---------------- Sturm chain (integer-only PRS) ---------------- #

def sturm_sequence_int(p_int):
    """
    Build a Sturm sequence using a PRS-based remainder, avoiding Fractions.

    Standard Sturm recursion: p0 = p, p1 = p', p_{k+1} = -rem(p_{k-1}, p_k).
    Here we compute a positive multiple of rem(...) via poly_prem_pos, which is valid.
    """
    p0 = poly_primitive_by_content(p_int)
    p1 = poly_primitive_by_content(poly_deriv_int(p0))
    seq = [p0, p1]
    while p1 != [0]:
        r = poly_prem_pos(p0, p1)           # positive multiple of rem(p0, p1)
        r = poly_primitive_by_content(r)    # positive scaling only
        if r == [0]:
            break
        r = [-c for c in r]                 # Sturm's required negation
        r = poly_primitive_by_content(r)
        seq.append(r)
        p0, p1 = p1, r
    return seq


def sign_variations_at(seq, x_int):
    """
    Compute V(x) = number of sign changes in seq evaluated at integer x,
    skipping zeros (as required by Sturm).
    """
    signs = []
    for p in seq:
        v = poly_eval_int(p, x_int)
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
    For square-free p: number of roots in (a, b] is V(a) - V(b).
    We later adjust endpoints to get [i, i+1).
    """
    return sign_variations_at(seq, a) - sign_variations_at(seq, b)


def satisfies_floor_conditions(p_int, n):
    """
    Verify: exactly one real root in each interval [i, i+1) for i=1..n,
    and all roots are simple.
    """
    # square-free check
    if poly_gcd_degree_over_Q(p_int, poly_deriv_int(p_int)) >= 1:
        return False

    seq = sturm_sequence_int(p_int)

    def is_root(k):
        return poly_eval_int(p_int, k) == 0

    for i in range(1, n + 1):
        # roots in (i, i+1]
        c = count_roots_open_closed(seq, i, i + 1)
        # remove roots at i+1 (belong to next interval [i+1, i+2))
        if is_root(i + 1):
            c -= 1
        # add roots at i (belong to [i, i+1))
        if is_root(i):
            c += 1
        if c != 1:
            return False

    return True


# ---------------- Build polynomial from forward differences ---------------- #

def poly_from_forward_differences(n, b_list):
    """
    b_list holds b_m = Δ^m p(1) for m=0..n-1, with Δ^n p(1)=n! (monic).
    Build p(x) in the standard power basis (descending integer coeff list).
    """
    fact = [factorial(i) for i in range(n + 1)]

    # c_m = b_m / m! must be integer; c_n = 1
    c = [0] * (n + 1)
    for m in range(n):
        c[m] = b_list[m] // fact[m]
    c[n] = 1

    # basis[m] = Π_{t=1..m} (x - t) in power basis
    basis = [[1]]
    for m in range(1, n + 1):
        basis.append(poly_mul_int(basis[-1], [1, -m]))

    poly = [0]
    for m in range(n + 1):
        if c[m] == 0:
            continue
        term = [coef * c[m] for coef in basis[m]]
        poly = poly_add_int(poly, term)

    poly = poly_trim(poly)
    if len(poly) < n + 1:
        poly = [0] * (n + 1 - len(poly)) + poly
    return poly


# ---------------- Enumeration ---------------- #

def solve_for_n(n):
    """
    Returns (count, sum_S) where sum_S = Σ_t S(t).
    """
    fact = [factorial(i) for i in range(n + 1)]

    # binomial C[m][k] for 0<=m<=n
    C = [[0] * (n + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        C[i][0] = C[i][i] = 1
        for j in range(1, i):
            C[i][j] = C[i - 1][j - 1] + C[i - 1][j]

    # bounds for y_k = p(k), k=1..n+1:
    y_lo = [0] * (n + 2)
    y_hi = [0] * (n + 2)
    for k in range(1, n + 2):
        M = factorial(k - 1) * factorial(n - k + 1) if (n - k + 1) >= 0 else 0
        sign = -1 if ((n - k + 1) % 2 == 1) else 1  # (-1)^(n-k+1)
        if sign == 1:
            y_lo[k], y_hi[k] = 0, M
        else:
            y_lo[k], y_hi[k] = -M, 0

    # monic constraint on forward differences yields:
    # y_{n+1} = n! + Σ_{i=1..n} coeff[i] * y_i
    coeff = [0] * (n + 1)
    for i in range(1, n + 1):
        coeff[i] = (-1 if ((n - i) % 2 == 1) else 1) * C[n][i - 1]

    # suffix pruning for y_{n+1} ∈ [0, n!]
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
        """Yield y in [lo,hi] with y ≡ rem (mod mod)."""
        if mod == 1:
            return range(lo, hi + 1)
        start = lo + ((rem - lo) % mod)
        return range(start, hi + 1, mod)

    total_count = 0
    total_sumS = 0

    b_vals = []

    def dfs(m, partial_y_np1):
        """
        Choose y_{m+1} consistent with divisibility b_m ≡ 0 (mod m!)
        and prune using possible range for y_{n+1}.
        """
        nonlocal total_count, total_sumS

        k = m + 1  # choosing y_k = p(k)

        # base = Σ_{j=0..m-1} b_j * C(m, j) so that b_m = y_k - base
        base = 0
        for j in range(m):
            base += b_vals[j] * C[m][j]

        mod = fact[m]
        for y in iter_congruent(y_lo[k], y_hi[k], mod, base):
            bm = y - base
            if bm % fact[m] != 0:
                continue

            b_vals.append(bm)

            new_partial = partial_y_np1 + coeff[k] * y
            cur = fact[n] + new_partial

            lo_possible = cur + suffix_min[k + 1]
            hi_possible = cur + suffix_max[k + 1]
            if hi_possible < 0 or lo_possible > fact[n]:
                b_vals.pop()
                continue

            if k == n:
                y_np1 = fact[n] + new_partial
                if not (0 <= y_np1 <= fact[n]):
                    b_vals.pop()
                    continue

                poly = poly_from_forward_differences(n, b_vals)
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
    # Test values from the problem statement:
    c4, s4 = solve_for_n(4)
    assert c4 == 12, (c4, s4)
    assert s4 == 2087, (c4, s4)

    # Final answer for n=7:
    c7, s7 = solve_for_n(7)
    assert s7 == 2046409616809, s7
    print(s7)


if __name__ == "__main__":
    main()

