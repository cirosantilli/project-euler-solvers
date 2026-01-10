#!/usr/bin/env python3
"""
Project Euler 483 - Repeated Permutation

We use the cycle-type formula. If a permutation on n elements has a_i cycles of length i,
then the number of such permutations is:

    n! / ∏_i (a_i! * i^{a_i})

and its order is lcm({ i : a_i > 0 }).

After dividing by n!, the required expectation becomes:

    g(n) =  Σ_{ Σ i*a_i = n }  lcm({i : a_i>0})^2  /  ∏_i (a_i! * i^{a_i})

We compute this sum with dynamic programming over cycle lengths, processing lengths
from n down to 1. To keep the LCM-state small, we "extract" prime-power contributions
as soon as they can no longer be affected by remaining (smaller) cycle lengths.
"""

from __future__ import annotations

from math import gcd


def _lcm(a: int, b: int) -> int:
    return a // gcd(a, b) * b


def _sieve_primes(n: int) -> list[int]:
    if n < 2:
        return []
    is_prime = bytearray(b"\x01") * (n + 1)
    is_prime[0:2] = b"\x00\x00"
    p = 2
    while p * p <= n:
        if is_prime[p]:
            step = p
            start = p * p
            for x in range(start, n + 1, step):
                is_prime[x] = 0
        p += 1
    return [i for i in range(2, n + 1) if is_prime[i]]


def format_sci_10(x: float) -> str:
    """
    Format with 10 significant digits, as in the problem statement.
    Example: 5.166666667e0 (no '+' sign, no leading zeros in exponent).
    """
    s = f"{x:.9e}"  # 10 significant digits total (1 before '.' + 9 after)
    mant, exp = s.split("e")
    return f"{mant}e{int(exp)}"


def g(n: int) -> float:
    """
    Compute g(n) as defined in Project Euler 483.

    DP state:
        dp[used][L] = accumulated contribution where
          - used is the total number of elements consumed by chosen cycles so far
          - L is a "tracked" LCM component that only keeps prime-power information
            that can still be influenced by future (smaller) cycle lengths.

    We iterate cycle lengths i from n down to 1, and choose how many i-cycles to use.
    For multiplicity a >= 1, the weight factor is 1 / (a! * i^a).

    Prime-power extraction trick:
        When we move from length i to i-1, any prime power p^k = i can no longer appear
        in future cycles. If the tracked LCM currently has exponent >= k (i.e. divisible
        by p^k), we can "lock in" one factor p into the final LCM^2 by multiplying the
        contribution by p^2 and dividing the tracked LCM by p (reducing the exponent by 1).
        This preserves correct interactions with remaining smaller powers of p.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return 1.0

    # For each i, extract[i] contains the prime p such that i == p^k for some k>=1.
    # (For i>=2, this list has length 1 exactly when i is a prime power, else 0.)
    extract: list[list[int]] = [[] for _ in range(n + 1)]
    for p in _sieve_primes(n):
        pk = p
        while pk <= n:
            extract[pk].append(p)
            pk *= p

    # dp[used] is a dict {tracked_lcm: value}
    dp: list[dict[int, float]] = [dict() for _ in range(n + 1)]
    dp[0][1] = 1.0

    for i in range(n, 0, -1):
        ii = i
        inv_i = 1.0 / ii
        new: list[dict[int, float]] = [dict() for _ in range(n + 1)]

        for used in range(n + 1):
            d = dp[used]
            if not d:
                continue
            max_a = (n - used) // ii
            for L0, v0 in d.items():
                # a = 0 (use no i-cycles)
                nd0 = new[used]
                try:
                    nd0[L0] += v0
                except KeyError:
                    nd0[L0] = v0

                if max_a == 0:
                    continue

                # a >= 1 (use i-cycles); LCM changes once if we use at least one i-cycle.
                L1 = _lcm(L0, ii)

                # t holds v0 / (a! * i^a) for current a; update iteratively for speed.
                t = v0 * inv_i  # a = 1
                used1 = used + ii
                nd = new[used1]
                try:
                    nd[L1] += t
                except KeyError:
                    nd[L1] = t

                for a in range(2, max_a + 1):
                    t /= a * ii  # now t = v0 / (a! * i^a)
                    used1 += ii
                    nd = new[used1]
                    try:
                        nd[L1] += t
                    except KeyError:
                        nd[L1] = t

        # Extract prime-power information that became "too large" when stepping below i.
        if extract[i]:
            comp: list[dict[int, float]] = [dict() for _ in range(n + 1)]
            div_check = i  # i == p^k
            for used in range(n + 1):
                d = new[used]
                if not d:
                    continue
                cd = comp[used]
                for L, v in d.items():
                    l = L
                    val = v
                    for p in extract[i]:
                        if l % div_check == 0:
                            l //= p
                            val *= float(p * p)
                    try:
                        cd[l] += val
                    except KeyError:
                        cd[l] = val
            new = comp

        dp = new

    return dp[n].get(1, 0.0)


def main() -> None:
    # Test values from the problem statement (10 significant digits).
    assert format_sci_10(g(3)) == "5.166666667e0"
    assert format_sci_10(g(5)) == "1.734166667e1"
    assert format_sci_10(g(20)) == "5.106136147e3"

    print(format_sci_10(g(350)))


if __name__ == "__main__":
    main()
