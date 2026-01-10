#!/usr/bin/env python3
"""
Project Euler 606 — Gozinta Chains II

A gozinta chain for n is a divisor chain {1, a, b, ..., n} with strict divisibility.
These chains are in bijection with ordered factorizations of n into factors > 1:
    n = r1 * r2 * ... * rk     (order matters, ri > 1)

Let g(n) be the number of such ordered factorizations (gozinta chains).

The problem asks for:
    S(N) = sum of all k <= N such that g(k) = 252
Given:
    S(10^6)  = 8462952
    S(10^12) = 623291998881978
Find last nine digits of S(10^36).

Key reduction (proved in README):
    g(n) = 252  <=>  n = p^3 * q^3  where p, q are distinct primes

So the qualifying numbers are exactly:
    k = (p*q)^3,  p < q prime
and constraint k <= N becomes:
    p*q <= floor(cuberoot(N)) =: M

Thus:
    S(N) = sum_{p<q, p*q<=M} (p*q)^3

For N = 10^36, M = 10^12, too large to enumerate semiprimes directly.

We compute the sum modulo 10^9 (last nine digits),
using a Lucy-style prime summatory sieve to obtain:
    P3(x) = sum_{prime <= x} prime^3  (mod 1e9)
for all needed x values of the form floor(M / i) and small x <= sqrt(M).

No external libraries used.
"""

# ----------------------------------------------------------------------
# Helpers: integer cube root, sieve
# ----------------------------------------------------------------------


def icbrt(n: int) -> int:
    """Floor integer cube root via binary search (works for huge ints)."""
    if n < 0:
        raise ValueError("icbrt expects nonnegative n")
    lo, hi = 0, 1
    while hi * hi * hi <= n:
        hi *= 2
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        m3 = mid * mid * mid
        if m3 <= n:
            lo = mid
        else:
            hi = mid
    return lo


def isqrt(n: int) -> int:
    """Integer floor sqrt (no math library)."""
    if n < 0:
        raise ValueError("isqrt expects nonnegative n")
    x = int(n**0.5)
    while (x + 1) * (x + 1) <= n:
        x += 1
    while x * x > n:
        x -= 1
    return x


def sieve_primes(limit: int):
    """Return list of primes <= limit using a bytearray sieve."""
    if limit < 2:
        return []
    bs = bytearray(b"\x01") * (limit + 1)
    bs[0:2] = b"\x00\x00"
    p = 2
    while p * p <= limit:
        if bs[p]:
            step = p
            start = p * p
            bs[start : limit + 1 : step] = b"\x00" * (((limit - start) // step) + 1)
        p += 1
    return [i for i in range(limit + 1) if bs[i]]


# ----------------------------------------------------------------------
# Brute for small N (used for asserts from statement)
# ----------------------------------------------------------------------


def brute_S(N: int) -> int:
    """
    Brute force for small N:
    k has 252 chains iff k=(p*q)^3, so enumerate prime pairs.
    """
    M = icbrt(N)
    primes = sieve_primes(M)
    total = 0
    for i, p in enumerate(primes):
        for q in primes[i + 1 :]:
            if p * q > M:
                break
            total += (p * q) ** 3
    return total


# ----------------------------------------------------------------------
# Lucy-style prime power summatory sieve for P3(x) = sum_{p<=x} p^3 (mod MOD)
#
# We build V = [n//i for i=1..r] + [V_last-1..1] (strictly decreasing)
# and S[v] = sum_{k=2..v} k^3 (mod MOD)
#
# Then sieve out composites with the recurrence:
#   S[v] -= p^3 * (S[v//p] - S[p-1])
# for each prime p and each v >= p^2.
#
# The final S[v] becomes sum of prime cubes <= v (mod MOD).
# ----------------------------------------------------------------------


def prime_cube_sums_lucy(n: int, primes, MOD: int):
    """
    Compute prime cube summatory values for all v in the Lucy key-set V(n),
    returning (V, S) where:
        V is the decreasing list of key values
        S[i] = sum_{prime<=V[i]} prime^3 (mod MOD)
    """
    r = isqrt(n)
    # Key values list V: decreasing
    V = [n // i for i in range(1, r + 1)]
    last = V[-1]
    # Avoid duplicating 'last' if last == r (it is for n=10^12)
    for v in range(last - 1, 0, -1):
        V.append(v)
    L = len(V)

    # Initialize S[v] = sum_{k=2..v} k^3 (mod MOD)
    # sum_{k=1..v} k^3 = (v(v+1)/2)^2
    S = [0] * L
    for i, v in enumerate(V):
        t = (v * (v + 1) // 2) % MOD
        S[i] = (t * t - 1) % MOD

    # Index for a small value x <= r:
    # in this V construction, x is at index (L - x)
    def idx_small(x: int) -> int:
        return L - x

    # For v = n//i in the first block, v is at index i-1.
    # So for big lookup of v = n//d (where d<=r), index is d-1.

    # Sieve
    for p in primes:
        p2 = p * p
        if p2 > n:
            break
        p3 = (p * p) % MOD
        p3 = (p3 * p) % MOD

        # sum of prime^3 <= (p-1) after previous sieving:
        if p == 2:
            sp = 0  # p-1=1, but primes <=1 none, and S[1] would be 0 anyway
        else:
            sp = S[idx_small(p - 1)]

        # ----- Update big block indices i=0..big_len-1 -----
        # Condition V[i] >= p^2 in big block is:
        #   n//(i+1) >= p^2  <=>  (i+1) <= n//p^2
        big_len = n // p2
        if big_len > r:
            big_len = r

        # Update in decreasing V order = increasing i
        for i in range(big_len):
            v = V[i]
            denom_u = (i + 1) * p
            if denom_u <= r:
                # u = n//denom_u is a big value, index denom_u-1
                Su = S[denom_u - 1]
            else:
                # u is small, compute u=v//p and map to small index
                u = v // p
                Su = S[idx_small(u)]
            diff = Su - sp
            diff %= MOD
            S[i] = (S[i] - p3 * diff) % MOD

        # ----- Update small tail values (which are explicit integers) -----
        # Tail begins at index r, with values last-1 down to 1.
        # We need to update all tail values v >= p^2, i.e. v in [p^2 .. r-1].
        small_len = r - p2
        if small_len > 0:
            start = r  # first tail index
            end = r + small_len  # exclusive
            # V[start] = r-1, V[end-1] = p^2
            for j in range(start, end):
                v = V[j]
                u = v // p
                Su = S[idx_small(u)]
                diff = Su - sp
                diff %= MOD
                S[j] = (S[j] - p3 * diff) % MOD

    return V, S


# ----------------------------------------------------------------------
# Final computation for N=10^36
# ----------------------------------------------------------------------


def S_big_last9(N: int) -> int:
    """
    Compute S(N) modulo 1e9 (last nine digits), for huge N (like 10^36).
    Uses the reduction g(k)=252 <=> k=p^3 q^3 with distinct primes.
    """
    MOD = 1_000_000_000
    M = icbrt(N)  # floor(N^(1/3))
    r = isqrt(M)  # primes p up to sqrt(M) are enough as the smaller factor

    primes = sieve_primes(r)

    # Lucy prime cube sums up to M (mod MOD), for key values list
    V, S = prime_cube_sums_lucy(M, primes, MOD)
    L = len(V)

    # Index helper for small x <= r
    def idx_small(x: int) -> int:
        return L - x

    total = 0
    for p in primes:
        # Need q > p and p*q <= M => p < sqrt(M) and M//p > p
        if M // p <= p:
            break
        # prime cube sum up to (M//p):
        # Since M//p = M//(p) is a big key value, it sits at index p-1 in first block.
        sum_up_to_qmax = S[p - 1]
        # prime cube sum up to p (includes p itself):
        sum_up_to_p = S[idx_small(p)]
        sum_q = (sum_up_to_qmax - sum_up_to_p) % MOD
        p3 = (p * p) % MOD
        p3 = (p3 * p) % MOD
        total = (total + p3 * sum_q) % MOD

    return total


def main():
    # Asserts from the problem statement:
    assert brute_S(10**6) == 8462952
    assert brute_S(10**12) == 623291998881978

    ans = S_big_last9(10**36)
    print(f"{ans:09d}")


if __name__ == "__main__":
    main()
