#!/usr/bin/env python3
"""
Project Euler 521 - Smallest Prime Factor
Compute S(10^12) mod 10^9.

No external libraries are used.

Key components:
- Fast prime table up to 1e6 (pi table, prime list, prime prefix sums)
- Segmented sieve up to 1e8 (lazy) for very fast pi(x) when x <= 1e8
- Lehmer prime counting pi(x) for x up to 1e12
- Min_25 sieve (mod 1e9) for prime summatory function sum_{p<=n} p
- Counting smpf contributions by splitting primes into ranges where the cofactor can
  have 0/1/2/many prime factors.
"""

from __future__ import annotations

import math
from bisect import bisect_left, bisect_right
from functools import lru_cache
from array import array

MOD = 1_000_000_000
TARGET_N = 10**12


# ---------------------------
# Small primes up to 1e6
# ---------------------------


def sieve_pi_table(limit: int):
    """Return (primes_list, pi_table, prime_prefix_sum)."""
    bs = bytearray(b"\x01") * (limit + 1)
    bs[:2] = b"\x00\x00"
    r = int(limit**0.5)
    for i in range(2, r + 1):
        if bs[i]:
            step = i
            start = i * i
            bs[start : limit + 1 : step] = b"\x00" * (((limit - start) // step) + 1)

    primes = [i for i in range(limit + 1) if bs[i]]

    pi = array("I", [0]) * (limit + 1)
    c = 0
    for i in range(limit + 1):
        if bs[i]:
            c += 1
        pi[i] = c

    ps = array("Q", [0])  # ps[k] = sum of first k primes
    s = 0
    for p in primes:
        s += p
        ps.append(s)

    return primes, pi, ps


PRIMES_1E6, PI_1E6, PRIME_SUM_1E6 = sieve_pi_table(1_000_000)


# Helper: sum of primes <= n for n <= 1e6
def prime_sum_upto_1e6(n: int) -> int:
    if n < 2:
        return 0
    idx = bisect_right(PRIMES_1E6, n)
    return int(PRIME_SUM_1E6[idx]) % MOD


# ---------------------------
# Lazy primes up to 1e8 for fast pi(x) queries
# ---------------------------


def simple_sieve(limit: int):
    """Plain sieve, returns list of primes <= limit."""
    bs = bytearray(b"\x01") * (limit + 1)
    bs[:2] = b"\x00\x00"
    r = int(limit**0.5)
    for i in range(2, r + 1):
        if bs[i]:
            start = i * i
            bs[start : limit + 1 : i] = b"\x00" * (((limit - start) // i) + 1)
    return [i for i in range(limit + 1) if bs[i]]


def segmented_primes(limit: int, seg_size: int = 1 << 22) -> array:
    """
    Segmented sieve returning array('I') of primes <= limit.
    seg_size is in integers (not odds); 2^22 ~ 4.2 million.
    """
    if limit < 2:
        return array("I")

    root = int(math.isqrt(limit))
    base = simple_sieve(root)
    base_odds = [p for p in base if p != 2]

    primes = array("I", [2])

    low = 3
    while low <= limit:
        high = min(low + seg_size - 1, limit)
        if low % 2 == 0:
            low += 1
        if high % 2 == 0:
            high -= 1
        if low > high:
            low = high + 2
            continue

        size = ((high - low) // 2) + 1  # count of odds in [low, high]
        is_prime = bytearray(b"\x01") * size
        sqrt_high = int(math.isqrt(high))

        for p in base_odds:
            if p > sqrt_high:
                break
            start = ((low + p - 1) // p) * p
            pp = p * p
            if start < pp:
                start = pp
            if start % 2 == 0:
                start += p
            idx = (start - low) // 2
            if idx >= size:
                continue
            step = p  # because numbers advance by 2, marking step in indices is p
            cnt = ((size - idx - 1) // step) + 1
            is_prime[idx::step] = b"\x00" * cnt

        for i, flag in enumerate(is_prime):
            if flag:
                primes.append(low + 2 * i)

        low = high + 2

    return primes


_PRIMES_1E8: array | None = None


def primes_upto_1e8() -> array:
    """Generate and cache primes <= 1e8 (used for fast pi(x) when x <= 1e8)."""
    global _PRIMES_1E8
    if _PRIMES_1E8 is None:
        _PRIMES_1E8 = segmented_primes(100_000_000)
    return _PRIMES_1E8


def pi_upto_1e8(n: int) -> int:
    """pi(n) for n <= 1e8 using cached prime list."""
    if n < 2:
        return 0
    primes = primes_upto_1e8()
    return bisect_right(primes, n)


# ---------------------------
# Integer roots
# ---------------------------


def iroot3(n: int) -> int:
    x = int(round(n ** (1.0 / 3.0)))
    while (x + 1) ** 3 <= n:
        x += 1
    while x**3 > n:
        x -= 1
    return x


def iroot4(n: int) -> int:
    x = int(round(n**0.25))
    while (x + 1) ** 4 <= n:
        x += 1
    while x**4 > n:
        x -= 1
    return x


# ---------------------------
# Lehmer pi(n)
# ---------------------------

BASE_PRIMES = (2, 3, 5, 7, 11, 13)
P_BASE = 1
for _p in BASE_PRIMES:
    P_BASE *= _p


def _precompute_base_phi():
    ok = bytearray(b"\x01") * (P_BASE + 1)
    ok[0] = 0
    for p in BASE_PRIMES:
        for m in range(p, P_BASE + 1, p):
            ok[m] = 0
    cnt = array("I", [0]) * (P_BASE + 1)
    c = 0
    for i in range(1, P_BASE + 1):
        if ok[i]:
            c += 1
        cnt[i] = c
    return cnt


CNT_BASE = _precompute_base_phi()


@lru_cache(maxsize=None)
def phi_count(n: int, a: int) -> int:
    """
    Count integers 1..n not divisible by the first a primes.
    (We will use it in Lehmer pi and in counting rough numbers.)
    """
    if n <= 0:
        return 0
    if a == 0:
        return n
    if a == 6:
        q, r = divmod(n, P_BASE)
        return q * CNT_BASE[P_BASE] + CNT_BASE[r]
    return phi_count(n, a - 1) - phi_count(n // PRIMES_1E6[a - 1], a - 1)


_LEHMER_CACHE: dict[int, int] = {}


def lehmer_pi(n: int) -> int:
    """Prime counting function pi(n) for n up to 1e12 (fast)."""
    if n < 2:
        return 0
    if n <= 1_000_000:
        return int(PI_1E6[n])
    if n <= 100_000_000:
        return pi_upto_1e8(n)
    if n in _LEHMER_CACHE:
        return _LEHMER_CACHE[n]

    a = lehmer_pi(iroot4(n))
    b = lehmer_pi(int(math.isqrt(n)))
    c = lehmer_pi(iroot3(n))

    res = phi_count(n, a) + ((b + a - 2) * (b - a + 1)) // 2
    # i indexes primes starting from 0
    for i in range(a, b):
        p = PRIMES_1E6[i]
        w = n // p
        res -= lehmer_pi(w)
        if i < c:
            lim = lehmer_pi(int(math.isqrt(w)))
            for j in range(i, lim):
                res -= lehmer_pi(w // PRIMES_1E6[j]) - j

    _LEHMER_CACHE[n] = res
    return res


# ---------------------------
# Min_25 sieve: sum of primes <= n (mod MOD)
# ---------------------------


def prime_sum_mod(n: int) -> int:
    """
    Return sum_{p <= n} p (mod MOD) using a Min_25 sieve variant.
    Only arithmetic modulo MOD is carried, which is valid because the process is linear.
    """
    if n < 2:
        return 0
    if n <= 1_000_000:
        return prime_sum_upto_1e6(n)

    m = int(math.isqrt(n))

    # distinct values of floor(n / i)
    vals = array("Q")
    i = 1
    while i <= n:
        v = n // i
        vals.append(v)
        i = n // v + 1

    L = len(vals)
    id1 = array("I", [0]) * (m + 1)
    id2 = array("I", [0]) * (m + 1)
    g = array("I", [0]) * L

    MOD0 = MOD
    n0 = n
    m0 = m

    # initialize g(v) = sum_{k=2..v} k = v(v+1)/2 - 1  (mod MOD)
    for idx in range(L):
        v = vals[idx]
        if v <= m0:
            id1[v] = idx
        else:
            id2[n0 // v] = idx
        g[idx] = int(((v * (v + 1) // 2 - 1) % MOD0))

    sp = 0  # sum of processed primes (< p) mod MOD

    vals0 = vals
    id10 = id1
    id20 = id2
    g0 = g

    for p in PRIMES_1E6:
        if p > m0:
            break
        p2 = p * p
        if p2 > n0:
            break

        sp_before = sp
        # update all v >= p^2
        # vals are in decreasing order, so break when v < p^2
        for j in range(L):
            v = vals0[j]
            if v < p2:
                break
            vp = v // p
            if vp <= m0:
                idx_vp = id10[vp]
            else:
                idx_vp = id20[n0 // vp]

            diff = (g0[idx_vp] - sp_before) % MOD0
            g0[j] = (g0[j] - (p * diff) % MOD0) % MOD0

        sp = (sp_before + p) % MOD0

    return int(g0[0] % MOD0)


# ---------------------------
# Problem-specific computation S(n)
# ---------------------------


def smpf_single(x: int) -> int:
    """Smallest prime factor (for tiny test values only)."""
    if x % 2 == 0:
        return 2
    d = 3
    while d * d <= x:
        if x % d == 0:
            return d
        d += 2
    return x


def S(n: int) -> int:
    """
    Compute S(n) = sum_{i=2..n} smpf(i) (mod MOD).

    We split primes p into ranges based on n:
    - p <= n^(1/4): cofactor may have many factors -> use phi_count
    - n^(1/4) < p <= n^(1/3): cofactor has at most 2 prime factors
    - n^(1/3) < p <= sqrt(n): cofactor has at most 1 prime factor
    - p > sqrt(n): only primes contribute once each
    """
    if n < 2:
        return 0

    y1 = iroot4(n)  # floor(n^(1/4))
    y2 = iroot3(n)  # floor(n^(1/3))
    sqrt_n = int(math.isqrt(n))

    primes = PRIMES_1E6

    def pi(x: int) -> int:
        if x <= 100_000_000:
            return pi_upto_1e8(x)
        return lehmer_pi(x)

    ans = 0

    # 1) p <= min(y1, sqrt_n)
    upper1 = min(y1, sqrt_n)
    for idx, p in enumerate(primes):
        if p > upper1:
            break
        # idx = number of primes < p
        ans = (ans + p * phi_count(n // p, idx)) % MOD

    # 2) y1 < p <= min(y2, sqrt_n): cofactor has at most 2 prime factors
    if upper1 < min(y2, sqrt_n):
        start = bisect_right(primes, upper1)
        end = bisect_right(primes, min(y2, sqrt_n))
        for p in primes[start:end]:
            X = n // p
            pi_p_minus = int(PI_1E6[p - 1])  # p <= 1e6 here for our target

            # m = 1 and m = prime >= p
            cnt = 1 + pi(X) - pi_p_minus

            lim = int(math.isqrt(X))
            q_start = bisect_left(primes, p)
            q_end = bisect_right(primes, lim)
            for q in primes[q_start:q_end]:
                # Here X <= n/p and q >= p > n^(1/4) ensures X//q <= 1e6 for n=1e12
                cnt += int(PI_1E6[X // q]) - int(PI_1E6[q - 1])

            ans = (ans + p * (cnt % MOD)) % MOD

    # 3) y2 < p <= sqrt_n: cofactor has at most 1 prime factor
    if y2 < sqrt_n:
        start = bisect_right(primes, min(y2, sqrt_n))
        end = bisect_right(primes, sqrt_n)
        for p in primes[start:end]:
            X = n // p
            # p <= sqrt_n so p <= 1e6 for n=1e12
            cnt = 1 + pi(X) - int(PI_1E6[p - 1])
            ans = (ans + p * (cnt % MOD)) % MOD

    # 4) p > sqrt_n: only primes contribute once each
    # sum_{sqrt(n) < p <= n} p = prime_sum(n) - prime_sum(sqrt(n))
    # prime_sum_upto_1e6 is correct for sqrt_n <= 1e6 (true for n <= 1e12)
    ans = (
        ans
        + prime_sum_mod(n)
        - (prime_sum_upto_1e6(sqrt_n) if sqrt_n <= 1_000_000 else prime_sum_mod(sqrt_n))
    ) % MOD

    return ans


def main() -> None:
    # Asserts from the problem statement:
    assert smpf_single(91) == 7
    assert smpf_single(45) == 3
    assert S(100) == 1257

    print(S(TARGET_N))


if __name__ == "__main__":
    main()
