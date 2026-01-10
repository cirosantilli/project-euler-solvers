#!/usr/bin/env python3
"""
Project Euler 522 - Hilbert's Blackout

We consider loopless endofunctions on {1..n}: each floor sends power to exactly one *other* floor.
Hilbert may rewire some floors (change their outgoing edge). An arrangement is "safe" iff it is a
single directed n-cycle (then any starting floor reaches all floors).

Let:
  z = number of nodes with indegree 0 (nobody sends power to them)
  p = number of "pure" components: directed cycles with no in-trees attached (i.e. a component
      consisting only of a cycle)

A key structural fact (proved in README) is that for loopless functional digraphs:
  minimal rewires = z + p, except when the graph is already a single n-cycle (then 0).

So for n >= 2:
  F(n) = sum_over_all_loopless_mappings z  +  sum_over_all_loopless_mappings p  - (# directed n-cycles)

Both sums can be computed by linearity of expectation.

Given modulus:
  MOD = 135707531  (prime; see README citations)

The required answer is F(12344321) mod MOD.
"""

from array import array

MOD = 135707531


def F(n: int, mod: int = MOD) -> int:
    """Return F(n) modulo mod."""
    if n <= 2:
        # For n=2 there's exactly one arrangement: 2-cycle, already safe.
        return 0

    # --- Sum of indegree-0 vertices across all loopless mappings ---
    # For a fixed vertex v, the probability that none of the other (n-1) vertices map to v is
    # ((n-2)/(n-1))^(n-1), hence:
    # total_z = (n-1)^n * n * ((n-2)/(n-1))^(n-1) = n*(n-1)*(n-2)^(n-1).
    total_z = (n % mod) * ((n - 1) % mod) % mod
    total_z = total_z * pow(n - 2, n - 1, mod) % mod

    # --- Sum of pure components (excluding the full n-cycle, which will be subtracted) ---
    #
    # Fix a directed cycle on k vertices (k>=2). It is a *pure component* iff:
    #   - those k vertices follow the cycle,
    #   - no vertex outside the cycle points into the cycle.
    #
    # If m = n-k vertices are outside the cycle, each outside vertex has (m-1) choices
    # (must point within the outside set and not to itself), hence (m-1)^m possibilities.
    #
    # Counting directed k-cycles on labeled vertices gives C(n,k)*(k-1)! = n!/(k*(n-k)!).
    #
    # Therefore, for n>=3:
    #   sum_p = (n-1)! + n! * sum_{m=2..n-2} (m-1)^m / ((n-m)*m!)
    #
    # In the final F(n) we subtract the number of directed n-cycles, which is (n-1)!,
    # so we only need:
    #   extra_p = n! * sum_{m=2..n-2} (m-1)^m / ((n-m)*m!)
    #
    # We compute it modulo mod using modular inverses. Since n < mod and mod is prime,
    # all 1..n are invertible modulo mod.

    # Precompute modular inverses inv[i] for 1<=i<=n in O(n), and n! mod mod.
    inv = array("I", [0]) * (n + 1)
    inv[1] = 1
    fact_n = 1
    for i in range(2, n + 1):
        inv[i] = (mod - (mod // i) * inv[mod % i] % mod) % mod
        fact_n = (fact_n * i) % mod

    # Accumulate S = sum_{m=2..n-2} (m-1)^m * inv_fact[m] * inv[n-m]
    # where inv_fact[m] = 1/m!.
    inv_fact = 1  # 1/0!
    S = 0
    pow_ = pow
    inv_local = inv
    mod_local = mod
    n_local = n

    for m in range(1, n_local - 1):  # m = 1..n-2
        inv_fact = (inv_fact * inv_local[m]) % mod_local  # now 1/m!
        if m >= 2:
            term = pow_(m - 1, m, mod_local)
            term = (term * inv_fact) % mod_local
            term = (term * inv_local[n_local - m]) % mod_local
            S += term
            if S >= mod_local:
                S %= mod_local

    extra_p = (fact_n * (S % mod_local)) % mod_local

    return (total_z + extra_p) % mod_local


def main() -> None:
    # Test values from the problem statement.
    assert F(3) == 6
    assert F(8) == 16276736
    assert F(100) == 84326147  # "F(100) mod 135707531"

    print(F(12344321))


if __name__ == "__main__":
    main()
