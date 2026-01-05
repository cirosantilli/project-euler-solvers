"""Project Euler 256: Tatami-Free Rooms.

We use a fast characterization of when an a×b rectangle is *tatami-free* (cannot
be tiled by 1×2 tatami with no four tatami corners meeting at a point).

Let a<=b and let q = b//a. Then the rectangle is tatami-free iff:

    (a+1)*q + 2 <= b <= (a-1)*(q+1) - 2

Given this, T(s) is the number of factor pairs (a,b) with a*b=s, a<=b,
that satisfy the inequality.

To find the smallest s with T(s)=N, we enumerate candidate s by recursively
building prime factorizations (starting from 2 to ensure even area), prune by a
cheap upper bound on the number of factor pairs, and compute T(s) only when the
bound is large enough.

This is a Python translation of the well-known fast approach by Eric Olson.
"""

from __future__ import annotations

import math
from functools import lru_cache
from typing import List, Tuple


S_MAX = 100_000_000  # search bound used by common reference solutions
P_NUM = 1300  # number of primes to precompute (enough for S_MAX)
F_NUM = 10  # max number of distinct primes tracked in the DFS


def _first_n_primes(n: int) -> List[int]:
    """Return the first n primes via a sieve."""
    if n <= 0:
        return []

    # 1300th prime is 10657; 20000 is a safe sieve limit.
    limit = 20_000
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    for p in range(2, int(limit**0.5) + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start : limit + 1 : step] = b"\x00" * (((limit - start) // step) + 1)
    primes: List[int] = [i for i, is_p in enumerate(sieve) if is_p]
    if len(primes) < n:
        raise RuntimeError("Prime sieve limit too small")
    return primes[:n]


@lru_cache(maxsize=1)
def _primes() -> Tuple[int, ...]:
    return tuple(_first_n_primes(P_NUM))


def _tfree(a: int, b: int) -> bool:
    """Return True if the a×b rectangle is tatami-free. Assumes a<=b."""
    q = b // a
    lmin = (a + 1) * q + 2
    lmax = (a - 1) * (q + 1) - 2
    return lmin <= b <= lmax


def tatami_free_factor_pairs(s: int) -> List[Tuple[int, int]]:
    """All tatami-free factor pairs (a, b) with a*b=s and a<=b."""
    res: List[Tuple[int, int]] = []
    for a in range(1, math.isqrt(s) + 1):
        if s % a:
            continue
        b = s // a
        if a <= b and _tfree(a, b):
            res.append((a, b))
    return res


def T_of_s(s: int) -> int:
    """Compute T(s) by enumerating factor pairs."""
    return len(tatami_free_factor_pairs(s))


def smallest_s_with_T(target: int) -> int:
    """Return the smallest s such that T(s)==target (or -1 if none <=S_MAX)."""

    primes = _primes()

    # Current factorization (in-place during DFS).
    p = [0] * F_NUM  # primes
    e = [0] * F_NUM  # exponents

    best = S_MAX + 1

    def sigma_bound(fmax: int) -> int:
        """Cheap upper bound used for pruning.

        Matches the original reference implementation: exponent of 2 contributes
        as e[0] (not e[0]+1), others contribute (exp+1).
        """
        r = e[0]
        for idx in range(1, fmax + 1):
            r *= e[idx] + 1
        return r

    def T_from_factorization(fmax: int, s: int) -> int:
        """Compute T(s) using the stored factorization p[0..fmax], e[0..fmax]."""
        # Precompute powers for fast multiplication.
        pow_lists: List[List[int]] = []
        for idx in range(fmax + 1):
            pi = p[idx]
            ei = e[idx]
            arr = [1] * (ei + 1)
            v = 1
            for k in range(1, ei + 1):
                v *= pi
                arr[k] = v
            pow_lists.append(arr)

        z = [0] * (fmax + 1)
        res = 0

        # Iterate over all exponent splits (skipping the all-zero split, as in C).
        while True:
            i = 0
            while i <= fmax and z[i] == e[i]:
                z[i] = 0
                i += 1
            if i > fmax:
                break
            z[i] += 1

            k = 1
            l = 1
            for j in range(fmax + 1):
                k *= pow_lists[j][z[j]]
                l *= pow_lists[j][e[j] - z[j]]
            if k <= l and _tfree(k, l):
                res += 1
        return res

    def dfs(i_idx: int, fmax: int, s: int) -> None:
        nonlocal best
        if s >= best or s > S_MAX:
            return

        if sigma_bound(fmax) >= target:
            t = T_from_factorization(fmax, s)
            if t == target and s < best:
                best = s

        pmax = S_MAX // s

        # Option 1: increase the exponent of the current prime.
        cur_p = primes[i_idx]
        if cur_p <= pmax:
            e[fmax] += 1
            dfs(i_idx, fmax, s * cur_p)
            e[fmax] -= 1

        # Option 2: introduce a new distinct prime.
        nf = fmax + 1
        if nf >= F_NUM:
            return
        e[nf] = 1
        for j in range(i_idx + 1, len(primes)):
            pj = primes[j]
            if pj > pmax:
                break
            p[nf] = pj
            dfs(j, nf, s * pj)
        e[nf] = 0

    # Start with a factor 2 to ensure even area.
    p[0] = 2
    e[0] = 1
    dfs(0, 0, 2)

    return best if best <= S_MAX else -1


def main() -> None:
    # Test values from the problem statement.
    # (Examples are quoted in many mirrors of PE256.)
    assert T_of_s(70) == 1
    assert set(tatami_free_factor_pairs(70)) == {(7, 10)}

    assert T_of_s(1320) == 5
    assert set(tatami_free_factor_pairs(1320)) == {
        (20, 66),
        (22, 60),
        (24, 55),
        (30, 44),
        (33, 40),
    }

    assert smallest_s_with_T(5) == 1320

    print(smallest_s_with_T(200))


if __name__ == "__main__":
    main()
