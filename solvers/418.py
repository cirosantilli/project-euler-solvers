#!/usr/bin/env python3
"""
Project Euler 418: Factorisation Triples

We need f(43!), where f(n) = a+b+c for the unique triple (a<=b<=c, abc=n)
that minimises c/a.
"""
from __future__ import annotations

import bisect
import math
from typing import List, Tuple


def prime_sieve(limit: int) -> List[int]:
    """Return all primes <= limit."""
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    r = int(limit**0.5)
    for p in range(2, r + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start : limit + 1 : step] = b"\x00" * (((limit - start) // step) + 1)
    return [i for i in range(2, limit + 1) if sieve[i]]


def legendre_factorial_exponent(n: int, p: int) -> int:
    """Exponent of prime p in n! (Legendre's formula)."""
    s = 0
    while n:
        n //= p
        s += n
    return s


def factorial(n: int) -> int:
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r


def generate_divisors(primes: List[int], exps: List[int]) -> List[int]:
    """Generate all divisors of Π p_i**e_i."""
    divs = [1]
    for p, e in zip(primes, exps):
        pe = 1
        new: List[int] = []
        for _ in range(e + 1):
            for d in divs:
                new.append(d * pe)
            pe *= p
        divs = new
    return divs


def choose_split(exps: List[int], max_divisors: int) -> int:
    """
    Choose a prefix length so that the divisor count of the prefix part
    stays <= max_divisors (greedy).
    """
    dcount = 1
    split = 0
    for i, e in enumerate(exps):
        if i > 0 and dcount * (e + 1) > max_divisors:
            break
        dcount *= e + 1
        split = i + 1
    return split


def divisors_in_range(
    L: int, H: int, divs1_sorted: List[int], divs2: List[int]
) -> List[int]:
    """All divisors d = d1*d2 with d in [L,H], where primes(d1) and primes(d2) are disjoint."""
    if L > H:
        return []
    res: List[int] = []
    for d2 in divs2:
        lo = (L + d2 - 1) // d2  # ceil(L/d2)
        hi = H // d2  # floor(H/d2)
        if lo > hi:
            continue
        i = bisect.bisect_left(divs1_sorted, lo)
        j = bisect.bisect_right(divs1_sorted, hi)
        for d1 in divs1_sorted[i:j]:
            res.append(d1 * d2)
    return res


def best_triple_from_candidates(
    n: int, a_list: List[int], c_list: List[int]
) -> Tuple[int, int, int] | None:
    """
    Return (a,b,c) among candidates minimising c/a, or None if no triple exists.
    Compare ratios exactly using cross-multiplication.
    """
    best: Tuple[int, int, int] | None = None
    c_sorted = sorted(c_list)
    for a in a_list:
        for c in c_sorted:
            if c < a:
                continue
            ac = a * c
            if n % ac != 0:
                continue
            b = n // ac
            if a <= b <= c:
                if best is None:
                    best = (a, b, c)
                else:
                    # c/a < best_c/best_a  <=>  c*best_a < best_c*a
                    if c * best[0] < best[2] * a:
                        best = (a, b, c)
    return best


def f_factorial(k: int) -> int:
    """
    Compute f(k!) using:
    - prime exponents for k!
    - meet-in-the-middle divisor generation
    - narrow search around the cube root (expand window until a triple is found)
    """
    primes = prime_sieve(k)
    exps = [legendre_factorial_exponent(k, p) for p in primes]

    # split primes so the first part has <= ~1e6 divisors (memory/time sweet spot)
    split = choose_split(exps, max_divisors=1_000_000)
    p1, e1 = primes[:split], exps[:split]
    p2, e2 = primes[split:], exps[split:]

    divs1 = generate_divisors(p1, e1)
    divs1.sort()
    divs2 = generate_divisors(p2, e2) if p2 else [1]

    n = factorial(k)
    # Cube root as float is fine for k<=43, but add small slack when converting to ints.
    cbrt = math.exp(math.log(n) / 3.0)

    delta = 1e-6
    while delta <= 0.05:
        # Add a tiny slack (+/-2) to counter float->int rounding at very small deltas.
        aL = max(1, int(cbrt / (1.0 + delta)) - 2)
        aH = int(cbrt) + 2
        cL = max(1, int(cbrt) - 2)
        cH = int(cbrt * (1.0 + delta)) + 2

        a_list = divisors_in_range(aL, aH, divs1, divs2)
        c_list = divisors_in_range(cL, cH, divs1, divs2)

        if a_list and c_list:
            # If the window is huge, the cartesian product may explode. For this problem (43!)
            # we find a triple at a very small delta, so this guard never triggers.
            if len(a_list) * len(c_list) <= 50_000_000:
                best = best_triple_from_candidates(n, a_list, c_list)
                if best is not None:
                    a, b, c = best
                    return a + b + c

        delta *= 2.0

    raise RuntimeError("Failed to find factorisation triple (window grew too large).")


def f_small(n: int) -> int:
    """Brute-force f(n) for small n (used for the statement's tiny examples)."""
    best: Tuple[int, int, int] | None = None
    best_ratio_num = None  # store (c, a) implicitly via best
    # a^3 <= n
    a_max = int(round(n ** (1 / 3))) + 3
    for a in range(1, a_max + 1):
        if n % a != 0:
            continue
        m = n // a
        b_max = int(math.isqrt(m))
        for b in range(a, b_max + 1):
            if m % b != 0:
                continue
            c = m // b
            if b > c:
                continue
            if best is None or c * best[0] < best[2] * a:
                best = (a, b, c)
                best_ratio_num = (c, a)
    if best is None:
        raise ValueError("No triple found (should be impossible for n>=1).")
    return sum(best)


def main() -> None:
    # Given examples in the problem statement:
    assert f_small(165) == 19
    assert f_small(100100) == 142
    assert f_factorial(20) == 4034872

    # Problem asks for f(43!)
    print(f_factorial(43))


if __name__ == "__main__":
    main()
