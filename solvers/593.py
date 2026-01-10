#!/usr/bin/env python3
"""
Project Euler 593: Fleeting Medians

Compute F(10^7, 10^5) for the sequence defined in the problem statement.

No external libraries are used.
"""

from __future__ import annotations

import math


MOD = 10007
PHI = MOD - 1  # since MOD is prime
MAX_S2 = 2 * (MOD - 1)  # max value of S2(k) is 10006 + 10006 = 20012
DOMAIN_SIZE = MAX_S2 + 1  # values are 0..20012 inclusive


def nth_prime_upper_bound(n: int) -> int:
    """Safe upper bound for the nth prime for n >= 6: n (ln n + ln ln n) + 10."""
    if n < 6:
        return 15
    x = float(n)
    return int(x * (math.log(x) + math.log(math.log(x))) + 10)


def sieve_primes_upto(limit: int) -> list[int]:
    """Simple sieve returning all primes <= limit (fast enough for sqrt bounds)."""
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    r = int(math.isqrt(limit))
    for p in range(2, r + 1):
        if sieve[p]:
            start = p * p
            step = p
            sieve[start : limit + 1 : step] = b"\x00" * (((limit - start) // step) + 1)
    return [i for i in range(2, limit + 1) if sieve[i]]


def _factorize(n: int) -> list[int]:
    """Return the distinct prime factors of n (n is small here)."""
    factors: list[int] = []
    x = n
    d = 2
    while d * d <= x:
        if x % d == 0:
            factors.append(d)
            while x % d == 0:
                x //= d
        d += 1
    if x > 1:
        factors.append(x)
    return factors


def build_log_exp_tables(mod: int) -> tuple[list[int], list[int]]:
    """
    Build discrete log / exponentiation tables for the multiplicative group mod 'mod'
    (where 'mod' is prime).

    For a primitive root g:
      exp[i] = g^i mod mod  (i = 0..mod-2)
      log[a] = i such that g^i ≡ a (mod mod), for a != 0
    Then for a != 0:
      a^e mod mod = exp[(log[a] * e) % (mod-1)]
    """
    phi = mod - 1
    factors = _factorize(phi)

    # Find a primitive root
    g = None
    for cand in range(2, mod):
        ok = True
        for q in factors:
            if pow(cand, phi // q, mod) == 1:
                ok = False
                break
        if ok:
            g = cand
            break
    if g is None:
        raise RuntimeError("Failed to find primitive root")

    exp_table = [0] * phi
    log_table = [-1] * mod
    x = 1
    for i in range(phi):
        exp_table[i] = x
        log_table[x] = i
        x = (x * g) % mod
    return log_table, exp_table


LOG_TABLE, EXP_TABLE = build_log_exp_tables(MOD)


def pow_mod_fast(a_mod: int, e_mod: int) -> int:
    """Compute (a_mod ** e_mod) % MOD quickly (a_mod already reduced)."""
    if a_mod == 0:
        return 0
    return EXP_TABLE[(LOG_TABLE[a_mod] * e_mod) % PHI]


def format_half(sum2: int) -> str:
    """Format an integer representing 2*x as '... .0' or '... .5'."""
    if sum2 & 1:
        return f"{sum2 // 2}.5"
    return f"{sum2 // 2}.0"


def generate_s2_prefix(n: int) -> list[int]:
    """
    Generate S2(1..n) as a Python list.
    Intended only for small n in the example asserts.
    """
    if n <= 0:
        return []
    lim = nth_prime_upper_bound(n)
    while True:
        # Sieve and take first n primes
        primes = sieve_primes_upto(lim)
        if len(primes) >= n:
            primes = primes[:n]
            break
        lim = int(lim * 1.25) + 100

    offsets = [0] * 1002  # store S(1..1001)
    out: list[int] = [0] * n

    e = 0  # k % PHI
    t = 1
    next_t = 10000
    for k, p in enumerate(primes, start=1):
        e += 1
        if e == PHI:
            e = 0
        if k == next_t:
            t += 1
            next_t += 10000
        pm = p % MOD
        s = pow_mod_fast(pm, e)
        if k <= 1001:
            offsets[k] = s
        out[k - 1] = s + offsets[t]
    return out


def median2_of_sorted(arr_sorted: list[int]) -> int:
    """Return 2 * median for a sorted list."""
    m = len(arr_sorted)
    if m & 1:
        return 2 * arr_sorted[m // 2]
    return arr_sorted[m // 2 - 1] + arr_sorted[m // 2]


def compute_F2(n: int, k: int) -> int:
    """
    Return 2*F(n,k) (an integer), using:
      - segmented sieve to enumerate first n primes
      - fast modular exponent via discrete log/exp tables
      - sliding median over small domain via counting + drifting pointer
    """
    if k <= 0 or n < k:
        return 0

    # Sliding window state
    counts = [0] * DOMAIN_SIZE
    window = [0] * k
    filled = 0
    pos = 0

    even = (k & 1) == 0
    r1 = (k // 2) if even else ((k + 1) // 2)

    m1 = 0  # current value of the r1-th order statistic
    below = 0  # number of elements < m1 in the current window
    sum2 = 0

    def init_m1() -> None:
        nonlocal m1, below
        cum = 0
        v = 0
        cts = counts
        while cum + cts[v] < r1:
            cum += cts[v]
            v += 1
        m1 = v
        below = cum

    def adjust_m1() -> None:
        nonlocal m1, below
        cts = counts
        # Ensure: below < r1 <= below + cts[m1]
        while below >= r1:
            m1 -= 1
            below -= cts[m1]
        while below + cts[m1] < r1:
            below += cts[m1]
            m1 += 1

    def median2() -> int:
        if not even:
            return m1 << 1
        cts = counts
        pos_in = r1 - below  # 1..cts[m1]
        if pos_in < cts[m1]:
            return m1 << 1
        m2 = m1 + 1
        while cts[m2] == 0:
            m2 += 1
        return m1 + m2

    # Precompute base primes up to sqrt(limit) for the segmented sieve.
    limit = nth_prime_upper_bound(n)
    root = int(math.isqrt(limit))
    base_primes = sieve_primes_upto(root)
    base_odds = [p for p in base_primes if p > 2]
    base_sq = [p * p for p in base_odds]

    # S2 needs S(1..1001) stored
    offsets = [0] * 1002

    # Helpers for exponent and t without division/mod in the hot loop
    e = 1  # idx % PHI, starts at 1 for idx=1
    t = 1
    next_t = 10000  # idx at which t increments
    idx = 1

    # Process prime 2 directly
    s = 2  # 2^1 mod MOD
    offsets[1] = s
    v = s + s  # S2(1) = S(1) + S(1)
    window[0] = v
    counts[v] += 1
    filled = 1

    # If k == 1, the window is already "full"
    if k == 1:
        init_m1()
        sum2 += median2()
        if n == 1:
            return sum2

    # Segmented sieve over odd numbers
    seg_odds = 1 << 20  # number of odd candidates per segment (~1MB)
    low = 3  # inclusive, odd
    while low <= limit:
        high = min(low + 2 * seg_odds, limit + 1)  # exclusive
        seg_len = (high - low) // 2
        seg = bytearray(b"\x01") * seg_len

        # Mark composites
        for p, sq in zip(base_odds, base_sq):
            if sq >= high:
                break
            start = sq
            if start < low:
                rem = low % p
                start = low if rem == 0 else low + (p - rem)
                if (start & 1) == 0:
                    start += p
            j = (start - low) // 2
            seg[j::p] = b"\x00" * (((seg_len - j - 1) // p) + 1)

        find = seg.find
        i = find(1)
        while i != -1:
            prime = low + 2 * i

            # Advance index and derived counters
            idx += 1
            e += 1
            if e == PHI:
                e = 0
            if idx == next_t:
                t += 1
                next_t += 10000

            pm = prime % MOD
            s = pow_mod_fast(pm, e)
            if idx <= 1001:
                offsets[idx] = s
            v = s + offsets[t]

            if filled < k:
                window[filled] = v
                counts[v] += 1
                filled += 1
                if filled == k:
                    init_m1()
                    sum2 += median2()
                if idx == n:
                    return sum2
            else:
                out = window[pos]
                if out != v:
                    counts[out] -= 1
                    if out < m1:
                        below -= 1
                    window[pos] = v
                    counts[v] += 1
                    if v < m1:
                        below += 1
                    adjust_m1()
                else:
                    window[pos] = v

                pos += 1
                if pos == k:
                    pos = 0

                sum2 += median2()
                if idx == n:
                    return sum2

            i = find(1, i + 1)

        low = high | 1

    raise RuntimeError("Prime bound too small (unexpected).")


def run_asserts() -> None:
    # Example medians
    s2_1000 = generate_s2_prefix(1000)
    assert median2_of_sorted(sorted(s2_1000[0:10])) == 4043  # 2021.5 * 2
    assert median2_of_sorted(sorted(s2_1000[99:1000])) == 9430  # 4715.0 * 2

    # Example F values
    assert compute_F2(100, 10) == 927257  # 463628.5 * 2
    assert compute_F2(10**5, 10**4) == 1350696415  # 675348207.5 * 2


def main() -> None:
    run_asserts()
    ans2 = compute_F2(10**7, 10**5)
    print(format_half(ans2))


if __name__ == "__main__":
    main()
