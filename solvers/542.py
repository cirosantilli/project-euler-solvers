#!/usr/bin/env python3
"""
Project Euler 542: Geometric Progression with Maximum Sum

We compute:
  S(k) = maximal sum of >=3 distinct positive integers <= k that form a geometric progression
  T(n) = sum_{k=4..n} (-1)^k * S(k)

Answer required: T(10^17)

No external libraries used.
"""
from __future__ import annotations


def iroot(n: int, k: int) -> int:
    """Return floor(n ** (1/k)) for integers n>=0, k>=1."""
    if k <= 1:
        return n
    # Float guess then fix with a couple of integer-power checks.
    x = int(n ** (1.0 / k))
    if x < 1:
        x = 1
    # Adjust around the floating-point rounding error.
    while pow(x + 1, k) <= n:
        x += 1
    while pow(x, k) > n:
        x -= 1
    return x


def S(k: int) -> int:
    """
    Compute S(k).

    Key fact:
      An optimal integer GP can be written (after sorting increasingly) as
        b*(p-1)^t, b*(p-1)^(t-1)*p, ..., b*p^t
      where p>=2, t>=2, b>=1, and the sum equals:
        b * (p^(t+1) - (p-1)^(t+1))

    Therefore:
      S(k) = max_{p>=2, t>=2} (k // p^t) * (p^(t+1) - (p-1)^(t+1))
    """
    if k < 4:
        return 0

    best = 0
    # t_max satisfies 2^t_max <= k
    t_max = k.bit_length() - 1

    # Iterate t downward; once (t+1)*k <= best, smaller t cannot beat best.
    for t in range(t_max, 1, -1):
        p_max = iroot(k, t)
        if p_max < 2:
            continue

        # Upper bound for any GP of length (t+1):
        #   sum <= (t+1)*k and also sum < p*k (since coefficient < p <= p_max)
        ub = min(t + 1, p_max) * k
        if ub <= best:
            # If p_max >= t+1 then ub=(t+1)*k and will only decrease for smaller t.
            if p_max >= t + 1:
                break
            continue

        # Brute-force p in this (small) range.
        for p in range(2, p_max + 1):
            d = pow(p, t)
            b = k // d
            if b == 0:
                break
            c = pow(p, t + 1) - pow(p - 1, t + 1)
            val = b * c
            if val > best:
                best = val

    return best


def alt_sum_constant(a: int, b: int) -> int:
    """Compute sum_{k=a..b} (-1)^k (returns -1, 0, or +1 times the constant)."""
    if a > b:
        return 0
    length = b - a + 1
    if length % 2 == 0:
        return 0
    return 1 if (a % 2 == 0) else -1


def T(n: int) -> int:
    """
    Compute T(n) = sum_{k=4..n} (-1)^k S(k).

    S(k) is nondecreasing and piecewise constant for long intervals.
    We jump between change points using exponential search + binary search.
    """
    if n < 4:
        return 0

    cache: dict[int, int] = {}

    def S_cached(x: int) -> int:
        v = cache.get(x)
        if v is None:
            v = S(x)
            cache[x] = v
        return v

    total = 0
    k = 4

    while k <= n:
        v = S_cached(k)

        # Exponential search for an upper bound where S changes.
        step = 1
        hi = min(n, k + step)
        v_hi = S_cached(hi)
        while v_hi == v and hi != n:
            step *= 2
            hi = min(n, k + step)
            v_hi = S_cached(hi)

        if hi == n and v_hi == v:
            # No change up to n.
            total += v * alt_sum_constant(k, n)
            break

        # Binary search first index in (k, hi] where S > v.
        lo = k + 1
        r = hi
        while lo < r:
            mid = (lo + r) // 2
            if S_cached(mid) == v:
                lo = mid + 1
            else:
                r = mid
        change = lo  # S(change) > v

        total += v * alt_sum_constant(k, change - 1)
        k = change

    return total


def main() -> None:
    # Asserts from the problem statement
    assert S(4) == 7
    assert S(10) == 19
    assert S(12) == 21
    assert S(1000) == 3439
    assert T(1000) == 2268

    n = 10**17
    print(T(n))


if __name__ == "__main__":
    main()
