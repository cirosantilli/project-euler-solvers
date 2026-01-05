#!/usr/bin/env python3
"""
Project Euler 495
W(n, k): number of ways to write n as the product of k distinct positive integers.
Compute W(10000!, 30) mod 1_000_000_007.

No external libraries are used.
"""

from array import array
import math

MOD = 1_000_000_007


# ----------------------------
# Prime sieve + factorial exponents
# ----------------------------


def sieve_primes_upto(n: int) -> list[int]:
    """Simple bytearray sieve."""
    if n < 2:
        return []
    bs = bytearray(b"\x01") * (n + 1)
    bs[0:2] = b"\x00\x00"
    lim = int(math.isqrt(n))
    for i in range(2, lim + 1):
        if bs[i]:
            step = i
            start = i * i
            bs[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i in range(n + 1) if bs[i]]


def factorial_prime_exponent_frequencies(n: int) -> dict[int, int]:
    """
    Returns a map exponent -> how many primes p have v_p(n!) == exponent.
    Uses Legendre's formula: v_p(n!) = sum_{t>=1} floor(n/p^t).
    """
    primes = sieve_primes_upto(n)
    freq: dict[int, int] = {}
    for p in primes:
        e = 0
        nn = n
        while nn:
            nn //= p
            e += nn
        freq[e] = freq.get(e, 0) + 1
    return freq


# ----------------------------
# Integer partitions of k (cycle types)
# ----------------------------


def partitions_of(n: int, max_part: int | None = None):
    """
    Generates integer partitions of n as non-increasing lists.
    Count for n=30 is 5604 (small enough to enumerate).
    """
    if max_part is None or max_part > n:
        max_part = n
    if n == 0:
        yield []
        return
    for first in range(max_part, 0, -1):
        for rest in partitions_of(n - first, first):
            yield [first] + rest


# ----------------------------
# Core solver
# ----------------------------


def precompute_base_ones_twos(max_e: int, k: int) -> list[list[array]]:
    """
    For speed, precompute coefficient arrays for generating functions:
      (1 - x)^(-r1) * (1 - x^2)^(-r2)
    for all 0<=r1<=k and 0<=r2<=floor(k/2).

    Stored as array('I') to keep memory low; per partition we convert to list
    and continue DP for parts >= 3.
    """
    # modular inverses up to max_e for binomial sequence of (1-x)^(-r1)
    inv = [0] * (max_e + 1)
    if max_e >= 1:
        inv[1] = 1
        for i in range(2, max_e + 1):
            inv[i] = MOD - (MOD // i) * inv[MOD % i] % MOD

    ones = [None] * (k + 1)
    ones[0] = [0] * (max_e + 1)
    ones[0][0] = 1
    for r1 in range(1, k + 1):
        dp = [0] * (max_e + 1)
        dp[0] = 1
        # dp[t] = C(r1+t-1, t) mod MOD
        for t in range(1, max_e + 1):
            dp[t] = (dp[t - 1] * (r1 + t - 1) % MOD) * inv[t] % MOD
        ones[r1] = dp

    base: list[list[array]] = [[None] * (k // 2 + 1) for _ in range(k + 1)]
    for r1 in range(k + 1):
        base[r1][0] = array("I", ones[r1])
        for r2 in range(1, k // 2 + 1):
            dp = list(base[r1][r2 - 1])
            # multiply by (1-x^2)^(-1) once: dp[t] += dp[t-2]
            for t in range(2, max_e + 1):
                x = dp[t] + dp[t - 2]
                if x >= MOD:
                    x -= MOD
                dp[t] = x
            base[r1][r2] = array("I", dp)
    return base


def W_from_factorial_freq(freq: dict[int, int], k: int) -> int:
    """
    Computes W(n,k) mod MOD where n is described by exponent frequencies:
      freq[e] = number of primes with exponent e in n.

    Uses the signed cycle-index / inclusion-exclusion over permutations.
    """
    if k == 0:
        return 1

    exponents = sorted(freq.keys())
    max_e = max(exponents) if exponents else 0
    exp_freq = [(e, freq[e]) for e in exponents]

    # weight precomputation: inv_fact and inv_pow[s][cnt] for s<=k, cnt<=k
    fact = [1] * (k + 1)
    for i in range(1, k + 1):
        fact[i] = fact[i - 1] * i % MOD

    inv_fact = [1] * (k + 1)
    inv_fact[k] = pow(fact[k], MOD - 2, MOD)
    for i in range(k, 0, -1):
        inv_fact[i - 1] = inv_fact[i] * i % MOD

    inv_pow = [[1] * (k + 1) for _ in range(k + 1)]
    for s in range(1, k + 1):
        invs = pow(s, MOD - 2, MOD)
        acc = 1
        for c in range(1, k + 1):
            acc = (acc * invs) % MOD
            inv_pow[s][c] = acc

    # DP bases for common 1- and 2-cycles
    base = precompute_base_ones_twos(max_e, k)

    total = 0
    freq1 = freq.get(1, 0)

    for parts in partitions_of(k):
        # parts describes cycle lengths; length(parts) = number of cycles
        b = len(parts)

        # count trailing 1s and 2s (parts are non-increasing so 1s/2s appear at the end)
        r1 = r2 = 0
        i = b - 1
        while i >= 0 and parts[i] == 1:
            r1 += 1
            i -= 1
        while i >= 0 and parts[i] == 2:
            r2 += 1
            i -= 1

        # If n has primes with exponent 1, any term without (1-x)^(-r1) has coeff[x^1]=0 => contributes 0.
        if r1 == 0 and freq1:
            continue

        rem_parts = parts[: i + 1]  # cycle lengths >= 3

        # Build coefficient array for P(x)=∏ (1-x^{m})^{-1} up to degree max_e
        dp = list(base[r1][r2])  # dp[t] = [x^t] (1-x)^(-r1) (1-x^2)^(-r2)
        for m in rem_parts:
            # multiply by (1-x^m)^(-1): unbounded knapsack update dp[t] += dp[t-m]
            for t in range(m, max_e + 1):
                x = dp[t] + dp[t - m]
                if x >= MOD:
                    x -= MOD
                dp[t] = x

        # f(parts) = ∏_p [x^{a_p}] P(x) = ∏_e dp[e]^{freq[e]}
        fval = 1
        for e, fe in exp_freq:
            c = dp[e]
            if c == 0:
                fval = 0
                break
            if fe == 1:
                fval = (fval * c) % MOD
            else:
                if c != 1:
                    fval = (fval * pow(c, fe, MOD)) % MOD
        if fval == 0:
            continue

        # weight(parts) = (-1)^{k-b} / ∏ (s^{b_s} * b_s!)
        w = 1
        j = 0
        while j < b:
            s = parts[j]
            jj = j + 1
            while jj < b and parts[jj] == s:
                jj += 1
            cnt = jj - j
            w = (w * inv_pow[s][cnt]) % MOD
            w = (w * inv_fact[cnt]) % MOD
            j = jj
        if (k - b) & 1:
            w = MOD - w

        total = (total + w * fval) % MOD

    return total


def solve() -> int:
    n = 10000
    k = 30
    freq = factorial_prime_exponent_frequencies(n)
    return W_from_factorial_freq(freq, k)


# ----------------------------
# Tests from the statement
# ----------------------------


def _test():
    # W(144,4) = 7
    assert W_from_factorial_freq({4: 1, 2: 1}, 4) == 7

    # W(100!, 10) = 287549200
    freq100 = factorial_prime_exponent_frequencies(100)
    assert W_from_factorial_freq(freq100, 10) == 287549200


if __name__ == "__main__":
    _test()
    print(solve())
