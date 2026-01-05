#!/usr/bin/env python3
"""
Project Euler 448 - Average Least Common Multiple

We use number-theoretic transformations to rewrite:

A(n) = average_{1<=i<=n} lcm(n,i)
S(N) = sum_{k<=N} A(k)

Key identities:

lcm(n,i) = n*i/gcd(n,i)

A(n) turns into a divisor-sum involving:
J(m) = sum_{1<=j<=m, gcd(j,m)=1} j

For m>1: J(m) = m*phi(m)/2, and J(1)=1

Then:
A(n) = sum_{d|n} J(d)
S(N) = sum_{n<=N} A(n)
     = sum_{d<=N} J(d) * floor(N/d)

We compute prefix sums of J via prefix sums of f(n)=n*phi(n),
using Du Jiao sieve on:
F(n) = sum_{k<=n} k*phi(k)

Then prefixJ(n) = sum_{k<=n} J(k) = (F(n) + 1)/2.

Finally:
S(N) = sum_{k=1..N} prefixJ(N//k)
grouped by constant quotient.
"""

from array import array


MOD = 999_999_017
N_TARGET = 99_999_999_019


def gcd(a: int, b: int) -> int:
    while b:
        a, b = b, a % b
    return a


def lcm(a: int, b: int) -> int:
    return a // gcd(a, b) * b


def A_bruteforce(n: int) -> int:
    s = 0
    for i in range(1, n + 1):
        s += lcm(n, i)
    return s // n


def S_bruteforce(n: int) -> int:
    return sum(A_bruteforce(k) for k in range(1, n + 1))


def build_prefix_F(limit: int) -> array:
    """
    Compute phi(1..limit) via linear sieve and build:
    prefF[x] = sum_{k<=x} k*phi(k) mod MOD
    """
    phi = array("I", [0]) * (limit + 1)
    is_comp = bytearray(limit + 1)
    primes = array("I")

    phi[1] = 1
    for i in range(2, limit + 1):
        if not is_comp[i]:
            primes.append(i)
            phi[i] = i - 1
        for p in primes:
            ip = i * p
            if ip > limit:
                break
            is_comp[ip] = 1
            if i % p == 0:
                phi[ip] = phi[i] * p
                break
            else:
                phi[ip] = phi[i] * (p - 1)

    prefF = array("I", [0]) * (limit + 1)
    s = 0
    for i in range(1, limit + 1):
        s = (s + (i * phi[i]) % MOD) % MOD
        prefF[i] = s
    return prefF


def solve(N: int) -> int:
    # modular inverses for divisions by 2 and 6
    inv2 = pow(2, MOD - 2, MOD)
    inv6 = pow(6, MOD - 2, MOD)

    # Heuristic limit: large enough to reduce recursion count,
    # small enough to fit memory.
    LIMIT = 20_000_000  # adjust upward/downward if needed

    prefF = build_prefix_F(LIMIT)
    memo = {}

    def sumF(n: int) -> int:
        """F(n) = sum_{k<=n} k*phi(k) mod MOD (Du Jiao sieve)."""
        if n <= LIMIT:
            return prefF[n]
        v = memo.get(n)
        if v is not None:
            return v

        # S2(n) = sum_{k<=n} k^2 = n(n+1)(2n+1)/6
        a = n % MOD
        res = (a * ((n + 1) % MOD) % MOD) * ((2 * n + 1) % MOD) % MOD
        res = (res * inv6) % MOD

        i = 2
        while i <= n:
            q = n // i
            j = n // q

            # sum_{k=i..j} k = (i+j)*(j-i+1)/2
            sum_ij = ((i + j) % MOD) * ((j - i + 1) % MOD) % MOD
            sum_ij = (sum_ij * inv2) % MOD

            fq = prefF[q] if q <= LIMIT else memo.get(q)
            if fq is None:
                fq = sumF(q)

            res = (res - sum_ij * fq) % MOD
            i = j + 1

        memo[n] = res
        return res

    def prefixJ(n: int) -> int:
        # prefixJ(n) = (F(n)+1)/2
        return ((sumF(n) + 1) % MOD) * inv2 % MOD

    # S(N) = sum_{k=1..N} prefixJ(N//k), grouped by quotient
    ans = 0
    k = 1
    while k <= N:
        q = N // k
        r = N // q
        cnt = (r - k + 1) % MOD
        ans = (ans + cnt * prefixJ(q)) % MOD
        k = r + 1

    return ans


def main() -> None:
    # Asserts from problem statement examples
    assert A_bruteforce(2) == 2
    assert A_bruteforce(10) == 32
    assert S_bruteforce(100) == 122726

    # Fast check on example mod (MOD is much larger than 122726)
    assert solve(100) == 122726

    print(solve(N_TARGET))


if __name__ == "__main__":
    main()
