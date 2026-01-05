#!/usr/bin/env python3
"""
Project Euler 486: Palindrome-containing Strings

We count binary strings of length <= n that contain a palindromic substring of length >= 5.
Let F5(n) be that count. We want D(10^18), where D(L) counts n in [5, L] with F5(n) divisible by 87654321.

No external libraries are used.
"""

from __future__ import annotations


MOD = 87654321  # 9 * 1997 * 4877

# Palindrome-free (no palindrome substring of length 5 or 6) counts are eventually periodic.
# Let A(n) be the number of palindrome-free strings of exact length n.
# Computed via a DFA on the last 5 bits (and verifiable by brute force for small n):
#   A(0..6) = 1,2,4,8,16,24,30
#   For n >= 7, A(n) repeats with period 6: [32,32,32,34,36,34]
#
# Let B(n) = sum_{k=0..n} A(k) be the number of palindrome-free strings of length <= n.
# Then:
#   F5(n) = (2^(n+1) - 1) - B(n)

B_SMALL = [1, 3, 7, 15, 31, 55, 85]  # B(0)..B(6)
B6 = 85
PERIOD = 6
PERIOD_SUM = 200
# prefix[r] = sum_{i=0..r-1} A_PERIOD[i], for r = 0..5, with prefix[0]=0
PREFIX = (0, 32, 64, 96, 130, 166)


def modinv(a: int, m: int) -> int:
    """Modular inverse of a modulo m (m may be composite). Requires gcd(a,m)=1."""
    t0, t1 = 0, 1
    r0, r1 = m, a % m
    while r1:
        q = r0 // r1
        r0, r1 = r1, r0 - q * r1
        t0, t1 = t1, t0 - q * t1
    if r0 != 1:
        raise ValueError("inverse does not exist")
    return t0 % m


def pal_free_cumulative(n: int) -> int:
    """B(n): number of palindrome-free binary strings of length <= n."""
    if n <= 6:
        return B_SMALL[n]
    q, r = divmod(n - 6, PERIOD)  # n = 6q + r + 6
    return B6 + q * PERIOD_SUM + PREFIX[r]


def F5(n: int) -> int:
    """Exact F5(n) for small n (used for asserts)."""
    total = (1 << (n + 1)) - 1  # sum_{k=0..n} 2^k (includes empty string)
    return total - pal_free_cumulative(n)


def _prepare_thresholds(L: int, o64: int, period_q: int) -> tuple[int, list[int]]:
    """
    For fixed L, count solutions among q in [0, q_max] for each residue r in 0..5:
        n = 6q + r + 6 <= L  => q_max = floor((L - r - 6)/6)

    Solutions are periodic in q with modulus period_q = MOD * o64 (gcd(MOD, o64)=1).

    If N = q_max + 1, write:
        N = Q*period_q + R, 0 <= R < period_q
    Then the number of q in [0, q_max] in the solution set for that r is:
        Q*o64 + #{solution residues < R}.

    Returns:
      base = sum_r Q_r * o64
      Rlist = [R_r for r=0..5]
    """
    if L < 6:
        return 0, [0] * 6

    base = 0
    Rlist = [0] * 6
    for r in range(6):
        qmax = (L - r - 6) // 6
        if qmax < 0:
            Rlist[r] = 0
            continue
        N = qmax + 1
        Q = N // period_q
        base += Q * o64
        Rlist[r] = N - Q * period_q  # N % period_q
    return base, Rlist


def solve_three(L1: int, L2: int, L3: int) -> tuple[int, int, int]:
    """
    Compute D(L1), D(L2), D(L3) in a single pass over k = 0..ord_MOD(64)-1.
    This keeps the sample asserts essentially free.
    """
    m = MOD

    # Order of 64 modulo MOD:
    # ord_9(64)=1, ord_1997(64)=998, ord_4877(64)=2438, so:
    o64 = 1216562
    period_q = m * o64  # gcd(m, o64) = 1

    inv200 = modinv(200, m)
    inv_o = modinv(o64, m)  # inverse of o64 modulo m

    # For n = 6q + r + 6:
    #   2^(n+1) = 2^(6q + r + 7) = 2^(r+7) * 64^q (mod m)
    pow2 = [pow(2, r + 7, m) for r in range(6)]
    # RHS: 1 + B(n) = 1 + B6 + PREFIX[r] + 200*q (mod m)
    C = [(1 + B6 + PREFIX[r]) % m for r in range(6)]

    base1, R1 = _prepare_thresholds(L1, o64, period_q)
    base2, R2 = _prepare_thresholds(L2, o64, period_q)
    base3, R3 = _prepare_thresholds(L3, o64, period_q)

    extra1 = 0
    extra2 = 0
    extra3 = 0

    # Iterate k = q mod o64. Maintain pow64 = 64^k mod m.
    pow64 = 1
    for k in range(o64):
        for r in range(6):
            # Solve mod m:
            #   pow2[r]*pow64 ≡ C[r] + 200*q
            # => q ≡ (pow2[r]*pow64 - C[r]) * inv200 (mod m)
            Lval = (pow2[r] * pow64) % m
            q0 = ((Lval - C[r]) * inv200) % m

            # Combine with q ≡ k (mod o64) using CRT (gcd(o64,m)=1):
            #   q = k + o64*t,  t ≡ (q0 - k) * inv_o (mod m)
            diff = q0 - k  # k < m, so no need for % m
            if diff < 0:
                diff += m
            t = (diff * inv_o) % m
            q_res = k + o64 * t  # 0 <= q_res < m*o64

            if q_res < R1[r]:
                extra1 += 1
            if q_res < R2[r]:
                extra2 += 1
            if q_res < R3[r]:
                extra3 += 1

        pow64 = (pow64 * 64) % m

    # n=5 is the only n in [5, ...] not covered by n=6q+r+6 with q>=0.
    add5_1 = 1 if L1 >= 5 and (F5(5) % m == 0) else 0
    add5_2 = 1 if L2 >= 5 and (F5(5) % m == 0) else 0
    add5_3 = 1 if L3 >= 5 and (F5(5) % m == 0) else 0

    return (add5_1 + base1 + extra1, add5_2 + base2 + extra2, add5_3 + base3 + extra3)


def main() -> None:
    # Sample values from the statement
    assert F5(4) == 0
    assert F5(5) == 8
    assert F5(6) == 42
    assert F5(11) == 3844

    d_1e7, d_5e9, d_1e18 = solve_three(10**7, 5 * 10**9, 10**18)

    assert d_1e7 == 0
    assert d_5e9 == 51

    print(d_1e18)


if __name__ == "__main__":
    main()
