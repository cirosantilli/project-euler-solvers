#!/usr/bin/env python3
"""
Project Euler 520: Simbers

We define a simber to be a positive integer in which:
- any odd digit, if present, occurs an odd number of times;
- any even digit, if present, occurs an even number of times.

Let Q(n) be the count of all simbers with at most n digits.

We are given:
Q(7) = 287975
Q(100) mod 1_000_000_123 = 123864868

Find (sum_{1 <= u <= 39} Q(2^u)) mod 1_000_000_123.
"""

MOD = 1_000_000_123


def egcd(a: int, b: int):
    while b:
        (
            a,
            b,
        ) = (
            b,
            a % b,
        )
    # This iterative form doesn't give coefficients; use recursive for inverse.
    # (Kept only as a placeholder; inverse uses recursive egcd2 below.)
    return a


def egcd2(a: int, b: int):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = egcd2(b, a % b)
    return g, y1, x1 - (a // b) * y1


def inv_mod(a: int, mod: int = MOD) -> int:
    a %= mod
    g, x, _ = egcd2(a, mod)
    if g != 1:
        raise ValueError("inverse does not exist")
    return x % mod


INV2 = inv_mod(2)


def poly_mul(p: dict, q: dict) -> dict:
    """Multiply Laurent polynomials in e^x: sum c[t] * E^t, keyed by integer exponent t."""
    r = {}
    for e1, c1 in p.items():
        for e2, c2 in q.items():
            e = e1 + e2
            r[e] = (r.get(e, 0) + c1 * c2) % MOD
    return r


def poly_pow(p: dict, n: int) -> dict:
    r = {0: 1}
    base = p
    while n:
        if n & 1:
            r = poly_mul(r, base)
        base = poly_mul(base, base)
        n >>= 1
    return r


# Factors expressed as Laurent polynomials in E = e^x.
# cosh(x) = (E + E^{-1})/2
# sinh(x) = (E - E^{-1})/2
# 1 + sinh(x) = 1 + (E - E^{-1})/2
COSH = {1: INV2, -1: INV2}
SINH = {1: INV2, -1: (-INV2) % MOD}
ONE_PLUS_SINH = {0: 1, 1: INV2, -1: (-INV2) % MOD}

# Unrestricted-leading strings:
# F(x) = cosh(x)^5 * (1+sinh(x))^5
F = poly_mul(poly_pow(COSH, 5), poly_pow(ONE_PLUS_SINH, 5))

# Strings after fixing the first digit to 0 (to subtract off leading-zero cases):
# Remaining length m = k-1; digit 0 must appear an odd number of times in the remainder:
# G(x) = sinh(x) * cosh(x)^4 * (1+sinh(x))^5
G = poly_mul(poly_mul(SINH, poly_pow(COSH, 4)), poly_pow(ONE_PLUS_SINH, 5))

# Precompute inverses of (t-1) for t in [-10..10], excluding t=1
INV_T_MINUS_1 = {}
for t in range(-10, 11):
    tm = t % MOD
    if tm != 1:
        INV_T_MINUS_1[tm] = inv_mod((tm - 1) % MOD)


def geom_sum_start1(t: int, n: int) -> int:
    """Sum_{k=1..n} t^k mod MOD."""
    if n <= 0:
        return 0
    tm = t % MOD
    if tm == 1:
        return n % MOD
    if tm == 0:
        return 0
    num = (pow(tm, n + 1, MOD) - tm) % MOD
    return num * INV_T_MINUS_1[tm] % MOD


def geom_sum_start0(t: int, n: int) -> int:
    """Sum_{k=0..n-1} t^k mod MOD."""
    if n <= 0:
        return 0
    tm = t % MOD
    if tm == 1:
        return n % MOD
    num = (pow(tm, n, MOD) - 1) % MOD
    return num * INV_T_MINUS_1[tm] % MOD


def Q(n: int) -> int:
    """
    Q(n) = count of simbers with at most n digits, mod MOD.
    Uses exponential generating functions and the identity:
      m! [x^m] e^{t x} = t^m.
    """
    n = int(n)
    sum_A = 0  # sum_{k=1..n} A_k
    sum_C = 0  # sum_{m=0..n-1} C_m

    for t, coef in F.items():
        sum_A = (sum_A + coef * geom_sum_start1(t, n)) % MOD

    for t, coef in G.items():
        sum_C = (sum_C + coef * geom_sum_start0(t, n)) % MOD

    return (sum_A - sum_C) % MOD


def solve() -> int:
    # Test values from the problem statement
    assert Q(7) == 287975
    assert Q(100) == 123864868

    total = 0
    for u in range(1, 40):
        total = (total + Q(1 << u)) % MOD
    return total


if __name__ == "__main__":
    print(solve())
