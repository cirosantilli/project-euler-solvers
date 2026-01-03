#!/usr/bin/env python3
"""
Project Euler 452 - Long Products

Define F(m,n) as the number of n-tuples of positive integers
for which the product of the elements doesn't exceed m.

We need:
    F(10^9, 10^9) mod 1234567891

Key observation:
If product <= m, then at most floor(log2(m)) entries can be > 1
(because 2^k <= m).
For m = 10^9 this maximum is 29.

So we count all *multisets* of values > 1 with multiplicities
(sum of multiplicities <= 29) such that the product constraint holds.
Then for each multiplicity pattern we compute how many ordered n-tuples
it produces (placing those values into n slots, filling the rest with 1s),
and sum contributions modulo MOD.

No external libraries used.
"""

from math import isqrt, gcd

MOD = 1234567891


def floor_log2(x: int) -> int:
    """Return floor(log2(x)) without floating point."""
    if x < 2:
        return 0
    p = 1
    k = 0
    while (p << 1) <= x:
        p <<= 1
        k += 1
    return k


def count_patterns(m: int) -> dict:
    """
    Count multiplicity patterns.

    A pattern is a multiset of multiplicities (exponents) of distinct integers > 1.
    Example pattern (10,2,1) represents choosing distinct a,b,c>1 such that:
        a^10 * b^2 * c^1 <= m
    and the tuple contains a repeated 10 times, b repeated 2 times, c once.
    We count how many distinct sets of values realize each pattern.

    Returns: dict {pattern_tuple_sorted_desc: count}
    """
    max_nonones = floor_log2(m)  # maximum total multiplicity
    patterns = {}

    def add_pattern(parts, amount):
        key = tuple(sorted(parts, reverse=True))
        patterns[key] = patterns.get(key, 0) + amount

    def dfs(min_val: int, limit: int, slots: int, parts: list):
        # Option: stop here (this set of chosen values is a valid configuration).
        add_pattern(parts, 1)

        if slots == 0 or min_val > limit:
            return

        # If limit < min_val^2, then we cannot add two distinct numbers >= min_val,
        # nor can we add any exponent >=2. So at most one more number can be added,
        # and it can only appear once.
        if limit < min_val * min_val:
            if slots >= 1 and limit >= min_val:
                add_pattern(parts + [1], limit - min_val + 1)
            return

        root = isqrt(limit)

        # Choose next value v in [min_val .. root] with exponent >=1 (up to slots)
        for v in range(min_val, root + 1):
            p = v
            for e in range(1, slots + 1):
                if p > limit:
                    break
                dfs(v + 1, limit // p, slots - e, parts + [e])
                p *= v

        # Values in (root .. limit] can only appear once (exponent 1),
        # and after choosing such a v we cannot choose any further values.
        start = max(min_val, root + 1)
        if slots >= 1 and start <= limit:
            add_pattern(parts + [1], limit - start + 1)

    dfs(2, m, max_nonones, [])
    return patterns


def ways_to_place(n: int, pattern: tuple) -> int:
    """
    Number of ordered n-tuples corresponding to a multiplicity pattern.

    Let k = sum(pattern).
    We place k non-1 entries into n positions (ordered), with repeats according
    to multiplicities in pattern, and remaining n-k entries are 1.

    Count = n! / (n-k)! / Π (mi!)
          = falling_factorial(n, k) / Π (mi!)

    Since MOD is not prime, we compute exactly as integers using gcd cancellation,
    then take modulo at the end.
    """
    k = sum(pattern)
    if k == 0:
        return 1

    numerators = [n - i for i in range(k)]

    # Precompute small factorials up to 29 (enough for this problem)
    # factorial(x) small, exact division guaranteed.
    for mi in pattern:
        d = 1
        for t in range(2, mi + 1):
            d *= t
        # Cancel d against the numerator factors
        for i in range(len(numerators)):
            if d == 1:
                break
            g = gcd(numerators[i], d)
            if g > 1:
                numerators[i] //= g
                d //= g
        # Extra pass (rarely needed)
        if d != 1:
            for i in range(len(numerators)):
                if d == 1:
                    break
                g = gcd(numerators[i], d)
                if g > 1:
                    numerators[i] //= g
                    d //= g

        assert d == 1, "Exact cancellation failed (should never happen)."

    res = 1
    for v in numerators:
        res *= v
    return res


def F(m: int, n: int, mod: int = MOD) -> int:
    """
    Compute F(m,n) modulo mod using pattern enumeration.
    """
    pats = count_patterns(m)
    total = 0
    for pat, cnt in pats.items():
        ways = ways_to_place(n, pat) % mod
        total = (total + (cnt % mod) * ways) % mod
    return total


def main():
    # Given test values from the statement
    assert F(10, 10, MOD) == 571
    assert F(10**6, 10**6, MOD) == 252903833

    # Required answer
    ans = F(10**9, 10**9, MOD)
    print(ans)


if __name__ == "__main__":
    main()

