#!/usr/bin/env python3
"""
Project Euler 550 - Divisor Game

We count winning positions for k piles, each pile size in [2..n], under perfect play.
Answer required modulo 987654321.

Key ideas:
- Sprague-Grundy theorem: position is losing iff XOR of pile nimbers is 0.
- For a pile of size m, its moves depend only on proper divisors of m.
- The nimber depends only on Ω(m) = total number of prime factors of m (with multiplicity).
- Count numbers in [2..n] by Ω using a linear sieve.
- Count k-tuples with XOR=0 via Walsh-Hadamard transform (XOR convolution).
"""

from array import array

MOD = 987654321


def inv_mod(a: int, mod: int = MOD) -> int:
    """Modular inverse of a modulo mod (mod is odd here, so 2^t is invertible)."""
    # Python's pow supports modular inverse for coprime inputs.
    return pow(a, -1, mod)


def fwht_xor(a, mod: int = MOD) -> None:
    """
    In-place Walsh–Hadamard transform for XOR convolution.
    After transform: A[u] = sum_v (-1)^{popcount(u&v)} a[v] (mod mod)
    """
    n = len(a)
    h = 1
    while h < n:
        step = h << 1
        for i in range(0, n, step):
            j_end = i + h
            for j in range(i, j_end):
                x = a[j]
                y = a[j + h]
                a[j] = (x + y) % mod
                a[j + h] = (x - y) % mod
        h = step


def compute_h_sequence(tmax: int):
    """
    h[t] = nimber for any pile with Ω(n)=t.

    Induction:
      - Proper divisors of a number with Ω=t have Ω in {1..t-1}.
      - If nimbers depend only on Ω, then the set of option nimbers is exactly {h[1..t-1]}.
      - Move replaces one pile by two piles => option nimber is xor of two values from that set.
      - Therefore h[t] = mex( {h[i] xor h[j] : 1<=i,j<t} ).

    Since tmax <= 23 for n=1e7, this is tiny.
    """
    if tmax <= 0:
        return [0] * (tmax + 1)

    h = [0] * (tmax + 1)
    h[1] = 0
    prev = [0]  # [h[1], h[2], ..., h[t-1]] as we build

    for t in range(2, tmax + 1):
        reachable = set()
        for a in prev:
            for b in prev:
                reachable.add(a ^ b)
        mex = 0
        while mex in reachable:
            mex += 1
        h[t] = mex
        prev.append(mex)

    return h


def omega_counts_up_to(n: int):
    """
    Count integers m in [2..n] by Ω(m) (total prime factors with multiplicity),
    using a linear sieve.

    Returns: (counts, max_omega)
      counts[t] = how many m in [2..n] have Ω(m)=t
    """
    spf = array("I", [0]) * (n + 1)  # smallest prime factor
    omega = bytearray(n + 1)  # Ω(m) fits in one byte for n<=1e7
    primes = []

    counts = [0] * 32  # enough for n<=1e7 (max Ω is 23)
    max_om = 0

    spf_local = spf
    omega_local = omega
    primes_append = primes.append
    counts_local = counts

    for i in range(2, n + 1):
        si = spf_local[i]
        if si == 0:
            spf_local[i] = i
            primes_append(i)
            omega_local[i] = 1
            si = i
            oi = 1
        else:
            oi = omega_local[i]

        counts_local[oi] += 1
        if oi > max_om:
            max_om = oi

        for p in primes:
            ip = i * p
            if ip > n:
                break
            spf_local[ip] = p
            omega_local[ip] = oi + 1
            if p == si:
                break

    return counts_local, max_om


def f(n: int, k: int, mod: int = MOD) -> int:
    """Compute f(n,k) modulo mod."""
    omega_counts, max_om = omega_counts_up_to(n)
    h = compute_h_sequence(max_om)

    max_g = 0
    for t in range(1, max_om + 1):
        if h[t] > max_g:
            max_g = h[t]

    size = 1 << (max_g.bit_length())  # power of two >= max_g+1
    vec = [0] * size
    for t in range(1, max_om + 1):
        vec[h[t]] += omega_counts[t]
    vec = [v % mod for v in vec]

    fwht_xor(vec, mod)

    s = 0
    for v in vec:
        s = (s + pow(v, k, mod)) % mod

    losing = s * inv_mod(size, mod) % mod
    total = pow(n - 1, k, mod)  # (n-1) choices per pile: sizes 2..n
    return (total - losing) % mod


def main() -> None:
    # Test value from the problem statement
    assert f(10, 5) == 40085

    print(f(10_000_000, 10**12))


if __name__ == "__main__":
    main()
