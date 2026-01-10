#!/usr/bin/env python3
"""
Project Euler 536: Modulo Power Identity

We need S(10^12), where S(N) is the sum of all m <= N such that:
    a^(m+4) ≡ a (mod m) for all integers a.

For squarefree m, the criterion becomes:
    for every prime p | m: (p-1) | (m+3)

(Equivalent to λ(m) | (m+3) for squarefree m, where λ is Carmichael's function.)

This solution enumerates valid m via backtracking (Carmichael-number style),
using the modular condition:
    L = lcm(p-1 for p|m) must divide (m+3)

Key prunings:
- m is squarefree.
- The only even solution is m=2; all other solutions are odd (because p-1 is even for any odd prime p|m).
- Maintain a partial product A (odd) and L = lcm(p-1 for p|A).
  If we want to extend A with more primes, we must have a cofactor B such that:
        A*B ≡ -3 (mod L)
  This is a linear congruence which gives a residue class for B modulo L/g, where g=gcd(A,L) (here g is always 1 or 3).
  If even the smallest possible B in that class is too large, we prune.
- When the remaining factor can contain at most one prime, we complete in O(#candidates)
  using the constraint (p-1) | (A+3) for the last prime p.
- When at most two primes remain, we try each next prime once and finish with the one-prime completion.

No external libraries are used.
"""

from __future__ import annotations

from math import gcd, isqrt
import sys


def odd_sieve(limit: int):
    """Return (odd_primes, is_prime_bytearray) up to limit."""
    if limit < 2:
        return [], bytearray(limit + 1)

    is_prime = bytearray(b"\x01") * (limit + 1)
    is_prime[0] = 0
    if limit >= 1:
        is_prime[1] = 0

    # clear evens
    for x in range(4, limit + 1, 2):
        is_prime[x] = 0

    r = isqrt(limit)
    for p in range(3, r + 1, 2):
        if is_prime[p]:
            step = p * 2
            start = p * p
            is_prime[start : limit + 1 : step] = b"\x00" * (
                ((limit - start) // step) + 1
            )

    primes = [p for p in range(3, limit + 1, 2) if is_prime[p]]
    return primes, is_prime


def compute_S(
    N: int, primes: list[int], is_prime: bytearray, pminus1: list[int], limitP: int
) -> int:
    """
    Compute S(N) using precomputed odd primes up to limitP (limitP must be >= isqrt(N+4)+5).
    """
    if N < 1:
        return 0

    plen = len(primes)
    total = 0

    # Only even solution is 2
    if N >= 2:
        total += 2

    # Tune: when the congruence modulus M is large, iterate candidates in an AP and
    # primality-test by table instead of scanning the prime list.
    AP_THRESHOLD = 2048

    sys.setrecursionlimit(10000)

    def complete_one(start_idx: int, A: int, L: int, pmin: int):
        """
        Add all solutions of the form m = A * p (p prime, p >= pmin),
        under the assumption that at most one more prime factor will be appended.
        """
        nonlocal total

        pmax = N // A
        if start_idx >= plen or pmin > pmax:
            return

        # g = gcd(A, L) is always 1 or 3; compute cheaply
        g = 3 if (A % 3 == 0 and L % 3 == 0) else 1
        M = L // g
        Ap3 = A + 3

        # Extra safety/validity filters for the new prime p:
        # - p must not divide L unless p == 3 (otherwise gcd(newA, newL) would include p>3)
        # - gcd(A, p-1) must be 1 or 3 (otherwise a prime factor >3 would become common between A and newL)
        if M == 1:
            for i in range(start_idx, plen):
                p = primes[i]
                if p > pmax:
                    break
                if p != 3 and (L % p) == 0:
                    continue
                if (Ap3 % (p - 1)) != 0:
                    continue
                g2 = gcd(A, p - 1)
                if g2 != 1 and g2 != 3:
                    continue
                total += A * p
            return

        invA = pow(A // g, -1, M)
        t0 = ((-3 // g) % M) * invA % M
        if t0 == 0:
            t0 = M  # interpret residue 0 as M for stepping

        if M > AP_THRESHOLD:
            cand = t0
            if cand < pmin:
                cand += ((pmin - cand + M - 1) // M) * M
            for p in range(cand, pmax + 1, M):
                if p <= limitP and is_prime[p]:
                    if p != 3 and (L % p) == 0:
                        continue
                    if (Ap3 % (p - 1)) != 0:
                        continue
                    g2 = gcd(A, p - 1)
                    if g2 != 1 and g2 != 3:
                        continue
                    total += A * p
        else:
            t0_mod = t0 % M
            for i in range(start_idx, plen):
                p = primes[i]
                if p > pmax:
                    break
                if (p % M) != t0_mod:
                    continue
                if p != 3 and (L % p) == 0:
                    continue
                if (Ap3 % (p - 1)) != 0:
                    continue
                g2 = gcd(A, p - 1)
                if g2 != 1 and g2 != 3:
                    continue
                total += A * p

    def dfs(start_idx: int, A: int, L: int):
        """
        Enumerate solutions with prime factors strictly increasing (avoids duplicates).
        A is the current (odd) partial product; L = lcm(p-1 for p|A).
        """
        nonlocal total

        # If A itself is a valid m, include it.
        if ((A + 3) % L) == 0:
            total += A

        if start_idx >= plen:
            return

        pmin = primes[start_idx]
        if A * pmin > N:
            return

        # Congruence pruning: any extension needs a cofactor B with A*B ≡ -3 (mod L).
        # Since gcd(A,L) is 1 or 3, there is a unique residue class mod M=L/g.
        g = 3 if (A % 3 == 0 and L % 3 == 0) else 1
        M = L // g
        if M != 1:
            invA = pow(A // g, -1, M)
            t = ((-3 // g) % M) * invA % M
            if t == 0:
                t = M
            if t < pmin:
                t += ((pmin - t + M - 1) // M) * M
            if A * t > N:
                return

        # If we can't fit two more distinct primes, finish with a single-prime completion.
        if A * pmin * pmin > N:
            complete_one(start_idx, A, L, pmin)
            return

        # If we can't fit three more primes, then at most two primes can remain.
        # First count 1-prime extensions, then 2-prime extensions.
        if A * pmin * pmin * pmin > N:
            complete_one(start_idx, A, L, pmin)

            limit_p = N // (A * pmin)  # p must leave room for another prime >= pmin
            for i in range(start_idx, plen):
                p = primes[i]
                if p > limit_p:
                    break

                # Fast validity checks for adding p
                if p != 3 and (L % p) == 0:
                    continue

                pm1 = pminus1[i]
                g2 = gcd(A, pm1)
                if g2 != 1 and g2 != 3:
                    continue

                newA = A * p
                newL = (L // gcd(L, pm1)) * pm1

                if i + 1 < plen:
                    complete_one(i + 1, newA, newL, primes[i + 1])
            return

        # General branching: try adding another prime factor p
        for i in range(start_idx, plen):
            p = primes[i]
            newA = A * p
            if newA > N:
                break

            if p != 3 and (L % p) == 0:
                continue

            pm1 = pminus1[i]
            g2 = gcd(A, pm1)
            if g2 != 1 and g2 != 3:
                continue

            newL = (L // gcd(L, pm1)) * pm1
            dfs(i + 1, newA, newL)

    dfs(0, 1, 1)
    return total


def main() -> None:
    MAX_N = 10**12
    limitP = isqrt(MAX_N + 4) + 5
    primes, is_prime = odd_sieve(limitP)
    pminus1 = [p - 1 for p in primes]

    # Tests from the problem statement
    assert compute_S(100, primes, is_prime, pminus1, limitP) == 32
    assert compute_S(10**6, primes, is_prime, pminus1, limitP) == 22868117

    print(compute_S(MAX_N, primes, is_prime, pminus1, limitP))


if __name__ == "__main__":
    main()
