#!/usr/bin/env python3
"""
Project Euler 552: Chinese Leftovers II

Let A_n be the smallest positive integer such that:
    A_n mod p_i = i   for 1 <= i <= n,
where p_i is the i-th prime.

Let S(n) be the sum of all primes <= n that divide at least one A_k.

Compute S(300000).

This program uses only the Python standard library.
"""

from __future__ import annotations

import math
import sys
from typing import List


def primes_up_to(n: int) -> List[int]:
    """Return list of all primes <= n (simple sieve)."""
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    r = int(n**0.5)
    for i in range(2, r + 1):
        if sieve[i]:
            step = i
            start = i * i
            sieve[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i in range(n + 1) if sieve[i]]


def compute_A(k: int) -> int:
    """
    Compute A_k exactly using incremental CRT:

    Maintain (A, P) where P is product of processed primes.
    When adding constraint x ≡ k (mod p_k):
        A' = A + t*P
        t ≡ (k - A) * inv(P mod p_k) (mod p_k)
    """
    if k <= 0:
        raise ValueError("k must be positive")
    # Need first k primes; k=10 is tiny, so just sieve a safe bound.
    # For k <= 10^5, 2*k*log k would be fine; but here we only use small k in tests.
    primes = primes_up_to(1000)
    if len(primes) < k:
        # Fallback (shouldn't trigger for our test sizes).
        bound = 20000
        while True:
            primes = primes_up_to(bound)
            if len(primes) >= k:
                break
            bound *= 2

    A = 0
    P = 1
    for idx in range(1, k + 1):
        p = primes[idx - 1]
        Ap = A % p
        Pp = P % p
        inv = pow(Pp, p - 2, p)  # p is prime
        t = ((idx - Ap) * inv) % p
        A += t * P
        P *= p
    return A


def compute_S(limit: int, block_size: int = 64) -> int:
    """
    Compute S(limit): sum of primes <= limit dividing at least one A_n.

    Key idea:
    - Build A_n incrementally (exact integers A and P).
    - Track A_n modulo many primes at once using blocks:
        For each block we keep:
            M  = product of remaining "eligible" primes in that block,
            aM = A mod M,
            pM = P mod M.
    - At step n with current prime p_n, any primes <= p_n can never divide A_n
      (they are in the constraint list), so we *remove* them from each block
      by dividing M and reducing residues mod the smaller modulus.
    - A prime q divides A_n iff gcd(A mod q, q) == q.
      Inside a block, gcd(aM, M) reveals which primes in that block divide A_n.

    block_size=64 is a good performance sweet spot in Python.
    """
    if limit < 2:
        return 0

    primes = primes_up_to(limit)
    m = len(primes)
    if m <= 1:
        return 0

    # Partition primes into consecutive blocks.
    blocks: List[List[int]] = [
        primes[i : i + block_size] for i in range(0, m, block_size)
    ]
    B = len(blocks)

    # For each block: pointer to first prime still "eligible" (> current p_n),
    # current modulus M = product of eligible primes,
    # residues a_mod = A mod M, P_mod = P mod M.
    ptr = [0] * B
    mod = [1] * B
    a_mod = [0] * B
    P_mod = [1] * B

    for j, bl in enumerate(blocks):
        prod = 1
        for q in bl:
            prod *= q
        mod[j] = prod

    found = bytearray(limit + 1)  # found[q] = 1 if prime q divides some A_n

    A = 0
    P = 1
    gcd = math.gcd  # local alias for speed

    active = list(range(B))  # blocks with mod > 1

    for idx in range(1, m):  # n = 1..m-1 (primes beyond p_n may divide A_n)
        p = primes[idx - 1]

        # Compute update coefficient t for CRT extension.
        Ap = A % p
        Pp = P % p
        inv = pow(Pp, p - 2, p)
        t = ((idx - Ap) * inv) % p

        # Update exact A and P.
        A += t * P
        P *= p

        new_active = []
        for j in active:
            bl = blocks[j]
            k = ptr[j]
            M = mod[j]

            # Shrink: drop all primes <= current p (ineligible now and forever).
            if k < len(bl) and bl[k] <= p:
                while k < len(bl) and bl[k] <= p:
                    M //= bl[k]
                    k += 1
                ptr[j] = k
                mod[j] = M
                if M == 1:
                    continue
                a_mod[j] %= M
                P_mod[j] %= M

            # Update residues mod current M.
            am = (a_mod[j] + t * P_mod[j]) % M
            pm = (P_mod[j] * p) % M
            a_mod[j] = am
            P_mod[j] = pm

            # Detect any prime divisors remaining in this block.
            g = gcd(am, M)
            if g != 1:
                # Because block_size is small, trial dividing by the remaining primes is cheap.
                for q in bl[ptr[j] :]:
                    if g % q == 0:
                        found[q] = 1
                        while g % q == 0:
                            g //= q
                        if g == 1:
                            break

            new_active.append(j)

        active = new_active
        if not active:
            break

    return sum(q for q in primes if found[q])


def _self_test() -> None:
    # Test values explicitly given in the problem statement.
    assert compute_A(2) == 5
    assert compute_A(3) == 23
    assert compute_A(4) == 53
    assert compute_A(5) == 1523
    a10 = compute_A(10)
    assert a10 == 5765999453
    assert a10 % 41 == 0
    assert compute_S(50) == 69


def main() -> None:
    _self_test()
    ans = compute_S(300000)
    print(ans)


if __name__ == "__main__":
    main()
