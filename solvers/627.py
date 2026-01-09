#!/usr/bin/env python3
"""
Project Euler 627 - Counting products

We need F(30, 10001) mod 1_000_000_007, where
S = {x1 * x2 * ... * xn | 1 <= xi <= m} and F(m,n) = |S|.
"""

MOD = 1_000_000_007


def distinct_products_count(m: int, n: int) -> int:
    """Exact F(m,n) by explicit enumeration. Only intended for small n."""
    if n < 0:
        raise ValueError("n must be non-negative")
    prods = {1}
    nums = list(range(1, m + 1))
    for _ in range(n):
        new = set()
        for p in prods:
            for x in nums:
                new.add(p * x)
        prods = new
    return len(prods)


def modinv(a: int) -> int:
    return pow(a % MOD, MOD - 2, MOD)


def rising_mod(a: int, k: int) -> int:
    """(a)^(k↑) = a*(a+1)*...*(a+k-1) modulo MOD."""
    res = 1
    a %= MOD
    for i in range(k):
        res = (res * (a + i)) % MOD
    return res


def eval_cubic_from_values_0_3(f0: int, f1: int, f2: int, f3: int, n: int) -> int:
    """
    Evaluate the unique degree<=3 polynomial f with f(0..3) given,
    at integer n, using forward differences:

      f(n) = f0 + Δ f0 * C(n,1) + Δ^2 f0 * C(n,2) + Δ^3 f0 * C(n,3)
    """
    f0 %= MOD
    f1 %= MOD
    f2 %= MOD
    f3 %= MOD

    d1 = (f1 - f0) % MOD
    d2 = (f2 - 2 * f1 + f0) % MOD
    d3 = (f3 - 3 * f2 + 3 * f1 - f0) % MOD

    n %= MOD
    c1 = n
    c2 = n * (n - 1) % MOD * modinv(2) % MOD
    c3 = n * (n - 1) % MOD * (n - 2) % MOD * modinv(6) % MOD

    return (f0 + d1 * c1 + d2 * c2 + d3 * c3) % MOD


def solve() -> int:
    # --- Asserts from the problem statement ---
    assert distinct_products_count(9, 2) == 36
    assert distinct_products_count(30, 2) == 308

    # Compute F(30,n) exactly for small n (cheap).
    # We'll use n=0..5 to (a) fit the reduced polynomial and (b) verify it.
    max_n = 5
    nums = list(range(1, 31))
    prods = {1}
    F30 = [1]
    for _ in range(max_n):
        new = set()
        for p in prods:
            for x in nums:
                new.add(p * x)
        prods = new
        F30.append(len(prods))

    # Ehrhart-reciprocity-based factor: (n+1)(n+2)...(n+7)
    # So F(30,n) = rising(n+1, 7) * C(n), where C is a cubic polynomial.
    cvals = []
    for k in range(4):  # C(0..3)
        denom = rising_mod(k + 1, 7)
        cvals.append(F30[k] * modinv(denom) % MOD)

    def F30_poly(n: int) -> int:
        c_at_n = eval_cubic_from_values_0_3(cvals[0], cvals[1], cvals[2], cvals[3], n)
        return rising_mod(n + 1, 7) * c_at_n % MOD

    # Verify the polynomial matches additional brute-force points.
    assert F30_poly(4) == F30[4] % MOD
    assert F30_poly(5) == F30[5] % MOD

    # Required output
    return F30_poly(10001)


if __name__ == "__main__":
    print(solve() % MOD)
