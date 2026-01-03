#!/usr/bin/env python3
"""Project Euler 492 - Exploding Sequence

Compute:
    B(10^9, 10^7, 10^15)

Where:
    a1 = 1
    a_{n+1} = 6*a_n^2 + 10*a_n + 3

    B(x,y,n) = sum(a_n mod p) over primes p with x <= p <= x+y.

All example values from the problem statement are asserted.

No external libraries are used.
"""

from __future__ import annotations

import math
from typing import Iterator, List, Tuple

# After the change of variables u_n = 6*a_n + 5 the recurrence becomes:
#   u_{n+1} = u_n^2 - 2
# and u_n equals a Lucas V-sequence value V_{2^{n-1}} with parameters:
#   P = u_1 = 11, Q = 1.
P = 11

# 117 = 3^2 * 13, so for odd primes p != 3,13:
#   (117/p) = (13/p)
# and because 13 == 1 (mod 4), (13/p) = (p/13).
# Quadratic residues mod 13 are {1,3,4,9,10,12}.
RESIDUES_13 = {1, 3, 4, 9, 10, 12}


def compute_a_exact(n: int) -> int:
    """Compute a_n exactly for small n (used only in asserts)."""
    a = 1
    for _ in range(1, n):
        a = 6 * a * a + 10 * a + 3
    return a


def simple_primes(limit: int) -> List[int]:
    """Return list of all primes <= limit (simple sieve, odd-only)."""
    if limit < 2:
        return []
    size = limit // 2 + 1  # index i represents odd number 2*i+1
    sieve = bytearray(b"\x01") * size
    sieve[0] = 0  # 1 is not prime

    r = int(math.isqrt(limit))
    for p in range(3, r + 1, 2):
        if sieve[p // 2]:
            start = (p * p) // 2
            step = p
            sieve[start::step] = b"\x00" * (((size - 1 - start) // step) + 1)

    primes = [2]
    primes.extend(2 * i + 1 for i in range(1, size) if sieve[i])
    return primes


def segmented_primes(low: int, high: int, base_primes: List[int]) -> Iterator[int]:
    """Yield primes in [low, high] inclusive (segmented sieve, odd-only)."""
    if high < 2 or high < low:
        return

    if low <= 2 <= high:
        yield 2

    start = low | 1  # first odd >= low
    if start > high:
        return

    size = ((high - start) // 2) + 1
    seg = bytearray(b"\x01") * size

    for q in base_primes[1:]:  # skip 2
        qq = q * q
        if qq > high:
            break
        first = qq if qq >= start else ((start + q - 1) // q) * q
        if (first & 1) == 0:
            first += q
        idx = (first - start) // 2
        seg[idx::q] = b"\x00" * (((size - 1 - idx) // q) + 1)

    for i, is_prime in enumerate(seg):
        if is_prime:
            yield start + 2 * i


def lucas_U_pair(n: int, mod: int) -> Tuple[int, int]:
    """Return (U_n, U_{n+1}) mod mod for Lucas parameters P=11, Q=1.

    U_0 = 0, U_1 = 1, U_{k+1} = P*U_k - U_{k-1}.

    Uses an iterative fast-doubling method (O(log n)).
    """
    if n == 0:
        return 0, 1

    u, up1 = 0, 1  # (U_0, U_1)
    mask = 1 << (n.bit_length() - 1)

    while mask:
        # Doubling step: from k to 2k and 2k+1.
        v = (2 * up1 - P * u) % mod  # V_k
        u2k = (u * v) % mod
        u2k1 = (up1 * v - 1) % mod

        if n & mask:
            # Move to (U_{2k+1}, U_{2k+2})
            u2k2 = (P * u2k1 - u2k) % mod
            u, up1 = u2k1, u2k2
        else:
            u, up1 = u2k, u2k1

        mask >>= 1

    return u, up1


def lucas_V(n: int, mod: int) -> int:
    """Return V_n mod mod for Lucas parameters P=11, Q=1.

    V_0 = 2, V_1 = P, V_{k+1} = P*V_k - V_{k-1}.

    Relation with U:
        V_n = 2*U_{n+1} - P*U_n  (valid for Q=1, including n=0)
    """
    u, up1 = lucas_U_pair(n, mod)
    return (2 * up1 - P * u) % mod


def a_mod_prime(n: int, p: int) -> int:
    """Compute a_n mod prime p."""
    if p in (2, 3):
        # 6 is not invertible mod 2 or 3; just iterate directly.
        a = 1 % p
        for _ in range(1, n):
            a = (6 * a * a + 10 * a + 3) % p
        return a

    # Order reduction:
    # Let D = P^2 - 4 = 117. For Q=1 the element alpha has norm 1.
    # In GF(p): if D is a residue, ord(alpha) | (p-1)
    # In GF(p^2): if D is a non-residue, ord(alpha) | (p+1)
    # So V_k (and hence u_n) depends on k modulo M = p - (D/p).
    # Here (D/p) = (13/p) = (p/13) via quadratic reciprocity.
    leg = 1 if (p % 13) in RESIDUES_13 else -1
    m = p - leg  # p-1 if residue, p+1 otherwise

    # u_n = V_{2^{n-1}}; reduce the huge index modulo m.
    e = pow(2, n - 1, m)
    u_n = lucas_V(e, p)

    # Back-transform: a_n = (u_n - 5) / 6 (mod p)
    inv6 = pow(6, -1, p)
    return ((u_n - 5) * inv6) % p


def B(x: int, y: int, n: int, base_primes: List[int]) -> int:
    """Compute B(x,y,n)."""
    total = 0
    for p in segmented_primes(x, x + y, base_primes):
        total += a_mod_prime(n, p)
    return total


def _self_tests(base_primes: List[int]) -> None:
    # Sequence examples
    assert compute_a_exact(3) == 2359
    assert compute_a_exact(6) == 269221280981320216750489044576319

    MOD = 1_000_000_007
    assert a_mod_prime(6, MOD) == 203064689
    assert a_mod_prime(100, MOD) == 456482974

    # B(x,y,n) examples
    assert B(10**9, 10**3, 10**3, base_primes) == 23674718882
    assert B(10**9, 10**3, 10**15, base_primes) == 20731563854


def solve() -> int:
    x = 10**9
    y = 10**7
    n = 10**15

    # One base sieve is enough for all calls (all highs are <= x+y).
    base_limit = int(math.isqrt(x + y)) + 1
    base_primes = simple_primes(base_limit)

    _self_tests(base_primes)
    return B(x, y, n, base_primes)


if __name__ == "__main__":
    print(solve())
