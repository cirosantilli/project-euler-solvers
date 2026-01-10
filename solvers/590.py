#!/usr/bin/env python3
"""Project Euler 590: Sets with a Given Least Common Multiple

Compute HL(50000) = H(L(50000)) modulo 1e9.

No external libraries are used.
"""

from __future__ import annotations

from collections import defaultdict
from math import gcd

MOD = 10**9
MOD2 = 2**9  # 512
MOD5 = 5**9  # 1_953_125
PHI5 = 4 * 5**8  # phi(5^9) = 1_562_500


def lcm(a: int, b: int) -> int:
    """Least common multiple."""
    return a // gcd(a, b) * b


def sieve(limit: int) -> list[int]:
    """Simple bytearray sieve."""
    if limit < 2:
        return []
    is_prime = bytearray(b"\x01") * (limit + 1)
    is_prime[0:2] = b"\x00\x00"
    p = 2
    while p * p <= limit:
        if is_prime[p]:
            step = p
            start = p * p
            is_prime[start : limit + 1 : step] = b"\x00" * (
                ((limit - start) // step) + 1
            )
        p += 1
    return [i for i in range(limit + 1) if is_prime[i]]


def max_power_exponent(p: int, n: int) -> int:
    """Return the largest e such that p**e <= n (for prime p)."""
    e = 1
    pp = p
    while pp * p <= n:
        pp *= p
        e += 1
    return e


def factorize(n: int) -> list[tuple[int, int]]:
    """Trial-division factorization (sufficient for tiny n in asserts)."""
    res = []
    d = 2
    while d * d <= n:
        if n % d == 0:
            e = 0
            while n % d == 0:
                n //= d
                e += 1
            res.append((d, e))
        d += 1 if d == 2 else 2  # 2 then odd numbers
    if n > 1:
        res.append((n, 1))
    return res


def H_small(n: int) -> int:
    """Compute H(n) exactly for small n via inclusion-exclusion over its primes.

    For n > 1:
      H(n) = sum_{A subset of primes(n)} (-1)^|A| * 2^{d(n / prod_{p in A} p)}

    Special case: H(1) = 1 (only set {1}).
    """
    if n == 1:
        return 1

    factors = factorize(n)
    primes = [p for p, _ in factors]
    exps = [e for _, e in factors]
    k = len(primes)

    total = 0
    for mask in range(1 << k):
        bits = 0
        divcount = 1
        for i in range(k):
            if (mask >> i) & 1:
                bits += 1
                divcount *= exps[i]  # exponent reduced by 1 => (e-1)+1 = e
            else:
                divcount *= exps[i] + 1
        term = 1 << divcount  # 2^divcount
        if bits & 1:
            total -= term
        else:
            total += term
    return total


def HL_small(n: int) -> int:
    """Compute HL(n) exactly for small n."""
    L = 1
    for i in range(1, n + 1):
        L = lcm(L, i)
    return H_small(L)


def binom_coeffs_signed_mod(n: int, mod: int) -> list[int]:
    """Return [(-1)^(n-k) * C(n,k) mod mod] for k=0..n."""
    coeffs = [0] * (n + 1)
    c = 1  # C(n,0)
    for k in range(n + 1):
        if ((n - k) & 1) == 0:
            coeffs[k] = c % mod
        else:
            coeffs[k] = (-c) % mod
        if k != n:
            c = c * (n - k) // (k + 1)
    return coeffs


def group_terms(
    exponent: int, count: int, mod_phi: int, mod_w: int
) -> list[tuple[int, int]]:
    """For a prime-exponent group with exponent=a and size=count, build all choices.

    Selecting t primes into the squarefree divisor q contributes:
      weight: (-1)^t * C(count,t)
      multiplier in x=d(m/q): a^t * (a+1)^(count-t)

    Returned as (multiplier mod mod_phi, weight mod mod_w) for t=0..count.
    """
    out: list[tuple[int, int]] = []
    c = 1  # C(count,0)
    for t in range(count + 1):
        mul = (
            pow(exponent, t, mod_phi) * pow(exponent + 1, count - t, mod_phi)
        ) % mod_phi
        w = c
        if t & 1:
            w = -w
        out.append((mul, w % mod_w))
        if t != count:
            c = c * (count - t) // (t + 1)
    return out


def eval_F_r(x_mod_phi: int, coeffs: list[int]) -> int:
    """Compute F_r(x) modulo 5^9.

    For r exponent-1 primes:
      F_r(x) = sum_{k=0..r} (-1)^(r-k) * C(r,k) * 2^{x*2^k}

    We evaluate 2^{x*2^k} by repeated squaring:
      p0 = 2^x, p_{k+1} = p_k^2.
    """
    mod = MOD5
    p = pow(2, x_mod_phi, mod)
    acc = 0
    # Reduce acc occasionally to avoid big integers.
    for i, ck in enumerate(coeffs):
        acc += ck * p
        if (i & 63) == 63:
            acc %= mod
        p = (p * p) % mod
    return acc % mod


def HL_50000() -> int:
    """Compute HL(50000) mod 1e9 using the specialized method."""
    N = 50000
    primes = sieve(N)

    # Exponents in L(N): for each prime p <= N, exponent a is max with p^a <= N.
    r = 0  # number of primes with exponent 1
    counts: dict[int, int] = defaultdict(
        int
    )  # exponent a>=2 -> how many primes have that exponent
    for p in primes:
        a = max_power_exponent(p, N)
        if a == 1:
            r += 1
        else:
            counts[a] += 1

    # Assert that modulo 2^9 every term vanishes (exponent >= 9), so result ≡ 0 (mod 512).
    # The minimal exponent among all 2^{d(...)} terms occurs when all exponent-1 primes are "removed"
    # and each exponent>=2 prime is also "removed" (giving factor a rather than a+1), hence prod(a).
    min_divcount = 1
    for a, c in counts.items():
        for _ in range(c):
            min_divcount *= a
            if min_divcount >= 9:
                break
        if min_divcount >= 9:
            break
    assert min_divcount >= 9

    # DP over exponent-groups (only a few) to accumulate weights for each x = d(m/q) modulo PHI5.
    dist: dict[int, int] = {1: 1}  # x_mod_phi -> weight mod MOD5
    for a in sorted(counts):
        c = counts[a]
        terms = group_terms(a, c, PHI5, MOD5)
        new: dict[int, int] = defaultdict(int)
        for x_prev, w_prev in dist.items():
            for mul, w in terms:
                new_x = (x_prev * mul) % PHI5
                new[new_x] = (new[new_x] + w_prev * w) % MOD5
        dist = new

    coeffs = binom_coeffs_signed_mod(r, MOD5)  # (-1)^(r-k) C(r,k)

    total_mod5 = 0
    for x_mod, w in dist.items():
        if w:
            total_mod5 = (total_mod5 + w * eval_F_r(x_mod, coeffs)) % MOD5

    # Combine residues: x ≡ 0 (mod 512) and x ≡ total_mod5 (mod 5^9) via CRT.
    inv_512 = pow(MOD2, -1, MOD5)
    t = (total_mod5 * inv_512) % MOD5
    return (MOD2 * t) % MOD


def main() -> None:
    # Test values from the problem statement:
    assert H_small(6) == 10
    assert HL_small(4) == 44

    print(HL_50000())


def solve() -> int:
    """Convenience hook for some runners."""
    return HL_50000()


if __name__ == "__main__":
    main()
