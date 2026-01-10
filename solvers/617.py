#!/usr/bin/env python3
"""Project Euler 617: Mirror Power Sequence

For integers n,e>1 define an (n,e)-MPS as an infinite integer sequence (a_i) with:
  a_{i+1} = min(a_i^e, n - a_i^e)  and  a_i > 1  for all i.

Let C(n) be the number of (n,e)-MPS over all e (equivalently, over all triples (n,e,a0)),
and D(N) = sum_{n=2..N} C(n).

This program computes D(10^18).
No external libraries are used.
"""

from __future__ import annotations


def _pow_capped(base: int, exp: int, cap: int) -> int:
    """Return min(base**exp, cap+1) using fast exponentiation with early stop."""
    result = 1
    a = base
    e = exp
    while e:
        if e & 1:
            result *= a
            if result > cap:
                return cap + 1
        e >>= 1
        if e:
            a *= a
            if a > cap:
                a = cap + 1
    return result


def int_nth_root(n: int, k: int) -> int:
    """Compute floor(n ** (1/k)) for integers n>=0, k>=1 (exact, via binary search)."""
    if k <= 1:
        return n
    if n < 2:
        return n

    lo, hi = 1, 1
    # Grow hi until hi^k > n.
    while _pow_capped(hi, k, n) <= n:
        hi <<= 1

    # Root is in [lo, hi)
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if _pow_capped(mid, k, n) <= n:
            lo = mid
        else:
            hi = mid
    return lo


def _max_t_for_b1(N: int, e: int) -> int:
    """Largest t such that t + t^e <= N. Returns 1 if no t>=2 works."""
    if N < 4:
        return 1

    # t^e <= N implies t <= floor_root(N, e)
    hi = int_nth_root(N, e) + 1
    lo = 1
    while lo + 1 < hi:
        mid = (lo + hi) // 2
        if mid + pow(mid, e) <= N:
            lo = mid
        else:
            hi = mid
    return lo


def count_for_exponent(N: int, e: int) -> int:
    """Count all (n,e,a0) with n<=N that yield an infinite sequence, for fixed e."""
    total = 0

    # b = 1: n = t + t^e.
    # We count primitive t (not exact e-th powers) without enumerating all t.
    t_max = _max_t_for_b1(N, e)
    total += t_max - int_nth_root(t_max, e)

    # b >= 2: t is small enough to enumerate.
    if N <= 4:
        return total

    # If e^b > floor(log2(N-2)), then 2^(e^b) > N-2, hence no t>=2 can satisfy t^(e^b) <= N-2.
    max_exp_for_2 = (N - 2).bit_length() - 1  # floor(log2(N-2))

    possible_bs: list[int] = []
    b = 2
    while True:
        exp = e**b  # exponent on t for the top term
        if exp > max_exp_for_2:
            break
        # minimal n for this b is 2 + 2^exp
        if 2 + (1 << exp) > N:
            break
        possible_bs.append(b)
        b += 1

    if not possible_bs:
        return total

    # Precompute all exact e-th powers up to the maximum t we'll enumerate.
    max_t_limit = 0
    for b in possible_bs:
        exp = e**b
        max_t_limit = max(max_t_limit, int_nth_root(N - 2, exp))

    u_max = int_nth_root(max_t_limit, e)
    non_primitive = {pow(u, e) for u in range(2, u_max + 1)}

    for b in possible_bs:
        exp = e**b
        t_limit = int_nth_root(
            N - 2, exp
        )  # ensure top term <= N-2, so sum can still be <= N
        for t in range(2, t_limit + 1):
            if t in non_primitive:
                continue

            # Build tower: p[k] = t^(e^k) for k=0..b, via repeated powering.
            p = [t]
            x = t
            for _ in range(b):
                x = pow(x, e)
                p.append(x)
            top = p[b]

            # Count valid a in [0..b-1]; p[a] increases with a, so break early.
            cnt_a = 0
            for a in range(b):
                if p[a] + top <= N:
                    cnt_a += 1
                else:
                    break
            total += b * cnt_a

    return total


def D(N: int) -> int:
    """Compute D(N) = sum_{n=2..N} C(n)."""
    total = 0
    e = 2
    while 2 + (1 << e) <= N:  # n = 2 + 2^e is the smallest possible for exponent e
        total += count_for_exponent(N, e)
        e += 1
    return total


def solve() -> int:
    return D(10**18)


def main() -> None:
    # Test values given in the problem statement:
    assert D(10) == 2
    assert D(100) == 21
    assert D(1000) == 69
    assert D(10**6) == 1303
    assert D(10**12) == 1014800

    print(solve())


if __name__ == "__main__":
    main()
