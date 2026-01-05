#!/usr/bin/env python3
"""Project Euler 326: Modulo Summations

Sequence:
  a_1 = 1
  a_n = (sum_{k=1}^{n-1} k * a_k) mod n

Count:
  f(N, M) = #{(p,q): 1<=p<=q<=N and (sum_{i=p}^q a_i) mod M = 0}

Key facts used:
  1) Closed form for a_n (depends only on n mod 6):
       n%6==0: a_n = n/2
       n%6==1: a_n = (2n+1)/3
       n%6==2: a_n = n/2
       n%6==3: a_n = (n-3)/6
       n%6==4: a_n = n-1
       n%6==5: a_n = (n-5)/6

  2) Use prefix sums modulo M and count equal values:
       s_0=0, s_n=(s_{n-1}+a_n) mod M
     Then sum_{i=p}^q a_i ≡ 0 (mod M) <=> s_{p-1} == s_q.

  3) For fixed M, (s_n mod M) is periodic with period P = 6*M and s_{n+P}=s_n.
     This lets us enumerate one period and scale to N=10^12.
"""

from __future__ import annotations

from array import array


def a(n: int) -> int:
    """Closed form for a_n (valid for all n >= 1)."""
    r = n % 6
    if r == 0 or r == 2:
        return n // 2
    if r == 1:
        return (2 * n + 1) // 3
    if r == 3:
        return (n - 3) // 6
    if r == 4:
        return n - 1
    # r == 5
    return (n - 5) // 6


def f(N: int, M: int) -> int:
    """Compute f(N, M) as defined in the problem statement."""
    if N < 0 or M <= 0:
        raise ValueError("Require N >= 0 and M > 0")

    P = 6 * M
    q, r = divmod(N, P)

    # Frequency of prefix sums in s_0..s_N.
    # Counts fit in uint64 (<= N+1 <= 1e12+1).
    freq = array("Q", [0]) * M

    # Index i=0 has s_0=0. Residue 0 (mod P) appears at indices 0, P, ..., qP.
    freq[0] += q + 1

    s = 0

    if q == 0:
        # Only indices 0..r occur; avoid iterating the full period.
        for i in range(1, r + 1):
            s = (s + a(i)) % M
            freq[s] += 1
    else:
        # Enumerate one whole period (indices 0..P-1).
        for i in range(1, P):
            s = (s + a(i)) % M
            freq[s] += (q + 1) if i <= r else q

    ans = 0
    for c in freq:
        if c > 1:
            ans += c * (c - 1) // 2
    return ans


def _run_tests() -> None:
    # Test values given in the problem statement.
    first_10 = [1, 1, 0, 3, 0, 3, 5, 4, 1, 9]
    for n, val in enumerate(first_10, start=1):
        assert a(n) == val, (n, a(n), val)

    assert f(10, 10) == 4
    assert f(10**4, 10**3) == 97158


def main() -> None:
    _run_tests()
    print(f(10**12, 10**6))


if __name__ == "__main__":
    main()
