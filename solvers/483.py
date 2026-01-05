#!/usr/bin/env python3
"""
Project Euler 483: Repeated Permutation

We define f(P) as the order of a permutation P (the smallest m>0 such that P^m = identity),
and g(n) as the average of f(P)^2 over all permutations of size n.

This program computes g(350) and prints it in scientific notation with 10 significant digits.

No external libraries are used (only Python standard library).
The exact example fractions in the statement are verified with asserts.

Important implementation notes:
- Uses the exponential generating function for permutations by cycle lengths:
    Product_{k>=1} exp(x^k / k)
  and a DP that tracks total size and the LCM of chosen cycle lengths.
- Speeds up LCM tracking by encoding LCM prime-exponent vectors into a compact bitmask,
  where LCM becomes bitwise OR.
"""

from fractions import Fraction
import math


# -----------------------------
# Small exact solver (for asserts)
# -----------------------------
def lcm(a: int, b: int) -> int:
    return a // math.gcd(a, b) * b


def g_exact(n: int) -> Fraction:
    """
    Exact computation of g(n) using Fractions (only feasible for small n).
    DP over cycle lengths k with multiplicity a_k, tracking size and integer lcm.
    """
    dp = [dict() for _ in range(n + 1)]
    dp[0][1] = Fraction(1, 1)

    for k in range(1, n + 1):
        # coefficient for choosing a cycles of length k: 1 / (k^a * a!)
        maxa = n // k
        coeff = [Fraction(1, 1)]
        c = Fraction(1, 1)
        for a in range(1, maxa + 1):
            c /= k * a
            coeff.append(c)

        new = [d.copy() for d in dp]
        for size in range(n + 1):
            if not dp[size]:
                continue
            maxa2 = (n - size) // k
            if maxa2 == 0:
                continue
            for L, w in dp[size].items():
                newL = lcm(L, k)
                if newL == L:
                    for a in range(1, maxa2 + 1):
                        ns = size + a * k
                        new[ns][L] = new[ns].get(L, Fraction(0, 1)) + w * coeff[a]
                else:
                    for a in range(1, maxa2 + 1):
                        ns = size + a * k
                        new[ns][newL] = new[ns].get(newL, Fraction(0, 1)) + w * coeff[a]
        dp = new

    total = Fraction(0, 1)
    for L, w in dp[n].items():
        total += w * (L * L)
    return total


# -----------------------------
# Prime-mask LCM representation
# -----------------------------
def build_prime_masks(n: int):
    """
    Returns:
      masks[k] = bitmask encoding prime-power content of k
      prime_info = list of (p, emax, offset)
    Encoding rule:
      For prime p with max exponent emax, we reserve emax bits at some offset.
      If number has exponent e, we set the lowest e bits in that block.
      Then LCM corresponds to bitwise OR.
    """
    spf = list(range(n + 1))
    for i in range(2, int(n**0.5) + 1):
        if spf[i] == i:
            step = i
            start = i * i
            for j in range(start, n + 1, step):
                if spf[j] == j:
                    spf[j] = i

    primes = [i for i in range(2, n + 1) if spf[i] == i]

    prime_info = []
    offset = 0
    pinfo = {}
    for p in primes:
        emax = 0
        t = p
        while t <= n:
            emax += 1
            t *= p
        prime_info.append((p, emax, offset))
        pinfo[p] = (emax, offset)
        offset += emax

    masks = [0] * (n + 1)
    masks[1] = 0
    for m in range(2, n + 1):
        x = m
        mask = 0
        while x > 1:
            p = spf[x]
            e = 0
            while x % p == 0:
                x //= p
                e += 1
            _, off = pinfo[p]
            mask |= ((1 << e) - 1) << off
        masks[m] = mask

    return masks, prime_info


def mask_to_value(mask: int, prime_info, cache: dict) -> int:
    """
    Decode mask back into integer LCM value.
    Uses cache to avoid recomputation.
    """
    v = cache.get(mask)
    if v is not None:
        return v
    val = 1
    for p, emax, off in prime_info:
        block = (mask >> off) & ((1 << emax) - 1)
        e = block.bit_count()
        if e:
            val *= p**e
    cache[mask] = val
    return val


# -----------------------------
# Fast approximate solver for n=350
# -----------------------------
def g_fast(n: int) -> float:
    """
    Computes g(n) using float DP with LCM masks.
    """
    masks, prime_info = build_prime_masks(n)

    dp = [dict() for _ in range(n + 1)]
    dp[0][0] = 1.0  # mask=0 represents LCM=1

    for k in range(2, n + 1):
        kmask = masks[k]
        inv_k = 1.0 / k

        dp2 = dp[:]  # lazy copy-on-write per size
        copied = [False] * (n + 1)

        def ensure(i: int):
            if not copied[i] and dp2[i] is dp[i]:
                dp2[i] = dp[i].copy()
                copied[i] = True
            return dp2[i]

        for size in range(n + 1):
            d = dp[size]
            if not d:
                continue
            if size + k > n:
                continue

            for Lmask, w in d.items():
                newmask = Lmask | kmask

                # add contributions for a >= 1 cycles of length k
                term = w * inv_k
                a = 1
                ns = size + k
                target = Lmask if newmask == Lmask else newmask
                while ns <= n:
                    dd = ensure(ns)
                    dd[target] = dd.get(target, 0.0) + term
                    a += 1
                    term *= inv_k / a
                    ns += k

        dp = dp2

    # Include 1-cycles by convolving with exp(x) => coefficient 1/(m!) for m fixed points
    inv_fact = [1.0] * (n + 1)
    f = 1.0
    for i in range(1, n + 1):
        f *= i
        inv_fact[i] = 1.0 / f

    dist = {}
    for size in range(n + 1):
        d = dp[size]
        if not d:
            continue
        factor = inv_fact[n - size]
        for Lmask, w in d.items():
            dist[Lmask] = dist.get(Lmask, 0.0) + w * factor

    # Expected value: sum_{mask} prob(mask) * L(mask)^2
    val_cache = {}
    total = 0.0
    for m, prob in dist.items():
        L = mask_to_value(m, prime_info, val_cache)
        total += (L * L) * prob

    return total


def format_sci(x: float) -> str:
    """
    10 significant digits scientific notation (as in statement).
    """
    return "{:.9e}".format(x)


def main():
    # --- Asserts from the problem statement ---
    assert g_exact(3) == Fraction(31, 6)
    assert g_exact(5) == Fraction(2081, 120)
    assert g_exact(20) == Fraction(12422728886023769167301, 2432902008176640000)

    # --- Required output ---
    ans = g_fast(350)
    print(format_sci(ans))


if __name__ == "__main__":
    main()
