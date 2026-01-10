#!/usr/bin/env python3
"""
Project Euler 438

We count integer coefficient tuples (a1..an) for the monic polynomial

    f(x) = x^n + a1 x^(n-1) + ... + an

whose n real roots x1 < ... < xn satisfy floor(xi) = i.

Key equivalence:
For infinitesimal epsilon > 0, the root-floor condition is equivalent to
the sign alternation constraints:

    f(n+1-ε) > 0
    f(n-ε)   < 0
    f(n-1-ε) > 0
    ...
    f(1-ε)   (sign depends on parity)

Subtract consecutive inequalities to obtain constraints on Δf at shifted points,
repeating to eliminate coefficients. After n-k forward differences, constraints
depend only on a1..ak and become linear inequalities in ak with ε-polynomial
right-hand side. Interpreting ε as a positive infinitesimal yields exact integer
bounds for each ak, enabling a tight recursive enumeration (not brute force).

No external libraries are used.
"""

from math import comb


def sum_abs_range(lo: int, hi: int) -> int:
    """Sum_{x=lo..hi} |x| for integers lo<=hi."""
    if lo > hi:
        return 0
    if hi < 0:
        # all negative: |x| = -x
        cnt = hi - lo + 1
        return -(lo + hi) * cnt // 2
    if lo > 0:
        # all positive: |x| = x
        cnt = hi - lo + 1
        return (lo + hi) * cnt // 2
    # crosses 0
    neg = (-lo) * ((-lo) + 1) // 2
    pos = hi * (hi + 1) // 2
    return neg + pos


def precompute_P(n: int):
    """
    Precompute ε-polynomial coefficients for all terms needed in the recursion.

    For each k=1..n and m=1..k+1 we use the inequality:
        (-1)^(k+1-m) * Δ^(n-k) f(m-ε) > 0

    Expand Δ^(n-k) f(m-ε) as:
        A0(k,m) * a_k + sum_{i=0..k-1} P(k,m,i) * a_i
    where a_0 is the implicit coefficient 1 of x^n.

    We store:
        P[(k,m,i)] = ε-polynomial list [c0,c1,...,cn] for contribution of a_i
        A0[(k,m)]  = integer coefficient for a_k (constant in ε)
    """
    maxdeg = n
    max_base = 2 * n + 1  # sufficient for m+j where m<=n+1 and j<=n

    # (base - ε)^p as ε-polynomial
    pow_shift = {}
    for base in range(1, max_base + 1):
        for p in range(0, n + 1):
            coeffs = [0] * (maxdeg + 1)
            # (base-ε)^p = sum_{e=0..p} C(p,e) base^(p-e) (-ε)^e
            for e in range(p + 1):
                coeffs[e] = comb(p, e) * (base ** (p - e)) * ((-1) ** e)
            pow_shift[(base, p)] = coeffs

    # T(k,m,i) = Δ^(n-k) x^(n-i) evaluated at x=m-ε as ε-polynomial
    T = {}
    for k in range(1, n + 1):
        r = n - k
        # Δ^r f(x) = sum_{j=0..r} (-1)^(r-j) C(r,j) f(x+j)
        cjs = [((-1) ** (r - j)) * comb(r, j) for j in range(r + 1)]
        for m in range(1, k + 2):
            for i in range(0, k + 1):
                p = n - i
                acc = [0] * (maxdeg + 1)
                for j, cj in enumerate(cjs):
                    if cj == 0:
                        continue
                    poly = pow_shift[(m + j, p)]
                    for d in range(maxdeg + 1):
                        acc[d] += cj * poly[d]
                T[(k, m, i)] = acc

    # Apply alternating sign factor s = (-1)^(k+1-m)
    P = {}
    A0 = {}
    for k in range(1, n + 1):
        r = n - k
        fact = 1
        for t in range(2, r + 1):
            fact *= t  # (n-k)!
        for m in range(1, k + 2):
            s = 1 if ((k + 1 - m) & 1) == 0 else -1
            for i in range(0, k + 1):
                poly = T[(k, m, i)]
                if s == 1:
                    P[(k, m, i)] = poly
                else:
                    P[(k, m, i)] = [-x for x in poly]
            A0[(k, m)] = s * fact  # coefficient for a_k (constant)
    return P, A0


def first_nonzero_sign(poly, start=1) -> int:
    """Return sign of the first nonzero coefficient poly[start:], else 0."""
    for i in range(start, len(poly)):
        v = poly[i]
        if v:
            return 1 if v > 0 else -1
    return 0


def solve(n: int):
    """
    Return (count, total) where:
      - count is the number of valid integer tuples (a1..an)
      - total is sum over tuples of S(t)=sum_i |ai|
    """
    if n == 1:
        # f(x)=x+a1, root in [1,2) implies a1=-1
        return 1, 1

    P, A0 = precompute_P(n)

    # B[(k,m)] is ε-polynomial for the current "constant part" of inequality
    #   A0(k,m)*a_k + B(k,m) > 0
    # after substituting fixed a1..a_{k-1}.
    B = {}
    for k in range(1, n + 1):
        for m in range(1, k + 2):
            B[(k, m)] = P[(k, m, 0)].copy()  # contribution from a0=1

    def apply(i: int, val: int):
        """Update all future B(kp,m) by adding val * P(kp,m,i)."""
        if val == 0:
            return
        for kp in range(i + 1, n + 1):
            for m in range(1, kp + 2):
                poly = P[(kp, m, i)]
                Bb = B[(kp, m)]
                for d in range(n + 1):
                    Bb[d] += val * poly[d]

    def bound_from_ineq(A0_val: int, Bpoly):
        """
        Solve: A0_val * a + Bpoly(ε) > 0 with ε -> 0+ lexicographic sign.

        Returns:
          ('lb', L) meaning a >= L
          ('ub', U) meaning a <= U
        """
        b0 = Bpoly[0]
        if A0_val > 0:
            # a > (-B)/A0
            num = -b0
            den = A0_val
            if num % den:
                return "lb", num // den + 1
            x0 = num // den
            # tie at constant term; inspect next ε coefficient
            s = first_nonzero_sign(Bpoly, start=1)
            return "lb", x0 if s > 0 else x0 + 1
        else:
            # a < (B)/(-A0)
            den = -A0_val
            num = b0
            if num % den:
                return "ub", num // den
            x0 = num // den
            s = first_nonzero_sign(Bpoly, start=1)
            return "ub", x0 if s > 0 else x0 - 1

    def bounds_for_k(k: int):
        """Intersect all (k+1) inequalities to get integer bounds for a_k."""
        lb = -(10**30)
        ub = 10**30
        for m in range(1, k + 2):
            typ, bnd = bound_from_ineq(A0[(k, m)], B[(k, m)])
            if typ == "lb":
                if bnd > lb:
                    lb = bnd
            else:
                if bnd < ub:
                    ub = bnd
        return lb, ub

    count = 0
    total = 0

    def dfs(k: int, prefix_abs: int):
        nonlocal count, total
        if k == n:
            lb, ub = bounds_for_k(n)
            if lb > ub:
                return
            cnt = ub - lb + 1
            count += cnt
            total += cnt * prefix_abs + sum_abs_range(lb, ub)
            return

        lb, ub = bounds_for_k(k)
        if lb > ub:
            return

        for ak in range(lb, ub + 1):
            apply(k, ak)
            dfs(k + 1, prefix_abs + abs(ak))
            apply(k, -ak)

    dfs(1, 0)
    return count, total


def main():
    # Test values from the problem statement:
    c4, s4 = solve(4)
    assert c4 == 12
    assert s4 == 2087

    # Target instance:
    _, ans = solve(7)
    print(ans)


if __name__ == "__main__":
    main()
