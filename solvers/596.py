#!/usr/bin/env python3
"""Project Euler 596: Number of lattice points in a hyperball.

Let T(r) be the number of integer quadruplets (x,y,z,t) such that
  x^2 + y^2 + z^2 + t^2 <= r^2.

We use Jacobi's four-square theorem:
  r4(n) = 8 * sum_{d|n, 4∤d} d   for n > 0
where r4(n) counts ordered integer quadruples with sum of four squares = n.

Then for N=r^2:
  T(r) = 1 + sum_{n=1..N} r4(n)
       = 1 + 8 * sum_{d<=N, 4∤d} d * floor(N/d)

Define S(N) = sum_{k=1..N} sigma(k) = sum_{d<=N} d * floor(N/d).
The restriction 4∤d gives:
  sum_{d<=N,4∤d} d*floor(N/d) = S(N) - 4*S(floor(N/4)).

So:
  T(r) = 1 + 8 * ( S(N) - 4*S(N//4) ).

To compute S(N) we use floor-division grouping:
  q = floor(N/i) is constant for i in [i, N//q].
This lets us sum whole ranges of i using arithmetic-series formulas.

Note: For N = 10^16 the grouping still requires ~2*sqrt(N) iterations
(about 2e8), which is heavy in pure Python but is the standard exact method
without specialized low-level optimizations.
"""

from __future__ import annotations

import sys

MOD = 1_000_000_007


def _inv2(mod: int) -> int:
    # mod is prime in this problem, so pow works.
    return (mod + 1) // 2 if mod == MOD else pow(2, mod - 2, mod)


def _sum_range(l: int, r: int, mod: int | None) -> int:
    """Return l+(l+1)+...+r (assumes l<=r)."""
    if l > r:
        return 0
    cnt = r - l + 1
    if mod is None:
        return (l + r) * cnt // 2

    inv2 = _inv2(mod)
    return ((l + r) % mod) * (cnt % mod) % mod * inv2 % mod


def sum_sigma_prefix(n: int, mod: int | None = None) -> int:
    """Compute S(n) = sum_{k=1..n} sigma(k).

    Identity: S(n) = sum_{d=1..n} d * floor(n/d).

    Uses grouping on the constant quotient q = floor(n/i).
    """
    if n <= 0:
        return 0

    total = 0
    i = 1
    while i <= n:
        q = n // i
        j = n // q  # max index with same quotient
        s = _sum_range(i, j, mod)
        if mod is None:
            total += q * s
        else:
            total = (total + (q % mod) * s) % mod
        i = j + 1
    return total


def T(r: int, mod: int | None = None) -> int:
    """Compute T(r), optionally modulo mod."""
    n = r * r
    if mod is None:
        s = sum_sigma_prefix(n, None)
        s4 = sum_sigma_prefix(n // 4, None)
        return 1 + 8 * (s - 4 * s4)

    s = sum_sigma_prefix(n, mod)
    s4 = sum_sigma_prefix(n // 4, mod)
    return (1 + 8 * ((s - 4 * s4) % mod)) % mod


def _self_test() -> None:
    # Test values from the problem statement
    assert T(2) == 89
    assert T(5) == 3121
    assert T(100) == 493490641
    assert T(10**4) == 49348022079085897


def main(argv: list[str]) -> None:
    _self_test()

    if len(argv) >= 2:
        r = int(argv[1])
        print(T(r, MOD))
    else:
        print(T(10**8, MOD))


if __name__ == "__main__":
    main(sys.argv)
