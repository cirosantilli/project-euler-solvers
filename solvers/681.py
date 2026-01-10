#!/usr/bin/env python3
"""
Project Euler 681: Maximal Area

We use Brahmagupta's formula for cyclic quadrilaterals:
  Area^2 = (s-a)(s-b)(s-c)(s-d)

Let U = s-a, V = s-b, W = s-c, T = s-d (all positive).
Then maximal area is sqrt(U*V*W*T).

If a<=b<=c<=d then U>=V>=W>=T.

Perimeter a+b+c+d = 2s = U+V+W+T.

So for each integer area k:
  U*V*W*T = k^2
  U>=V>=W>=T>=1
  U < V+W+T      (equivalently smallest side > 0)
  perimeter even (to ensure a,b,c,d are integers)

We sum p = U+V+W+T over all such solutions with k <= n.
"""

from math import isqrt


def build_spf(limit: int):
    """Smallest prime factor sieve up to 'limit'."""
    spf = list(range(limit + 1))
    for i in range(2, isqrt(limit) + 1):
        if spf[i] == i:
            step = i
            start = i * i
            for j in range(start, limit + 1, step):
                if spf[j] == j:
                    spf[j] = i
    return spf


def factorize(n: int, spf):
    """Return prime factorization of n as list of (p, exp)."""
    out = []
    while n > 1:
        p = spf[n]
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        out.append((p, e))
    return out


def divisors_of_k2_upto_k(k: int, fac):
    """
    Generate all divisors d of k^2 such that d <= k.
    Returned list is sorted ascending.

    If k = Π p^e, then k^2 has exponents 2e.
    """
    divs = [1]
    for p, e in fac:
        # powers: p^0..p^(2e)
        powers = [1]
        pe = 1
        for _ in range(2 * e):
            pe *= p
            powers.append(pe)

        new_vals = []
        # Multiply existing divisors by each positive power, prune by <= k
        for d in divs:
            for pw in powers[1:]:
                v = d * pw
                if v > k:
                    break
                new_vals.append(v)
        if new_vals:
            divs += new_vals

    divs.sort()
    # No duplicates should occur in this construction.
    return divs


def sp(n: int) -> int:
    """
    Compute SP(n).
    """
    spf = build_spf(n)
    total = 0

    for k in range(1, n + 1):
        k2 = k * k
        fac = factorize(k, spf)
        divs = divisors_of_k2_upto_k(k, fac)
        dlen = len(divs)

        for ti in range(dlen):
            T = divs[ti]
            k2_div_T = k2 // T

            for wi in range(ti, dlen):
                W = divs[wi]

                # Need T*W | k^2
                if W > k2_div_T:
                    break
                if k2_div_T % W:
                    continue

                R = k2_div_T // W  # R = k^2/(T*W)
                vmax = isqrt(R)
                if vmax < W:
                    continue
                if vmax > k:
                    vmax = k

                S = W + T  # shorthand
                # Use quadratic bound from U < V+W+T:
                # U = R/V, require R/V < V + S -> R < V(V+S)
                disc = S * S + (R << 2)
                root = isqrt(disc)
                vmin = (root - S) // 2 + 1
                if vmin < W:
                    vmin = W
                if vmin > vmax:
                    continue

                # find first index in divs >= vmin
                lo, hi = 0, dlen
                while lo < hi:
                    mid = (lo + hi) >> 1
                    if divs[mid] < vmin:
                        lo = mid + 1
                    else:
                        hi = mid

                for vi in range(lo, dlen):
                    V = divs[vi]
                    if V > vmax:
                        break
                    if R % V:
                        continue

                    U = R // V
                    if U < V:
                        continue
                    if U >= V + S:
                        continue

                    p = U + V + S  # since S=W+T
                    if p & 1:
                        continue

                    total += p

    return total


def main():
    # Given test values in the statement
    assert sp(10) == 186
    assert sp(100) == 23238

    print(sp(1_000_000))


if __name__ == "__main__":
    main()
