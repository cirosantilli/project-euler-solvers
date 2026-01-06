#!/usr/bin/env python3
"""
Project Euler 536 - Modulo Power Identity

Let S(n) be the sum of all positive integers m <= n such that:
    a^(m+4) ≡ a (mod m)  for all integers a.

Key reduction:
- m must be squarefree
- for each prime p|m we must have (p-1) | (m+3)
So equivalently, for squarefree m:
    lcm(p-1 for p|m) | (m+3)

We compute S(10^12) via a DFS + congruence pruning strategy.

No external libraries are used.
"""

from math import gcd, isqrt


def sieve_primes(limit: int):
    """Return list of primes <= limit using a bytearray sieve."""
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    r = isqrt(limit)
    for p in range(2, r + 1):
        if sieve[p]:
            step = p
            start = p * p
            sieve[start:limit + 1:step] = b"\x00" * (((limit - start) // step) + 1)
    return [i for i in range(limit + 1) if sieve[i]]


def lcm(a: int, b: int) -> int:
    return a // gcd(a, b) * b


def factor_squarefree(n: int, primes):
    """
    Factor n using trial division by primes.
    Return list of prime factors if squarefree, else None.
    """
    factors = []
    tmp = n
    for p in primes:
        pp = p * p
        if pp > tmp:
            break
        if tmp % p == 0:
            tmp //= p
            if tmp % p == 0:
                return None  # not squarefree
            factors.append(p)
    if tmp > 1:
        factors.append(tmp)
    return factors


def S(N: int) -> int:
    """
    Compute S(N): sum of all m <= N satisfying the identity for all integers a.
    """
    # Prime solutions: m=2,3,5 (and m=1) are included automatically by the DFS check,
    # but we seed 1 and 2 for convenience.
    solutions = set([1])
    if N >= 2:
        solutions.add(2)

    # We only need primes up to sqrt(N) for trial division / branching
    limit = isqrt(N)
    primes = sieve_primes(limit)
    odd_primes = [p for p in primes if p != 2]

    # DFS state:
    # A  = product of chosen primes ("kernel")
    # L  = lcm(p-1 for p|A)
    #
    # Any completion A*R must satisfy:
    #    A*R ≡ -3 (mod L)
    #
    # Let g = gcd(A, L). Solvable iff g | 3.
    # Then modulo reduces to M = L/g, and R must lie in one residue class mod M.
    #
    # When the number of candidates for R in that class becomes small,
    # we enumerate them directly and factor-check them.
    #
    THRESHOLD = 7000  # tuning constant; balances branching vs enumeration

    def dfs(min_idx: int, A: int, L: int):
        # If A itself already satisfies constraints for its primes, record it.
        if (A + 3) % L == 0:
            solutions.add(A)

        g = gcd(A, L)
        if 3 % g != 0:
            return

        maxR = N // A
        if maxR == 0:
            return

        M = L // g
        count = maxR // M + 1

        # If the arithmetic progression for R is short enough, enumerate.
        if M != 1 and count <= THRESHOLD:
            A1 = (A // g) % M
            rhs = (-3 // g) % M
            invA = pow(A1, -1, M)  # modular inverse in C, fast
            T = (rhs * invA) % M

            r = T if T > 0 else M
            min_p = odd_primes[min_idx] if min_idx < len(odd_primes) else None

            while r <= maxR:
                if gcd(r, A) == 1:
                    fac = factor_squarefree(r, primes)
                    if fac is not None and fac:
                        if (min_p is None) or (fac[0] >= min_p):
                            n = A * r
                            np3 = n + 3
                            ok = True
                            for p in fac:
                                if np3 % (p - 1) != 0:
                                    ok = False
                                    break
                            if ok:
                                solutions.add(n)
                r += M
            return

        # Otherwise expand the kernel by trying larger primes.
        for idx in range(min_idx, len(odd_primes)):
            p = odd_primes[idx]
            newA = A * p
            if newA > N:
                break
            newL = lcm(L, p - 1)
            if 3 % gcd(newA, newL) != 0:
                continue
            dfs(idx + 1, newA, newL)

    dfs(0, 1, 1)
    return sum(x for x in solutions if x <= N)


def main():
    # Problem statement test values:
    assert S(100) == 32
    assert S(10**6) == 22868117

    print(S(10**12))


if __name__ == "__main__":
    main()

