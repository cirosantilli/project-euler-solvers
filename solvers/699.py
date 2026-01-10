#!/usr/bin/env python3
"""
Project Euler 699 - Triffle Numbers

We need T(N): sum of all n <= N such that when sigma(n)/n is reduced to a/b,
the denominator b is a power of 3 with exponent > 0.

This solution uses:
- p-adic valuation constraints derived from gcd(n, sigma(n))
- multiplicativity of sigma(n)
- backtracking with strong pruning
"""

import sys

sys.setrecursionlimit(10000)


# Candidate primes that can occur in triffle numbers up to 10^14.
# (Prime 3 is handled separately via n = 3^a * m, where gcd(m,3)=1.)
PRIMES = [
    2,
    3,
    5,
    7,
    11,
    13,
    17,
    19,
    23,
    31,
    37,
    41,
    61,
    67,
    73,
    127,
    193,
    547,
    661,
    757,
    1093,
    1181,
    1597,
    1871,
    3851,
    4561,
    8191,
    34511,
    131071,
    524287,
    797161,
]
PRIMES_NO3 = [p for p in PRIMES if p != 3]
PRIMES_NO3.sort()
P = len(PRIMES_NO3)
P_INDEX = {p: i for i, p in enumerate(PRIMES_NO3)}


def _sigma_prime_power(p: int, e: int) -> int:
    """sigma(p^e) = (p^(e+1)-1)/(p-1)"""
    return (pow(p, e + 1) - 1) // (p - 1)


def _build_components(max_n: int):
    """
    Precompute for each prime p != 3 a list for exponents e>=1 with p^e <= max_n:
        (p^e, sparse_factorization_of_sigma(p^e) over PRIMES_NO3, v3(sigma(p^e))).
    The sparse factorization lists only the primes in PRIMES_NO3 that divide sigma(p^e).
    """
    comps = {}
    for p in PRIMES_NO3:
        lst = []
        pe = p
        e = 1
        while pe <= max_n:
            s = _sigma_prime_power(p, e)
            tmp = s
            sparse = []
            # Factor tmp only by the relevant prime set; remaining factors are irrelevant
            # because they cannot appear in n under the 10^14 constraint.
            for q in PRIMES_NO3:
                if q == p:
                    continue
                if tmp % q == 0:
                    c = 0
                    while tmp % q == 0:
                        tmp //= q
                        c += 1
                    sparse.append((P_INDEX[q], c))
            c3 = 0
            while tmp % 3 == 0:
                tmp //= 3
                c3 += 1
            lst.append((pe, tuple(sparse), c3))
            e += 1
            pe *= p
        comps[p] = lst
    return comps


# Global precomputation used for all T(N) calls in this file.
COMPONENTS = _build_components(10**14)


def T(N: int) -> int:
    """
    Compute T(N).

    Write n = 3^a * m where a = v3(n) >= 1 and gcd(m,3)=1.
    Then:
      - For every prime p != 3, we need v_p(sigma(n)) >= v_p(n) = v_p(m).
      - For p = 3, we need v3(sigma(n)) < a, which becomes v3(sigma(m)) < a
        because sigma(3^a) is not divisible by 3.

    We search for all valid m for each a, using backtracking over the allowed primes.
    """
    # max_a with 3^a <= N
    max_a = 0
    t = 3
    while t <= N:
        max_a += 1
        t *= 3

    # powers of 3 up to max_a+1
    pow3 = [1] * (max_a + 2)
    for i in range(1, max_a + 2):
        pow3[i] = pow3[i - 1] * 3

    total = 0
    primes = PRIMES_NO3
    comps_by_prime = COMPONENTS

    for a in range(1, max_a + 1):
        base = pow3[a]
        M = N // base  # m must satisfy m <= M

        # Initial "supply" from sigma(3^a) to cancel primes in m.
        # sigma(3^a) = (3^(a+1)-1)/2
        sigma3 = (pow3[a + 1] - 1) // 2
        init = [0] * P
        tmp = sigma3
        for q in primes:
            if tmp % q == 0:
                c = 0
                while tmp % q == 0:
                    tmp //= q
                    c += 1
                init[P_INDEX[q]] = c

        # For pruning: for each prime index i, compute:
        # - allowed[i]: how many exponents of primes[i] fit within M
        # - max_contrib[i][t]: maximum possible v_{primes[t]}(sigma(primes[i]^e)) over allowed e
        allowed = [0] * P
        max_contrib = [[0] * P for _ in range(P)]

        for i, p in enumerate(primes):
            mx = max_contrib[i]
            k = 0
            for pe, sparse, _c3 in comps_by_prime[p]:
                if pe > M:
                    break
                k += 1
                for idx, val in sparse:
                    if val > mx[idx]:
                        mx[idx] = val
            allowed[i] = k

        # affected[i] = list of t < i where max_contrib[i][t] > 0.
        # When moving from depth i to i+1, only these primes may lose future "potential supply".
        affected = [[] for _ in range(P)]
        for i in range(P):
            row = max_contrib[i]
            affected[i] = [t for t in range(i) if row[t] != 0]

        # remaining[t][pos] = sum_{j>=pos} max_contrib[j][t]
        remaining = [[0] * (P + 1) for _ in range(P)]
        for t_idx in range(P):
            acc = 0
            arr = remaining[t_idx]
            arr[P] = 0
            for pos in range(P - 1, -1, -1):
                acc += max_contrib[pos][t_idx]
                arr[pos] = acc

        demand = [0] * P
        supply = [0] * P

        def dfs(i: int, m: int, v3_sigma_m: int) -> None:
            nonlocal total
            if v3_sigma_m >= a:
                return

            if i == P:
                # At the leaf, remaining[*][P] is 0, so this is the final feasibility check.
                for t_idx in range(P):
                    if demand[t_idx] > init[t_idx] + supply[t_idx]:
                        return
                total += base * m
                return

            p = primes[i]
            comps = comps_by_prime[p]
            M_div = M // m
            old_d = demand[i]

            # Exponent e = 0
            if old_d <= init[i] + supply[i] + remaining[i][i + 1]:
                ok = True
                for t_idx in affected[i]:
                    if (
                        demand[t_idx]
                        > init[t_idx] + supply[t_idx] + remaining[t_idx][i + 1]
                    ):
                        ok = False
                        break
                if ok:
                    dfs(i + 1, m, v3_sigma_m)

            # Exponents e >= 1
            cap = init[i] + supply[i] + remaining[i][i + 1] - old_d
            if cap <= 0:
                return

            max_e = cap
            if max_e > allowed[i]:
                max_e = allowed[i]

            for e in range(1, max_e + 1):
                pe, sparse, c3 = comps[e - 1]
                if pe > M_div:
                    break

                demand[i] = old_d + e
                for idx, val in sparse:
                    supply[idx] += val

                # Feasibility for current prime and for earlier primes affected by moving past index i.
                if demand[i] <= init[i] + supply[i] + remaining[i][i + 1]:
                    ok = True
                    for t_idx in affected[i]:
                        if (
                            demand[t_idx]
                            > init[t_idx] + supply[t_idx] + remaining[t_idx][i + 1]
                        ):
                            ok = False
                            break
                    if ok:
                        dfs(i + 1, m * pe, v3_sigma_m + c3)

                for idx, val in sparse:
                    supply[idx] -= val
                demand[i] = old_d

        dfs(0, 1, 0)

    return total


def main() -> None:
    # Tests from the problem statement
    assert T(100) == 270
    assert T(10**6) == 26089287

    print(T(10**14))


if __name__ == "__main__":
    main()
