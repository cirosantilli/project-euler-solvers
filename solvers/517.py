#!/usr/bin/env python3
"""
Project Euler 517 - A real recursion

We are given, for every real a > 1:
  g_a(x) = 1                          for x < a
  g_a(x) = g_a(x-1) + g_a(x-a)        for x >= a

Define:
  G(n) = g_{sqrt(n)}(n)

Given:
  G(90) = 7564511

Task:
  Sum G(p) for primes p with 10_000_000 < p < 10_010_000, modulo 1_000_000_007.

No external libraries are used.
"""

from __future__ import annotations

import math
from array import array

MOD = 1_000_000_007
LOW = 10_000_000
HIGH = 10_010_000  # exclusive


def precompute_factorials(n: int) -> tuple[array, array]:
    """
    Precompute factorials and inverse factorials mod MOD up to n inclusive.

    Uses array('I') to store 32-bit unsigned values (MOD fits in 32-bit).
    """
    fac = array("I", [0]) * (n + 1)
    invfac = array("I", [0]) * (n + 1)

    fac[0] = 1
    mod = MOD
    f = fac
    for i in range(1, n + 1):
        f[i] = (f[i - 1] * i) % mod

    invfac[n] = pow(fac[n], mod - 2, mod)
    inv = invfac
    for i in range(n, 0, -1):
        inv[i - 1] = (inv[i] * i) % mod

    return fac, invfac


def comb(n: int, k: int, fac: array, invfac: array) -> int:
    """Compute C(n, k) modulo MOD, assuming 0 <= n <= len(fac)-1."""
    if k < 0 or k > n:
        return 0
    mod = MOD
    return (fac[n] * invfac[k] % mod) * invfac[n - k] % mod


def primes_in_open_interval(lo: int, hi: int) -> list[int]:
    """
    Return primes p with lo < p < hi using a segmented sieve.
    """
    start = lo + 1
    end = hi  # exclusive

    limit = math.isqrt(end) + 1

    # simple sieve up to limit
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    r = math.isqrt(limit)
    for i in range(2, r + 1):
        if sieve[i]:
            step = i
            begin = i * i
            sieve[begin : limit + 1 : step] = b"\x00" * (((limit - begin) // step) + 1)
    base_primes = [i for i in range(2, limit + 1) if sieve[i]]

    # segmented sieve on [start, end)
    seg = bytearray(b"\x01") * (end - start)
    for p in base_primes:
        first = ((start + p - 1) // p) * p
        for x in range(first, end, p):
            seg[x - start] = 0

    primes = []
    for i, is_p in enumerate(seg):
        if is_p:
            val = start + i
            if val >= 2:
                primes.append(val)
    return primes


def G(n: int, fac: array, invfac: array) -> int:
    """
    Compute G(n) = g_{sqrt(n)}(n) mod MOD.

    Key combinatorial fact:
      g_{a}(n) counts the number of sequences of steps of size 1 and a
      whose partial sums first exceed n - a.

    Split by the LAST step (which causes the exceed):
      - last step is 1: for each i (# of 'a' steps before last), there is a unique
        c = floor(n - (i+1)*a) (# of 1-steps before last) and the number of such
        sequences is C(c+i, i).
      - last step is a: for each c (# of 'a' steps before last), the valid number
        of 1-steps k lies in an interval, and sum_{k} C(k+c, c) is computed via the
        hockey-stick identity.

    All floors are computed exactly using integer arithmetic:
      floor(m*sqrt(n)) = isqrt(m^2 * n).
    For prime n, sqrt(n) is irrational, so 'ceil' is 'floor+1' and no equality issues occur.
    """
    a_floor = math.isqrt(n)  # floor(sqrt(n)) since n is not a perfect square here
    isq = math.isqrt
    cmb = comb
    mod = MOD

    # u[m] = floor(n - m*sqrt(n)) for m >= 1
    # floor(n - m*a) = n - ceil(m*a) = n - (floor(m*a) + 1) because m*a is irrational
    # floor(m*a) = isqrt(m^2*n)
    u = [0] * (a_floor + 3)  # need up to m = a_floor + 1
    for m in range(1, a_floor + 2):
        u[m] = n - isq(m * m * n) - 1

    ans = 0

    # Case 1: last step is 1
    # i ranges 0 .. a_floor-1 (since i*a < n-a <=> i < sqrt(n)-1)
    for m in range(1, a_floor + 1):  # m = i+1
        c = u[m]  # floor(n - m*a)
        i = m - 1
        ans += cmb(c + i, i, fac, invfac)

    # Case 2: last step is a
    # for each c = #a-steps before last, k ranges [L, U] where:
    #   U = floor(n - (c+1)*a) = u[c+1]
    #   L = floor(n - (c+2)*a) + 1 = u[c+2] + 1
    for c in range(0, a_floor):
        upper = u[c + 1]
        if upper < 0:
            continue
        lower = u[c + 2] + 1
        if lower < 0:
            lower = 0
        if lower > upper:
            continue

        # sum_{k=lower}^{upper} C(k+c, c) =
        #   C(c+upper+1, c+1) - C(c+lower, c+1)
        ans += cmb(c + upper + 1, c + 1, fac, invfac)
        if lower > 0:
            ans -= cmb(c + lower, c + 1, fac, invfac)

    return ans % mod


def main() -> None:
    # The largest 'n' used in any binomial is < HIGH, so precompute up to HIGH.
    fac, invfac = precompute_factorials(HIGH)

    # Test from problem statement
    assert G(90, fac, invfac) == 7_564_511

    primes = primes_in_open_interval(LOW, HIGH)
    total = 0
    for p in primes:
        total += G(p, fac, invfac)
    total %= MOD
    print(total)


if __name__ == "__main__":
    main()
