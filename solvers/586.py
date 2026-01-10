#!/usr/bin/env python3
"""
Project Euler 586 - Binary Quadratic Form

We count integers k <= n that have exactly r representations:
    k = a^2 + 3ab + b^2  with integers a > b > 0

Let d = Π (e_p + 1) over primes p ≡ 1,4 (mod 5) in k's factorization (excluding p=5),
and require that primes p ≡ 2,3 (mod 5) appear with even exponent.
Then the number of valid representations is floor(d/2).

So we need count k <= n with d in {2r, 2r+1}.
"""

from __future__ import annotations

import math
import bisect


def sieve_primes_upto(n: int) -> list[int]:
    """Simple sieve of Eratosthenes up to n (inclusive)."""
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    lim = int(math.isqrt(n))
    for p in range(2, lim + 1):
        if sieve[p]:
            start = p * p
            step = p
            sieve[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i in range(n + 1) if sieve[i]]


def iroot(n: int, k: int) -> int:
    """floor(n ** (1/k)) for integers n>=0, k>=1."""
    if k == 1:
        return n
    if k == 2:
        return int(math.isqrt(n))
    # floating guess then fix
    x = int(n ** (1.0 / k))
    if x < 1:
        x = 1
    while pow(x + 1, k) <= n:
        x += 1
    while pow(x, k) > n:
        x -= 1
    return x


def factor_multisets(target: int) -> list[list[int]]:
    """
    All nondecreasing factor multisets (>=2) whose product is target.
    Example: 80 -> [2,2,2,2,5], [2,40], [80], ...
    """
    res: list[list[int]] = []

    def rec(rem: int, start: int, cur: list[int]) -> None:
        if rem == 1:
            res.append(cur.copy())
            return
        for f in range(start, rem + 1):
            if f < 2:
                continue
            if rem % f == 0:
                cur.append(f)
                rec(rem // f, f, cur)
                cur.pop()

    rec(target, 2, [])
    return res


def unique_permutations(multiset: list[int]) -> list[tuple[int, ...]]:
    """Unique permutations of a multiset (small sizes only in this problem)."""
    from collections import Counter

    c = Counter(multiset)
    keys = sorted(c)
    out: list[tuple[int, ...]] = []
    seq = [0] * len(multiset)

    def backtrack(pos: int) -> None:
        if pos == len(multiset):
            out.append(tuple(seq))
            return
        prev = None
        for k in keys:
            if c[k] == 0:
                continue
            if prev == k:
                continue
            prev = k
            c[k] -= 1
            seq[pos] = k
            backtrack(pos + 1)
            c[k] += 1

    backtrack(0)
    return out


def multipliers_prefix(qmax: int) -> list[int]:
    """
    Build W[0..qmax] where W[x] is the count of multipliers <= x of form:
        5^a * s^2
    where s only uses primes p ≡ 2,3 (mod 5) (inert primes), any exponents.
    """
    if qmax <= 0:
        return [0]

    inert_primes = [
        p for p in sieve_primes_upto(int(math.isqrt(qmax)) + 1) if p % 5 in (2, 3)
    ]

    vals: list[int] = []

    def rec(idx: int, cur: int) -> None:
        # multiply by 5^a
        t = cur
        while t <= qmax:
            vals.append(t)
            t *= 5

        # multiply by inert prime squares
        for j in range(idx, len(inert_primes)):
            p = inert_primes[j]
            p2 = p * p
            if cur * p2 > qmax:
                break
            x = cur * p2
            while x <= qmax:
                rec(j + 1, x)
                x *= p2

    rec(0, 1)
    vals = sorted(set(vals))

    W = [0] * (qmax + 1)
    c = 0
    i = 0
    for x in range(1, qmax + 1):
        while i < len(vals) and vals[i] == x:
            c += 1
            i += 1
        W[x] = c
    return W


def build_sequences(
    n: int, r: int, first_split_primes: list[int]
) -> list[tuple[int, ...]]:
    """
    Build all exponent sequences (ordered for increasing primes) whose (e+1) product is 2r or 2r+1,
    and whose minimal possible core <= n.
    """
    seqs: list[tuple[int, ...]] = []
    for d in (2 * r, 2 * r + 1):
        for facs in factor_multisets(d):
            exps = [f - 1 for f in facs]
            for seq in unique_permutations(exps):
                if len(seq) > len(first_split_primes):
                    continue
                prod = 1
                ok = True
                for p, e in zip(first_split_primes, seq):
                    prod *= pow(p, e)
                    if prod > n:
                        ok = False
                        break
                if ok:
                    seqs.append(seq)
    return seqs


def compute_f(n: int, r: int) -> int:
    # get enough small split primes for minimal core checks
    small_primes = sieve_primes_upto(20000)
    first_split = [p for p in small_primes if p % 5 in (1, 4)]
    seqs = build_sequences(n, r, first_split)
    if not seqs:
        return 0

    # smallest core among all sequences (using smallest split primes)
    min_core = None
    for seq in seqs:
        prod = 1
        for p, e in zip(first_split, seq):
            prod *= pow(p, e)
        if min_core is None or prod < min_core:
            min_core = prod
    assert min_core is not None
    qmax = n // min_core

    W = multipliers_prefix(qmax)

    # prime sieve bound needed: only up to maximal possible last prime
    max_need = 0
    for seq in seqs:
        if len(seq) == 1:
            bound = iroot(n, seq[0])
        else:
            prod = 1
            for p, e in zip(first_split, seq[:-1]):
                prod *= pow(p, e)
            bound = iroot(n // prod, seq[-1])
        if bound > max_need:
            max_need = bound

    primes = sieve_primes_upto(max_need + 10)
    split_primes = [p for p in primes if p % 5 in (1, 4)]

    # Fast last-level summation with quotient grouping
    def sum_last(A: int, start_idx: int, e: int) -> int:
        max_p = iroot(n // A, e)
        end_idx = bisect.bisect_right(split_primes, max_p)
        if end_idx <= start_idx:
            return 0

        total = 0
        idx = start_idx
        while idx < end_idx:
            p = split_primes[idx]
            pe = p if e == 1 else (p * p if e == 2 else pow(p, e))
            q = n // (A * pe)
            # group all primes up to high_p giving same q
            high_p = iroot(n // (A * q), e)
            if high_p > max_p:
                high_p = max_p
            idx2 = bisect.bisect_right(split_primes, high_p, idx, end_idx)
            total += (idx2 - idx) * W[q]
            idx = idx2
        return total

    def sum_for_sequence(seq: tuple[int, ...]) -> int:
        k = len(seq)
        total = 0

        def rec(pos: int, start_idx: int, A: int) -> None:
            nonlocal total
            if pos == k - 1:
                total += sum_last(A, start_idx, seq[pos])
                return

            e = seq[pos]
            max_p_here = iroot(n // A, e)
            for idx in range(start_idx, len(split_primes)):
                # need enough primes remaining
                if idx + (k - 1 - pos) >= len(split_primes):
                    break

                p = split_primes[idx]
                if p > max_p_here:
                    break

                pe = p if e == 1 else (p * p if e == 2 else pow(p, e))
                newA = A * pe
                if newA > n:
                    break

                max_rem = n // newA
                # minimal remaining product uses the next split primes
                prod_min = 1
                ok = True
                for j in range(pos + 1, k):
                    pj = split_primes[idx + (j - pos)]
                    ej = seq[j]
                    prod_min *= pj if ej == 1 else (pj * pj if ej == 2 else pow(pj, ej))
                    if prod_min > max_rem:
                        ok = False
                        break
                if not ok:
                    break

                rec(pos + 1, idx + 1, newA)

        rec(0, 0, 1)
        return total

    ans = 0
    for seq in seqs:
        ans += sum_for_sequence(seq)
    return ans


def main() -> None:
    # Given in the problem statement:
    assert compute_f(10**5, 4) == 237
    assert compute_f(10**8, 6) == 59517

    print(compute_f(10**15, 40))


if __name__ == "__main__":
    main()
