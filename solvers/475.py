#!/usr/bin/env python3
"""Project Euler 475: Music Festival

12n musicians first form 3n fixed quartets (a fixed partition into groups of 4).
Next day they form 4n trios such that no trio contains two musicians from the
same original quartet.

This program computes f(600) mod 1_000_000_007.

It also asserts the two check values from the problem statement:
  f(12) = 576
  f(24) mod 1_000_000_007 = 509089824

No external libraries are used.
"""

import sys

MOD = 1_000_000_007


def _prep_factorials(limit: int):
    """Return (fact, invfact) modulo MOD for 0..limit."""
    fact = [1] * (limit + 1)
    for i in range(1, limit + 1):
        fact[i] = fact[i - 1] * i % MOD

    invfact = [1] * (limit + 1)
    invfact[limit] = pow(fact[limit], MOD - 2, MOD)
    for i in range(limit, 0, -1):
        invfact[i - 1] = invfact[i] * i % MOD

    return fact, invfact


def compute_f(n: int) -> int:
    """Compute f(12n) modulo MOD."""
    E = 4 * n  # number of trios
    m = 3 * n  # number of quartets (variables)

    # Largest factorial index we need is max(3i+j) where i,j <= E, i+j<=E.
    # So max(3i+j) <= 4E = 16n.
    limit = 16 * n + 10
    fact, invfact = _prep_factorials(limit)

    # Precompute small power tables used heavily in loops.
    pow2 = [1] * (E + 1)
    for t in range(1, E + 1):
        pow2[t] = (pow2[t - 1] * 2) % MOD

    neg3 = MOD - 3
    pow_neg3 = [1] * (E + 1)
    for t in range(1, E + 1):
        pow_neg3[t] = (pow_neg3[t - 1] * neg3) % MOD

    inv2 = (MOD + 1) // 2
    inv24 = pow(24, MOD - 2, MOD)

    # It can be shown that a <= m and (b+d) <= E for the inner sums.
    inv24pow = [1] * (m + 1)
    for t in range(1, m + 1):
        inv24pow[t] = (inv24pow[t - 1] * inv24) % MOD

    inv2pow = [1] * (E + 1)
    for t in range(1, E + 1):
        inv2pow[t] = (inv2pow[t - 1] * inv2) % MOD

    # sigma is the reduced sum described in README; final f cancels E!.
    sigma = 0
    for i in range(E + 1):
        max_j = E - i
        for j in range(max_j + 1):
            k = E - i - j
            A = 3 * i + j

            base = fact[A] * invfact[i] % MOD
            base = base * pow_neg3[j] % MOD
            base = base * pow2[k] % MOD

            dmin = 0 if i >= n else (n - i)
            dmax = j // 2
            if dmin > dmax:
                continue

            invfact_c = invfact[k]
            sumd = 0
            for d in range(dmin, dmax + 1):
                a = i - n + d
                b = j - 2 * d

                # term = 1/(a! b! c! d! 24^a 2^(b+d))
                term = invfact[a]
                term = term * invfact[b] % MOD
                term = term * invfact_c % MOD
                term = term * invfact[d] % MOD
                term = term * inv24pow[a] % MOD
                term = term * inv2pow[b + d] % MOD

                sumd = (sumd + term) % MOD

            sigma = (sigma + base * sumd) % MOD

    # f = 24^m * m! * sigma / 6^E
    pow24m = pow(24, m, MOD)
    inv6E = pow(pow(6, E, MOD), MOD - 2, MOD)
    return pow24m * fact[m] % MOD * sigma % MOD * inv6E % MOD


def main() -> None:
    # Optional command line: python3 main.py 50
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 50

    # Asserts for the test values given in the statement.
    assert compute_f(1) == 576
    assert compute_f(2) == 509089824

    print(compute_f(n))


if __name__ == "__main__":
    main()
