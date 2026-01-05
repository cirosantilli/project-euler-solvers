#!/usr/bin/env python3
"""
Project Euler 439

Let d(n) be the sum of divisors (sigma function).
S(N) = sum_{1<=i<=N} sum_{1<=j<=N} d(i*j)

We use the identity:
    S(N) = sum_{k=1..N} (k*mu(k)) * H(N//k)^2
where
    mu is Möbius,
    H(x) = sum_{t=1..x} t * (x//t) = sum_{n<=x} sigma(n)

We compute prefix IMU(n) = sum_{k<=n} k*mu(k) with a Dujiao-sieve style recursion:
    IMU(n) = 1 - sum_{blocks i..j} (sum_{k=i..j} k) * IMU(n//i)

All arithmetic for the final answer is modulo 1e9.
"""

import sys
import math

MOD = 10**9


def brute_S(N: int) -> int:
    """Brute force for small N (used only for the given test values)."""
    maxv = N * N
    sigma = [0] * (maxv + 1)
    for d in range(1, maxv + 1):
        for m in range(d, maxv + 1, d):
            sigma[m] += d
    s = 0
    for i in range(1, N + 1):
        base = i
        for j in range(1, N + 1):
            s += sigma[base * j]
    return s


def solve(N: int, mod: int = MOD) -> int:
    """
    Compute S(N) mod mod using:
        S(N) = sum_{k=1..N} (k*mu(k)) * H(N//k)^2
    with quotient grouping and Dujiao sieve for IMU(n)=sum_{k<=n} k*mu(k).
    """
    sys.setrecursionlimit(1_000_000)

    sqrtN = math.isqrt(N)

    # Sieve limit: cap to keep memory reasonable in Python.
    sieve_limit = int(N ** (2 / 3))
    sieve_limit = min(sieve_limit, 3_000_000)
    if sieve_limit < sqrtN:
        sieve_limit = sqrtN

    # Linear sieve for Möbius up to sieve_limit
    mu = [0] * (sieve_limit + 1)
    is_comp = bytearray(sieve_limit + 1)
    primes = []
    mu[1] = 1
    for i in range(2, sieve_limit + 1):
        if not is_comp[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            ip = i * p
            if ip > sieve_limit:
                break
            is_comp[ip] = 1
            if i % p == 0:
                mu[ip] = 0
                break
            mu[ip] = -mu[i]

    # prefix IMU for small values
    pre_imu = [0] * (sieve_limit + 1)
    acc = 0
    for i in range(1, sieve_limit + 1):
        acc = (acc + i * mu[i]) % mod
        pre_imu[i] = acc

    imu_cache = {0: 0}

    def imu(x: int) -> int:
        """IMU(x)=sum_{k<=x} k*mu(k) mod mod, via Dujiao sieve recursion."""
        if x <= sieve_limit:
            return pre_imu[x]
        got = imu_cache.get(x)
        if got is not None:
            return got
        res = 1 % mod
        i = 2
        while i <= x:
            v = x // i
            j = x // v
            cnt = j - i + 1
            sum_i = (i + j) * cnt // 2
            res = (res - (sum_i % mod) * imu(v)) % mod
            i = j + 1
        imu_cache[x] = res
        return res

    # Precompute H(x)=sum_{n<=x} sigma(n) for x<=sqrtN using divisor sieve.
    sigma = [0] * (sqrtN + 1)
    for d in range(1, sqrtN + 1):
        for m in range(d, sqrtN + 1, d):
            sigma[m] += d
    H_small = [0] * (sqrtN + 1)
    acc = 0
    for i in range(1, sqrtN + 1):
        acc = (acc + sigma[i]) % mod
        H_small[i] = acc

    def H(x: int) -> int:
        """H(x)=sum_{t=1..x} t*(x//t) mod mod."""
        if x <= sqrtN:
            return H_small[x]
        res = 0
        i = 1
        while i <= x:
            v = x // i
            j = x // v
            cnt = j - i + 1
            sum_i = (i + j) * cnt // 2
            res = (res + (v % mod) * (sum_i % mod)) % mod
            i = j + 1
        return res

    # Main grouped sum over k where q=N//k is constant.
    ans = 0
    k = 1
    prev_imu = 0  # IMU(k-1)
    while k <= N:
        q = N // k
        r = N // q
        cur_imu = imu(r)
        seg = (cur_imu - prev_imu) % mod
        prev_imu = cur_imu

        hq = H(q)
        ans = (ans + seg * (hq * hq % mod)) % mod

        k = r + 1

    return ans


def _run_tests():
    # Given examples from problem statement
    assert brute_S(3) == 59
    assert brute_S(1000) == 563576517282
    assert solve(100000, MOD) == 215766508


if __name__ == "__main__":
    _run_tests()
    print(solve(10**11, MOD))
