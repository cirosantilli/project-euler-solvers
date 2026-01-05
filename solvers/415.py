#!/usr/bin/env python3
# Project Euler 415: Titanic Sets
# Uses Mustonen's f(n,k) and Lj(n) second-difference formula + Du Jiao recursion
# Works modulo 10^8.

MOD = 100_000_000
MOD2 = 2 * MOD  # compute collinear-subset sum mod 2*MOD, then divide by 2 safely


def partial_sum(n: int, k: int) -> int:
    """Exact sum_{i=1..n} i^k for k in {0,1,2}."""
    if k == 0:
        return n
    if k == 1:
        return n * (n + 1) // 2
    if k == 2:
        return n * (n + 1) * (2 * n + 1) // 6
    raise ValueError("k must be 0,1,2")


class CoprimeSums:
    """
    Du Jiao-style recursion computing:
      F(n,a,b) = sum_{1<=i,j<=n, gcd(i,j)=1} i^a j^b   (mod mod)
    for a,b in {0,1}.
    """

    def __init__(self, mod: int):
        self.mod = mod
        self.cache = [[{} for _ in range(2)] for __ in range(2)]
        # base n=1
        for a in (0, 1):
            for b in (0, 1):
                self.cache[a][b][1] = 1 % mod

    def dfs(self, n: int, a: int, b: int) -> int:
        mod = self.mod
        ca = self.cache[a][b]
        if n in ca:
            return ca[n]

        # G(n) = (sum i^a)(sum j^b)
        S = (partial_sum(n, a) % mod) * (partial_sum(n, b) % mod) % mod

        i = 2
        last = partial_sum(1, a + b) % mod
        while i <= n:
            q = n // i
            j = n // q + 1  # first index after this quotient block
            coef = partial_sum(j - 1, a + b) % mod
            S = (S - ((coef - last) % mod) * self.dfs(q, a, b)) % mod
            last = coef
            i = j

        ca[n] = S
        return S


# Closed-form prefix sums mod m:
# S0(n)=sum_{k=0..n} 2^k
# S1(n)=sum_{k=0..n} k*2^k
# S2(n)=sum_{k=0..n} k^2*2^k
def pref_pow2(n: int, m: int) -> int:
    if n < 0:
        return 0
    return (pow(2, n + 1, m) - 1) % m


def pref_kpow2(n: int, m: int) -> int:
    if n < 0:
        return 0
    pow2 = pow(2, n + 1, m)
    return (2 + ((n - 1) % m) * pow2) % m


def pref_k2pow2(n: int, m: int) -> int:
    if n < 0:
        return 0
    pow2 = pow(2, n + 1, m)
    a = (n * n - 2 * n + 3) % m
    return (a * pow2 - 6) % m


def range_sum(pref_fn, a: int, b: int, m: int) -> int:
    return (pref_fn(b, m) - pref_fn(a - 1, m)) % m


def sum_squares(a: int, b: int) -> int:
    # sum_{k=a..b} k^2 = SS(b)-SS(a-1)
    def SS(n: int) -> int:
        return n * (n + 1) * (2 * n + 1) // 6

    return SS(b) - SS(a - 1)


def block_contribution(n: int, L: int, R: int, q: int, cps: CoprimeSums) -> int:
    """
    Adds sum_{k=L..R} f(n,k) * (2^(k-1) - 1)   mod MOD2,
    where q = floor((n-1)/k) is constant on [L,R].
    """
    mod = MOD2

    # Positive quadrant coprime sums:
    Cpos = cps.dfs(q, 0, 0)  # count
    SX = cps.dfs(q, 1, 0)  # sum of x over ordered coprime pairs
    SXY = cps.dfs(q, 1, 1)  # sum of x*y over ordered coprime pairs

    # Lift to full [-q..q]^2 primitive vectors, excluding (0,0), including axes:
    # C = 4*Cpos + 4 axes
    # Sabs = 8*SX + 4 axes contribution to |x|+|y|
    # P = 4*SXY (axes contribute 0)
    C = (4 * Cpos + 4) % mod
    Sabs = (8 * SX + 4) % mod
    P = (4 * SXY) % mod

    nmod = n % mod

    # f(n,k) = n^2*C - n*k*Sabs + k^2*P  (mod mod)
    A0 = (nmod * nmod) % mod * C % mod
    A1 = nmod * Sabs % mod
    A2 = P

    # exponent part uses 2^(k-1): shift t=k-1
    tL, tR = L - 1, R - 1
    sum2 = range_sum(pref_pow2, tL, tR, mod)
    sumt2 = range_sum(pref_kpow2, tL, tR, mod)
    sumt22 = range_sum(pref_k2pow2, tL, tR, mod)

    sum_2km1 = sum2
    sum_k_2km1 = (sumt2 + sum2) % mod  # (t+1)2^t
    sum_k2_2km1 = (sumt22 + 2 * sumt2 + sum2) % mod  # (t+1)^2 2^t

    length = R - L + 1
    sumk = (L + R) * length // 2
    sumk2 = sum_squares(L, R)

    Sexpo = (A0 * sum_2km1 - A1 * sum_k_2km1 + A2 * sum_k2_2km1) % mod
    Splain = (A0 * (length % mod) - A1 * (sumk % mod) + A2 * (sumk2 % mod)) % mod
    return (Sexpo - Splain) % mod


def collinear_subsets_ge3(N: int) -> int:
    """
    Returns (mod 1e8) the number of subsets of size >=3 that are collinear
    in the (N+1)x(N+1) grid.

    Uses:
      B = (1/2) * sum_{k=2..n-1} f(n,k) * (2^(k-1) - 1)
    where n=N+1, and f(n,k) is Mustonen's function.
    """
    n = N + 1
    cps = CoprimeSums(MOD2)

    total = 0
    k = 2
    kmax = n - 1
    while k <= kmax:
        q = (n - 1) // k
        r = (n - 1) // q  # largest k with same q
        if r > kmax:
            r = kmax
        total = (total + block_contribution(n, k, r, q, cps)) % MOD2
        k = r + 1

    # total should be even (we will divide by 2)
    if total & 1:
        raise AssertionError("Internal parity check failed; sum should be even.")
    return (total // 2) % MOD


def titanic_sets(N: int) -> int:
    """
    T(N) = total subsets - empty - singletons - (collinear subsets of size>=3), mod 1e8.
    Problem statement uses 0<=x,y<=N, so number of points is (N+1)^2.
    """
    n = N + 1
    P = n * n
    total_subsets = pow(2, P, MOD)
    bad = collinear_subsets_ge3(N)
    return (total_subsets - 1 - (P % MOD) - bad) % MOD


def main() -> None:
    # Asserts for all test cases given in the problem statement.
    assert titanic_sets(1) == 11
    assert titanic_sets(2) == 494
    assert titanic_sets(4) == 33_554_178
    assert titanic_sets(10) == 60_631_646
    assert titanic_sets(20) == 74_363_930

    N = 10**11
    print(titanic_sets(N))


if __name__ == "__main__":
    main()
