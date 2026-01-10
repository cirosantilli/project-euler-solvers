#!/usr/bin/env python3
"""
Project Euler 604: Convex Path in Square

We compute F(N): the maximum number of lattice points in an axis-aligned N×N square
that can lie on the graph of a single strictly convex increasing function.

The program prints F(10^18).

No external libraries are used (only Python standard library).
"""

from array import array


def gcd(a: int, b: int) -> int:
    """Greatest common divisor (Euclid)."""
    while b:
        a, b = b, a % b
    return a


def iroot3(n: int) -> int:
    """Floor of the real cube root of n (n >= 0), using integer-only binary search."""
    if n < 0:
        raise ValueError("iroot3() expects n >= 0")

    # Find an upper bound hi with hi^3 > n by doubling.
    lo = 0
    hi = 1
    while hi * hi * hi <= n:
        hi <<= 1

    # Binary search in [lo, hi)
    while lo + 1 < hi:
        mid = (lo + hi) >> 1
        m3 = mid * mid * mid
        if m3 <= n:
            lo = mid
        else:
            hi = mid
    return lo


def sieve_totients(limit: int) -> array:
    """
    Compute phi(0..limit) using a linear sieve in O(limit).

    Returns an array('I') (32-bit unsigned) since phi(k) <= k <= limit fits in 32-bit.
    """
    phi = array("I", [0]) * (limit + 1)
    is_comp = bytearray(limit + 1)
    primes = []

    if limit >= 1:
        phi[1] = 1

    for i in range(2, limit + 1):
        if not is_comp[i]:
            primes.append(i)
            phi[i] = i - 1

        phii = phi[i]
        for p in primes:
            ip = i * p
            if ip > limit:
                break
            is_comp[ip] = 1
            if i % p == 0:
                phi[ip] = phii * p
                break
            else:
                phi[ip] = phii * (p - 1)

    return phi


def can_add_single(sum_s: int, r: int) -> bool:
    """
    After taking as many swapped pairs as possible from layer sum_s = a+b,
    we have remaining budget r in BOTH x and y.

    We can add one more primitive vector (a, sum_s-a) if there exists an a such that:
      1 <= a <= r
      1 <= sum_s-a <= r
      gcd(a, sum_s) = 1

    That is: a in [sum_s - r, r] and gcd(a, sum_s)=1.
    """
    low = sum_s - r
    if low < 1:
        low = 1
    high = r
    if high > sum_s - 1:
        high = sum_s - 1
    if low > high:
        return False

    # Usually we find a coprime very quickly; search from the middle outward.
    mid = (low + high) >> 1
    if gcd(mid, sum_s) == 1:
        return True
    span = high - low
    for d in range(1, span + 1):
        a = mid + d
        if a <= high and gcd(a, sum_s) == 1:
            return True
        a = mid - d
        if a >= low and gcd(a, sum_s) == 1:
            return True
    return False


def F(N: int) -> int:
    """
    Compute F(N).

    Outline:
      - Let s = a+b. Primitive step vectors (a,b) with gcd(a,b)=1 and a,b>0
        exist in count phi(s) for each s (via a and s-a).
      - Taking all primitive vectors with s <= t uses exactly
          X = Y = (1/2) * sum_{s=2..t} s*phi(s)
        lattice width/height, and yields
          V = sum_{s=2..t} phi(s)
        step vectors (so V+1 lattice points).
      - Choose maximal t such that X <= N.
      - Remaining budget is R = N - X in each dimension.
        Any additional vector has s >= t+1, so by total-sum bound:
          k <= floor(2R / (t+1)).
        This is achievable by taking floor(R/(t+1)) swapped pairs (cost (t+1,t+1) each),
        plus possibly one extra single vector if it fits.
    """
    if N < 1:
        return 1  # not needed for this problem, but keeps the function total.

    # A safe initial upper bound: t is ~ (pi^2 N)^(1/3) < (10N)^(1/3) for all N here.
    M = iroot3(10 * N) + 1000
    if M < 10:
        M = 10

    target = 2 * N

    while True:
        # Need phi up to at least M+1 because we'll query t+1.
        phi = sieve_totients(M + 1)

        sum_phi = 0  # sum_{s=2..t} phi(s)
        sum_sphi = 0  # sum_{s=2..t} s*phi(s)
        t = 1
        base_phi = 0
        base_sphi = 0

        # Scan upward until we exceed the budget.
        for s in range(2, M + 1):
            ph = phi[s]
            sum_phi += ph
            sum_sphi += s * ph
            if sum_sphi <= target:
                t = s
                base_phi = sum_phi
                base_sphi = sum_sphi
            else:
                break

        if t < M:
            used_each = base_sphi // 2
            R = N - used_each

            s0 = t + 1  # next (smallest) unused sum a+b
            p = R // s0
            add = 2 * p
            r = R - p * s0  # remaining in each dimension, r < s0

            # Try to add one more vector (odd extra).
            if r > 0 and can_add_single(s0, r):
                add += 1

            # Vectors + 1 starting point = lattice points on the curve.
            return base_phi + add + 1

        # If our bound was too small (rare), double and retry.
        M *= 2


def solve() -> None:
    print(F(10**18))


if __name__ == "__main__":
    # Test values from the problem statement.
    assert F(1) == 2
    assert F(3) == 3
    assert F(9) == 6
    assert F(11) == 7
    assert F(100) == 30
    assert F(50000) == 1898

    solve()
