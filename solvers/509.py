#!/usr/bin/env python3
"""
Project Euler 509: Divisor Nim

Rules (single pile):
- A move from a pile of size n is to remove d stones where d is a proper divisor of n (d | n, 1 <= d < n).

For three piles (a, b, c), the game is the disjunctive sum of the three single-pile games,
so the position is losing iff g(a) XOR g(b) XOR g(c) == 0, where g(.) is the Grundy number
of the single-pile game.

This program proves/uses the fact that:
    g(n) = v2(n)  (the exponent of 2 in n; i.e., the number of trailing zero bits in n)
and counts losing triples via the distribution of v2 on [1..N].
"""

from __future__ import annotations


def _counts_v2_upto(n: int) -> list[int]:
    """Return an array f where f[k] = #{1<=x<=n : v2(x) == k}."""
    if n <= 0:
        return [0]
    max_k = n.bit_length() - 1  # max v2 among 1..n occurs at highest power of 2 <= n
    size = (
        1 if max_k == 0 else (1 << max_k.bit_length())
    )  # power-of-two for XOR indexing
    f = [0] * size
    for k in range(max_k + 1):
        # count of numbers divisible by 2^k minus those divisible by 2^(k+1)
        f[k] = (n >> k) - (n >> (k + 1))
    return f


def _losing_triples_from_counts(f: list[int], mod: int | None = None) -> int:
    """
    Given counts f[k], compute L = #{(a,b,c): v2(a)^v2(b)^v2(c)=0}.

    If mod is provided, returns L modulo mod.
    """
    L = 0
    m = len(f)

    if mod is None:
        for i in range(m):
            ci = f[i]
            if ci == 0:
                continue
            for j in range(m):
                cj = f[j]
                if cj == 0:
                    continue
                L += ci * cj * f[i ^ j]
        return L

    # Modular variant to avoid huge intermediates when n is very large.
    for i in range(m):
        ci = f[i] % mod
        if ci == 0:
            continue
        for j in range(m):
            cj = f[j] % mod
            if cj == 0:
                continue
            L = (L + (ci * cj % mod) * (f[i ^ j] % mod)) % mod
    return L


def S(n: int, mod: int | None = None) -> int:
    """
    Number of winning positions (a,b,c) with 1<=a,b,c<=n.

    Winning iff v2(a)^v2(b)^v2(c) != 0.
    So S(n) = n^3 - L(n), where L(n) counts losing triples.
    """
    f = _counts_v2_upto(n)
    if mod is None:
        total = n * n * n
        losing = _losing_triples_from_counts(f, None)
        return total - losing

    nn = n % mod
    total = (nn * nn % mod) * nn % mod
    losing = _losing_triples_from_counts(f, mod)
    return (total - losing) % mod


def main() -> None:
    # Test values from the problem statement
    assert S(10) == 692
    assert S(100) == 735494

    n = 123456787654321
    mod = 1234567890
    print(S(n, mod))


if __name__ == "__main__":
    main()
