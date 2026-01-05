#!/usr/bin/env python3
"""
Project Euler 421: Prime Factors of n^15 + 1

We need:
  sum_{n=1..L} s(n, M)
where s(n, M) is the sum of distinct prime factors of n^15 + 1 not exceeding M,
with L = 10^11 and M = 10^8.

No external libraries are used (stdlib only).
"""

from __future__ import annotations

from math import isqrt


# ---------------------------
# Small helpers for asserts
# ---------------------------


def _primes_upto_small(limit: int) -> list[int]:
    """Simple sieve for small limits (used only for problem-statement asserts)."""
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    r = isqrt(limit)
    for p in range(2, r + 1):
        if sieve[p]:
            start = p * p
            sieve[start : limit + 1 : p] = b"\x00" * ((limit - start) // p + 1)
    return [i for i in range(limit + 1) if sieve[i]]


def _s_statement(n: int, m: int) -> int:
    """Compute s(n,m) directly by checking divisibility by primes <= m (small m in asserts)."""
    val = pow(n, 15) + 1
    total = 0
    for p in _primes_upto_small(m):
        if val % p == 0:
            total += p
    return total


# Problem statement examples (must be asserts)
assert _s_statement(2, 10) == 3
assert _s_statement(2, 1000) == 345
assert _s_statement(10, 100) == 31
assert _s_statement(10, 1000) == 483


# ---------------------------
# Prime generation up to 1e8
# ---------------------------


def iter_odd_primes_upto(limit: int):
    """
    Yield all odd primes <= limit using an odd-only sieve.

    Index i represents the odd number (2*i + 1).
    The sieve length is (limit+1)//2 so we never represent an odd > limit.
    """
    if limit < 3:
        return
    size = (limit + 1) // 2  # odds: 1,3,5,...,(limit if odd else limit-1)
    sieve = bytearray(b"\x01") * size
    sieve[0] = 0  # 1 is not prime

    r = isqrt(limit)
    for i in range(1, (r // 2) + 1):
        if sieve[i]:
            p = 2 * i + 1
            start = (p * p) // 2  # index of p^2
            sieve[start::p] = b"\x00" * (((size - start - 1) // p) + 1)

    idx = sieve.find(1, 1)  # start at 3
    while idx != -1:
        yield 2 * idx + 1
        idx = sieve.find(1, idx + 1)


# ---------------------------
# Generator finding for d in {3,5,15}
# ---------------------------

_SMALL_BASES = (
    2,
    3,
    5,
    7,
    11,
    13,
    17,
    19,
    23,
    29,
    31,
    37,
    41,
    43,
    47,
    53,
    59,
    61,
    67,
    71,
    73,
    79,
    83,
    89,
    97,
)


def _is_order_15(g: int, p: int) -> bool:
    """Return True iff g has exact order 15 modulo prime p (assuming g^15 == 1)."""
    if g == 1:
        return False
    g2 = (g * g) % p
    g3 = (g2 * g) % p
    if g3 == 1:
        return False  # order divides 3
    g4 = (g2 * g2) % p
    g5 = (g4 * g) % p
    if g5 == 1:
        return False  # order divides 5
    return True  # remaining possibility is 15


def find_generator_of_subgroup(p: int, d: int) -> int:
    """
    Find an element of exact order d in the subgroup {u: u^15 == 1}.

    d is one of {3,5,15}. We compute g = a^((p-1)/d) for small a until it has order d.
    This is fast in practice; the probability that a random a works is sizeable.
    """
    exp = (p - 1) // d

    # Try a curated list of small prime bases first.
    for a in _SMALL_BASES:
        if a >= p:
            break
        g = pow(a, exp, p)
        if d == 3:
            if g != 1:
                return g
        elif d == 5:
            if g != 1:
                return g
        else:  # d == 15
            if _is_order_15(g, p):
                return g

    # Deterministic fallback: scan upwards a bit further (still cheap).
    # This avoids rare failures where the curated bases are unlucky.
    upper = min(p, 500)  # small cap; should be enough in practice
    for a in range(2, upper):
        g = pow(a, exp, p)
        if d == 3:
            if g != 1:
                return g
        elif d == 5:
            if g != 1:
                return g
        else:
            if _is_order_15(g, p):
                return g

    raise RuntimeError(f"Failed to find generator of order {d} for p={p}")


# ---------------------------
# Main solver
# ---------------------------


def solve(L: int = 10**11, M: int = 10**8) -> int:
    """
    Compute sum_{n=1..L} s(n, M).

    Identity:
      sum_{n<=L} s(n,M) = sum_{p<=M} p * #{n<=L : p | (n^15+1)}

    For odd primes p, solutions to n^15 ≡ -1 (mod p) are:
      n ≡ -u (mod p) for each u satisfying u^15 ≡ 1 (mod p).

    The number of 15th roots of unity is d = gcd(15, p-1) ∈ {1,3,5,15},
    determined for primes ≥ 7 solely by p mod 30.
    """
    # d lookup by p % 30 (valid for all primes > 2)
    d_table = [1] * 30
    d_table[1] = 15
    d_table[11] = 5
    d_table[7] = d_table[13] = d_table[19] = 3

    divmod_ = divmod

    ans = 0

    # Prime 2: n^15+1 is even iff n is odd.
    if M >= 2:
        ans += 2 * ((L + 1) // 2)

    for p in iter_odd_primes_upto(M):
        d = d_table[p % 30]
        q, t = divmod_(L, p)

        if d == 1:
            # Only solution is n ≡ -1 (mod p), i.e. residue p-1.
            cnt = q + (1 if t == p - 1 else 0)
            ans += p * cnt
            continue

        g = find_generator_of_subgroup(p, d)

        # Residues are r = (-u mod p) = p-u for u in subgroup.
        # In the last partial block 1..t, count residues r <= t.
        # r = p-u <= t  <=>  u >= p-t.
        threshold = p - t
        u = 1
        extra = 0
        for _ in range(d):
            if u >= threshold:
                extra += 1
            u = (u * g) % p

        cnt = d * q + extra
        ans += p * cnt

    return ans


def main() -> None:
    print(solve())


if __name__ == "__main__":
    main()
