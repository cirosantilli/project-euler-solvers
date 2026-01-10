#!/usr/bin/env python3
"""
Project Euler 379: Least common multiple count

We want g(N) = number of pairs (x, y) with 1 <= x <= y and lcm(x, y) <= N.

Key identity:
For each n, the number of ordered pairs (a,b) with lcm(a,b)=n is tau(n^2).
Thus:
L(N) = sum_{n<=N} tau(n^2)  counts ordered pairs (a,b) with lcm<=N.
Then unordered with x<=y is:
g(N) = (L(N) + N) // 2  (diagonal pairs a=b contribute N).

So we need compute:
L(N) = sum_{n<=N} tau(n^2)

This is computed using a Min_25/Lucy sieve style:
1) Lucy: compute prime counting over "key values" floor(N/i).
2) Convert prime counts into prime-sums for f(p)=tau(p^2)=3.
3) Un-Lucy: expand prime sums into the full multiplicative summatory for tau(n^2).

No brute force over pairs.
"""

from bisect import bisect_left
from math import isqrt


def primes_upto(limit: int):
    """Fast odd-only sieve producing primes <= limit."""
    if limit < 2:
        return []
    size = limit // 2 + 1  # indices represent odd numbers 1..limit
    bs = bytearray(b"\x01") * size
    bs[0] = 0  # 1 is not prime
    r = isqrt(limit)
    for p in range(3, r + 1, 2):
        if bs[p // 2]:
            start = p * p
            start_idx = start // 2
            step = p
            count = (size - start_idx - 1) // step + 1
            bs[start_idx::step] = b"\x00" * count
    primes = [2]
    primes.extend(2 * i + 1 for i in range(1, size) if bs[i])
    return primes


def sum_tau_sq(n: int) -> int:
    """
    Returns L(n) = sum_{k<=n} tau(k^2).
    Uses Lucy (prime sums) + un-Lucy (multiplicative expansion).
    """
    m = isqrt(n)

    # Key values V are all distinct floor(n / i).
    V = []
    i = 1
    while i <= n:
        q = n // i
        V.append(q)
        i = n // q + 1
    V.reverse()
    L = len(V)

    # id2 maps (n//v) -> index for values v > m
    id2 = [-1] * (m + 1)
    for idx, v in enumerate(V):
        if v > m:
            id2[n // v] = idx

    # Lucy initialization for prime counting:
    # S[v] = v - 1  (counts integers >=2 up to v)
    S = [v - 1 for v in V]

    primes = primes_upto(m)

    # Lucy sieve: compute pi(v) for each key v
    for p in primes:
        p2 = p * p
        if p2 > n:
            break
        sp = S[p - 2]  # pi(p-1)
        start = bisect_left(V, p2)
        j = L - 1
        while j >= start:
            v = V[j]
            u = v // p
            Sj = S[u - 1] if u <= m else S[id2[n // u]]
            S[j] -= Sj - sp
            j -= 1

    # Convert pi(v) into prime sum for f(p)=tau(p^2)=3:
    # sum_{p<=v} f(p) = 3*pi(v)
    for j in range(L):
        S[j] *= 3

    # Un-Lucy: expand to full multiplicative summatory
    # f(p^e)=tau((p^e)^2)=2e+1
    for p in reversed(primes):
        p2 = p * p
        if p2 > n:
            continue
        sp = S[p - 1]  # sum_{q<=p prime} f(q)
        start = bisect_left(V, p2)
        j = L - 1
        while j >= start:
            v = V[j]
            u = v // p
            e = 1
            while u >= p:
                Sj = S[u - 1] if u <= m else S[id2[n // u]]
                # Add numbers with smallest prime factor exactly p, exponent e
                S[j] += (2 * e + 1) * (Sj - sp) + (2 * (e + 1) + 1)
                e += 1
                u //= p
            j -= 1

    # S[-1] is sum_{2<=k<=n} tau(k^2), so add tau(1^2)=1
    return S[-1] + 1


def g(n: int) -> int:
    """Compute required g(n) for x<=y and lcm(x,y)<=n."""
    L = sum_tau_sq(n)
    return (L + n) // 2


def main():
    # Test value from problem statement
    assert g(10**6) == 37429395

    # Target value (do not hardcode any known result)
    print(g(10**12))


if __name__ == "__main__":
    main()
