#!/usr/bin/env python3
"""
Project Euler 690: Tom and Jerry

We count "Tom graphs" on n vertices (up to isomorphism) and output T(2019) mod 1_000_000_007.

Key facts used (encoded as generating functions):
- Tom graphs are exactly forests whose connected components are "lobster" trees.
- The number of unlabeled lobster trees has an explicit ordinary generating function in terms of
  the partition generating function P(x) = Π_{k>=1} 1/(1-x^k).

No external libraries are used.
"""

MOD = 1_000_000_007


def partitions_upto(n: int) -> list[int]:
    """Partition numbers p(0..n) modulo MOD (P(x) coefficients)."""
    p = [0] * (n + 1)
    p[0] = 1
    for k in range(1, n + 1):
        for i in range(k, n + 1):
            p[i] += p[i - k]
            if p[i] >= MOD:
                p[i] -= MOD
    return p


def poly_mul(a: list[int], b: list[int], n: int) -> list[int]:
    """Multiply two series a,b modulo MOD, truncated to degree n."""
    mod = MOD
    mod2 = mod * mod
    res = [0] * (n + 1)
    rb = b
    rr = res
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        maxj = n - i
        for j in range(maxj + 1):
            v = rr[i + j] + ai * rb[j]
            if v >= mod2:
                v %= mod
            rr[i + j] = v
    for k in range(n + 1):
        rr[k] %= mod
    return rr


def inv_series(f: list[int], n: int) -> list[int]:
    """
    Series inverse g = 1/f mod x^(n+1), assuming f[0] != 0.
    O(n^2) Newton-free recurrence.
    """
    mod = MOD
    mod2 = mod * mod
    g = [0] * (n + 1)
    g0 = pow(f[0], mod - 2, mod)
    g[0] = g0
    for i in range(1, n + 1):
        s = 0
        for k in range(1, i + 1):
            s += f[k] * g[i - k]
            if s >= mod2:
                s %= mod
        g[i] = (-s * g0) % mod
    return g


def lobster_counts_upto(n: int) -> list[int]:
    """
    Coefficients L[k] for k=0..n where L[k] is # of unlabeled lobster trees on k vertices.

    Uses the explicit generating function (Andrew Howroyd / OEIS A130131):

      P(x) = Π_{k>=1} 1/(1-x^k)
      A(x) = x^2 * ( (P(x)-1/(1-x))^2 / (1-x*P(x))
                   + (P(x^2)-1/(1-x^2))*(1+x*P(x)) / (1-x^2*P(x^2)) ) / 2
             + x*P(x) - x^3/((1-x)^2*(1+x))

    Then L[k] = [x^k] A(x).
    """
    p = partitions_upto(n)
    P = p[:]  # P(x)
    inv2 = (MOD + 1) // 2

    # Q(x) = P(x) - 1/(1-x) where 1/(1-x) = sum_{m>=0} x^m.
    Q = [(P[i] - 1) % MOD for i in range(n + 1)]

    # term1 = Q^2 / (1 - x*P)
    num1 = poly_mul(Q, Q, n)
    den1 = [0] * (n + 1)
    den1[0] = 1
    for i in range(1, n + 1):
        den1[i] = (-P[i - 1]) % MOD  # coefficient of -x*P
    inv_den1 = inv_series(den1, n)
    term1 = poly_mul(num1, inv_den1, n)

    # Build P(x^2) and Q2 = P(x^2) - 1/(1-x^2)
    P2 = [0] * (n + 1)
    Q2 = [0] * (n + 1)
    for i in range(0, n // 2 + 1):
        P2[2 * i] = P[i]
        Q2[2 * i] = (P[i] - 1) % MOD

    # one_plus = 1 + x*P
    one_plus = [0] * (n + 1)
    one_plus[0] = 1
    for i in range(1, n + 1):
        one_plus[i] = P[i - 1]

    # term2 = Q2*(1 + x*P) / (1 - x^2*P(x^2))
    num2 = poly_mul(Q2, one_plus, n)
    den2 = [0] * (n + 1)
    den2[0] = 1
    for i in range(2, n + 1):
        den2[i] = (-P2[i - 2]) % MOD
    inv_den2 = inv_series(den2, n)
    term2 = poly_mul(num2, inv_den2, n)

    s = [(term1[i] + term2[i]) % MOD for i in range(n + 1)]

    # main = x^2 * s / 2
    main = [0] * (n + 1)
    for i in range(0, n - 1):
        main[i + 2] = (s[i] * inv2) % MOD

    # x*P
    xP = [0] * (n + 1)
    for i in range(1, n + 1):
        xP[i] = P[i - 1]

    # last = x^3/((1-x)^2*(1+x))
    # (1-x)^-2 = Σ (m+1) x^m
    A1 = [(i + 1) % MOD for i in range(n + 1)]
    # (1+x)^-1 = Σ (-1)^m x^m
    A2 = [1 if (i % 2 == 0) else MOD - 1 for i in range(n + 1)]
    temp = poly_mul(A1, A2, n)
    last = [0] * (n + 1)
    for i in range(0, n - 2):
        last[i + 3] = temp[i]

    # A = main + xP - last
    A = [(main[i] + xP[i] - last[i]) % MOD for i in range(n + 1)]
    return A


def euler_transform(b: list[int], n: int) -> list[int]:
    """
    Euler transform for unlabeled multisets:
      A(x) = Π_{k>=1} (1 - x^k)^(-b[k])
    Given b[1..n], returns a[0..n] with a[0]=1.
    """
    mod = MOD
    c = [0] * (n + 1)
    for d in range(1, n + 1):
        bd = b[d]
        if bd == 0:
            continue
        addv = (d * bd) % mod
        for k in range(d, n + 1, d):
            c[k] += addv
            if c[k] >= mod:
                c[k] -= mod

    inv = [0] * (n + 1)
    for i in range(1, n + 1):
        inv[i] = pow(i, mod - 2, mod)

    a = [0] * (n + 1)
    a[0] = 1
    mod2 = mod * mod
    for m in range(1, n + 1):
        s = 0
        for k in range(1, m + 1):
            s += c[k] * a[m - k]
            if s >= mod2:
                s %= mod
        a[m] = (s % mod) * inv[m] % mod
    return a


def solve(n: int = 2019) -> int:
    lobsters = lobster_counts_upto(n)
    tom_graphs = euler_transform(lobsters, n)

    # Test values from the problem statement:
    assert tom_graphs[3] == 3
    assert tom_graphs[7] == 37
    assert tom_graphs[10] == 328
    assert tom_graphs[20] == 1416269

    return tom_graphs[n]


if __name__ == "__main__":
    print(solve())
