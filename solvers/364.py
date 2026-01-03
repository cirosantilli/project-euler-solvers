#!/usr/bin/env python3
"""
Project Euler 364 - Comfortable Distance

We count the number of possible seat-taking sequences under the rules, modulo 100000007.

Key idea (sketch):
- While rule (1) applies, chosen seats can never be adjacent, and rule (1) continues until the chosen
  set becomes a *maximal independent set* on a path of length N.
- Maximal independent sets on a path have gaps of size 1 or 2 between chosen seats, and possibly
  a single empty seat at each end.

From any maximal independent set:
- Stage 1 (rule 1): pick the k seats of the maximal independent set in any order  -> k!
- Each gap of size 2 (pattern 1 0 0 1) yields two choices for which middle seat is taken in stage 2,
  and exactly one such seat is taken in stage 2 -> factor 2^p, where p = number of size-2 gaps.
- End gaps (if present) contribute forced stage-2 picks.
- Stage 2 (rule 2): pick all stage-2 seats in any order -> (p + e)!
- Stage 3 (rule 3): the remaining seats are isolated (each has two occupied neighbors), so any order
  -> (k-1)!  (one remaining seat per gap between stage-1 seats)

We then count how many maximal independent sets have given (p, k, e) using compositions with steps 2/3.
"""

import sys

MOD = 100000007
N_TARGET = 1_000_000


def prepare_factorials(max_n: int, mod: int):
    """Precompute factorials and inverse factorials up to max_n modulo mod (mod is prime)."""
    fact = [1] * (max_n + 1)
    for i in range(1, max_n + 1):
        fact[i] = (fact[i - 1] * i) % mod

    invfact = [1] * (max_n + 1)
    invfact[max_n] = pow(fact[max_n], mod - 2, mod)
    for i in range(max_n, 0, -1):
        invfact[i - 1] = (invfact[i] * i) % mod
    return fact, invfact


def prepare_powers_of_two(max_p: int, mod: int):
    pow2 = [1] * (max_p + 1)
    for i in range(1, max_p + 1):
        pow2[i] = (pow2[i - 1] * 2) % mod
    return pow2


def nCk(n: int, k: int, fact, invfact, mod: int) -> int:
    if k < 0 or k > n:
        return 0
    return (fact[n] * invfact[k] % mod) * invfact[n - k] % mod


def T(n: int, fact, invfact, pow2, mod: int = MOD) -> int:
    """
    Compute T(n) mod mod.

    Boundary parameters:
      a in {1,2}  : position of first stage-1 seat (1 => no left end gap, 2 => one left end gap)
      b in {0,1}  : whether there is one trailing seat after the last stage-1 seat (b=1 means last at n-1)
      e = (a==2) + (b==1)  : number of end-gap seats (forced stage-2 picks)

    Between consecutive stage-1 seats the distance is 2 or 3:
      distance 2 => pattern 1 0 1 (one size-1 gap)
      distance 3 => pattern 1 0 0 1 (one size-2 gap)

    Let p = #distance-3 steps, q = #distance-2 steps.
      3p + 2q = L, where L = n - a - b
      k = 1 + p + q = 1 + (L - p)/2
      number of step-orderings = C(p+q, p) = C(k-1, p)
    """
    res = 0
    for a in (1, 2):
        for b in (0, 1):
            L = n - a - b
            if L < 0:
                continue
            e = (1 if a == 2 else 0) + (1 if b == 1 else 0)

            # Need L - 3p even  <=> (L - p) even, so p has fixed parity.
            start_p = L & 1
            max_p = L // 3
            for p in range(start_p, max_p + 1, 2):
                rem = L - 3 * p
                if rem < 0:
                    break
                # rem is even by construction
                q = rem // 2
                k = 1 + p + q  # also equals 1 + (L - p)//2
                # count of maximal independent sets with these step counts
                ways_mis = nCk(k - 1, p, fact, invfact, mod)
                # contribution
                term = ways_mis
                term = (term * pow2[p]) % mod
                term = (term * fact[k]) % mod
                term = (term * fact[p + e]) % mod
                term = (term * fact[k - 1]) % mod
                res += term
                res %= mod
    return res


def main() -> None:
    max_n = N_TARGET
    fact, invfact = prepare_factorials(max_n, MOD)
    pow2 = prepare_powers_of_two(max_n // 3 + 3, MOD)

    # Asserts from the problem statement
    assert T(4, fact, invfact, pow2, MOD) == 8
    assert T(10, fact, invfact, pow2, MOD) == 61632
    assert T(1000, fact, invfact, pow2, MOD) == 47255094

    ans = T(N_TARGET, fact, invfact, pow2, MOD)
    sys.stdout.write(str(ans) + "\n")


if __name__ == "__main__":
    main()
