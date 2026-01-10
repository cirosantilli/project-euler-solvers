#!/usr/bin/env python3
"""
Project Euler 638 - Weighted Lattice Paths

We must compute:
    sum_{k=1..7} C(10^k+k, 10^k+k, k)  (mod 1_000_000_007)

For a path from (0,0) to (a,b) with steps Right/Up, the area under the path equals:
    sum over each Right step of the current y-coordinate
which is exactly the number of (Up before Right) pairs in the step word (an inversion statistic).

Therefore:
    C(a,b,k) = sum_{paths} k^{area} = Gaussian (q-)binomial coefficient
    C(a,b,k) = [a+b choose a]_q evaluated at q=k.

For q>1 we use the product formula:
    [m choose n]_q = Π_{i=1..n} (1 - q^{m-n+i}) / (1 - q^{i}),
with n = min(n, m-n).

Since MOD = 1_000_000_007 is prime and for q in {2..7} we have q^t != 1 for all t <= 20_000_014,
all denominators are invertible and we can multiply all numerator factors and all denominator factors,
then take exactly one modular inverse.
"""

MOD = 1_000_000_007


def binom_mod(n: int, r: int, mod: int = MOD) -> int:
    """Compute nCr mod prime mod via multiplicative formula (good for the small n used here)."""
    if r < 0 or r > n:
        return 0
    r = min(r, n - r)
    if r == 0:
        return 1
    num = 1
    den = 1
    # num = Π (n-r+1 .. n), den = r!
    start = n - r
    for i in range(1, r + 1):
        num = (num * (start + i)) % mod
        den = (den * i) % mod
    return (num * pow(den, mod - 2, mod)) % mod


def gaussian_binom(m: int, n: int, q: int, mod: int = MOD) -> int:
    """Compute Gaussian binomial coefficient [m choose n]_q modulo mod."""
    if n < 0 or n > m:
        return 0
    if n == 0 or n == m:
        return 1

    q %= mod
    if q == 1:
        return binom_mod(m, n, mod)

    n = min(n, m - n)
    if n == 0:
        return 1

    b = m - n  # so m-n+i == b+i

    # Products of (1 - q^{b+i}) and (1 - q^i)
    num_prod = 1
    den_prod = 1

    qmod = q
    pow_den = qmod  # q^1
    pow_num = pow(qmod, b + 1, mod)  # q^{b+1}

    modp1 = (
        mod + 1
    )  # used to keep factors positive: (1 - x) mod mod == (mod+1-x) mod mod
    for _ in range(n):
        num_prod = (num_prod * (modp1 - pow_num)) % mod
        den_prod = (den_prod * (modp1 - pow_den)) % mod
        pow_den = (pow_den * qmod) % mod
        pow_num = (pow_num * qmod) % mod

    return (num_prod * pow(den_prod, mod - 2, mod)) % mod


def C(a: int, b: int, k: int, mod: int = MOD) -> int:
    """The weighted lattice path sum C(a,b,k) modulo mod."""
    # C(a,b,k) = [a+b choose a]_k (Gaussian binomial evaluated at q=k)
    return gaussian_binom(a + b, a, k, mod)


def solve() -> int:
    # Test values from the problem statement
    assert C(2, 2, 1) == 6
    assert C(2, 2, 2) == 35
    assert C(10, 10, 1) == 184_756
    assert C(15, 10, 3) == 880_419_838
    assert C(10_000, 10_000, 4) == 395_913_804

    ans = 0
    for k in range(1, 8):
        n = 10**k + k
        ans = (ans + C(n, n, k)) % MOD
    return ans


if __name__ == "__main__":
    print(solve())
