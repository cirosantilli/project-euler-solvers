#!/usr/bin/env python3
"""
Project Euler 388 - Distinct Lines

Count distinct lines from the origin to lattice points (a,b,c) with 0<=a,b,c<=N.
A line is uniquely determined by the primitive direction vector (a,b,c)/gcd(a,b,c).

We compute:
D(N) = sum_{d=1..N} mu(d) * ( (floor(N/d)+1)^3 - 1 )
     = sum_{d=1..N} mu(d) * ( q^3 + 3q^2 + 3q ),  q=floor(N/d)

To handle N=1e10 efficiently we:
- Precompute mu(d) and its prefix sum M(d)=sum_{i<=d} mu(i) up to B=floor((N^2)^(1/3)).
- Use a memoized (Du Jiao) recursion to get M(n) for n>B.
- Split the Dirichlet sum at d=B, so the remaining quotients q are small (~N^(1/3)).
"""

from array import array
import sys


def icbrt(n: int) -> int:
    """Return floor(cuberoot(n)) for n>=0 (integer cube root)."""
    if n < 0:
        raise ValueError("icbrt expects n>=0")
    if n < 2:
        return n
    # Newton iteration with a bit-length based starting point.
    x = 1 << ((n.bit_length() + 2) // 3)
    while True:
        y = (2 * x + n // (x * x)) // 3
        if y >= x:
            # Fix possible off-by-one due to integer rounding.
            while (x + 1) ** 3 <= n:
                x += 1
            while x**3 > n:
                x -= 1
            return x
        x = y


def mobius_prefix_linear(n: int):
    """
    Linear sieve for Möbius mu(1..n) and prefix sums M(k)=sum_{i<=k} mu(i).
    Returns (mu, M) where:
      - mu is array('b') of length n+1
      - M is a Python list of ints of length n+1 (M[0]=0)
    """
    mu = array("b", [0]) * (n + 1)
    mu[1] = 1
    lp = array("I", [0]) * (n + 1)  # lowest prime factor
    primes = []  # Python list is fast for iteration

    for i in range(2, n + 1):
        if lp[i] == 0:
            lp[i] = i
            primes.append(i)
            mu[i] = -1
        for p in primes:
            ip = i * p
            if ip > n:
                break
            lp[ip] = p
            if i % p == 0:
                mu[ip] = 0
                break
            mu[ip] = -mu[i]

    M = [0] * (n + 1)
    s = 0
    for i in range(1, n + 1):
        s += mu[i]
        M[i] = s
    return mu, M


def G(q: int) -> int:
    """(q+1)^3 - 1 = q^3 + 3q^2 + 3q, written to avoid pow()."""
    return q * (q * (q + 3) + 3)


def build_solver(N: int):
    """
    Precompute data for a maximum N and return a function D(n) for n<=N.
    """
    B = icbrt(N * N)  # ~ N^(2/3)
    mu, M_small = mobius_prefix_linear(B)

    memo = {}

    def mertens(n: int) -> int:
        """Summatory Möbius M(n)=sum_{k<=n} mu(k) for all n (memoized Du Jiao sieve)."""
        if n <= B:
            return M_small[n]
        v = memo.get(n)
        if v is not None:
            return v
        res = 1
        l = 2
        while l <= n:
            q = n // l
            r = n // q
            res -= (r - l + 1) * mertens(q)
            l = r + 1
        memo[n] = res
        return res

    # Warm the cache: this makes later lookups for n//k values fast.
    mertens(N)

    def D(n: int) -> int:
        """
        Number of distinct lines for 0<=a,b,c<=n.
        """
        if n <= B:
            total = 0
            l = 1
            while l <= n:
                q = n // l
                r = n // q
                total += (M_small[r] - M_small[l - 1]) * G(q)
                l = r + 1
            return total

        # Part 1: d <= B (use prefix sums of mu)
        total = 0
        l = 1
        while l <= B:
            q = n // l
            r = n // q
            if r > B:
                r = B
            total += (M_small[r] - M_small[l - 1]) * G(q)
            l = r + 1

        # Part 2: d > B  ->  q = floor(n/d) is small (<= n//(B+1) ~= n^(1/3))
        max_q = n // (B + 1)
        for q in range(1, max_q + 1):
            left = n // (q + 1) + 1
            right = n // q
            if left <= B:
                left = B + 1
            if left > right:
                continue
            total += (mertens(right) - mertens(left - 1)) * G(q)

        return total

    return D


def main() -> None:
    N = 10_000_000_000
    if len(sys.argv) > 1:
        N = int(sys.argv[1])

    D = build_solver(N)

    # Test value from the problem statement
    assert D(1_000_000) == 831909254469114121

    value = D(N)
    s = str(value)
    print(s[:9] + s[-9:])


if __name__ == "__main__":
    main()
