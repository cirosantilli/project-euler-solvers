#!/usr/bin/env python3
"""Project Euler 619 - Square Subsets

For the integer interval {a, a+1, ..., b}, define C(a,b) as the number of
non-empty subsets whose product is a perfect square.

This program prints:
    C(1_000_000, 1_234_567) mod 1_000_000_007

No external libraries are used.
"""

MOD = 1_000_000_007


def primes_upto(n: int) -> list[int]:
    """Return all primes <= n using a bytearray sieve."""
    if n < 2:
        return []
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[0:2] = b"\x00\x00"
    import math

    limit = math.isqrt(n)
    for i in range(2, limit + 1):
        if sieve[i]:
            start = i * i
            step = i
            sieve[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)

    return [i for i in range(n + 1) if sieve[i]]


def sieve_spf_linear(n: int) -> list[int]:
    """Smallest-prime-factor sieve in O(n) time (linear sieve)."""
    spf = [0] * (n + 1)
    primes: list[int] = []
    for i in range(2, n + 1):
        if spf[i] == 0:
            spf[i] = i
            primes.append(i)
        si = spf[i]
        for p in primes:
            v = i * p
            if v > n:
                break
            spf[v] = p
            if p == si:
                break
    spf[0] = spf[1] = 1
    return spf


def C(a: int, b: int, mod: int = MOD) -> int:
    """Compute C(a,b) mod `mod`."""
    import math

    m = b - a + 1

    # Split primes into:
    #   small primes <= T where T = floor(sqrt(b))
    #   big primes  > T
    # For any n <= b, its squarefree kernel contains at most one big prime.
    T = math.isqrt(b)
    small_primes = primes_upto(T)

    # Map each small prime to a bit in an integer mask.
    small_bit = [0] * (T + 1)
    for idx, p in enumerate(small_primes):
        small_bit[p] = 1 << idx

    spf = sieve_spf_linear(b)

    # For each big prime p, store the first observed small-mask (pivot).
    pivot_small_mask: dict[int, int] = {}

    # Basis for the "small" subspace (dimension <= pi(T) ~ 200), maintained incrementally.
    basis: dict[int, int] = {}
    rank_small = 0

    def add_small_vector(v: int) -> None:
        """Insert v into the GF(2) basis if it is linearly independent."""
        nonlocal rank_small
        while v:
            lb = v & -v
            bvec = basis.get(lb)
            if bvec is None:
                basis[lb] = v
                rank_small += 1
                return
            v ^= bvec

    for n in range(a, b + 1):
        x = n
        small_mask = 0
        big_prime = 0

        # Factor x using spf, tracking exponent parity for each prime.
        while x > 1:
            p = spf[x]
            x //= p
            parity = 1
            while x % p == 0:
                x //= p
                parity ^= 1
            if parity:
                if p <= T:
                    small_mask ^= small_bit[p]
                else:
                    # There can be only one such prime when using T = floor(sqrt(b)).
                    big_prime = p

        if big_prime == 0:
            add_small_vector(small_mask)
        else:
            prev = pivot_small_mask.get(big_prime)
            if prev is None:
                pivot_small_mask[big_prime] = small_mask
            else:
                # Eliminate the big prime column: (e_p + prev) XOR (e_p + small_mask)
                # = prev XOR small_mask, a purely-small vector.
                add_small_vector(prev ^ small_mask)

    rank = len(pivot_small_mask) + rank_small
    # #subsets mapping to zero under XOR = 2^(m-rank). Exclude empty subset.
    return (pow(2, m - rank, mod) - 1) % mod


def main() -> None:
    # Test values from the problem statement
    assert C(5, 10) == 3
    assert C(40, 55) == 15
    assert C(1000, 1234) == 975523611

    print(C(1_000_000, 1_234_567))


if __name__ == "__main__":
    main()
