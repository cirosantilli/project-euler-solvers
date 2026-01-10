#!/usr/bin/env python3
"""
Project Euler 636 - Restricted Factorisations

We count representations of n! of the form:

    a^1 * b1^2 * b2^2 * c1^3 * c2^3 * c3^3 * d1^4 * d2^4 * d3^4 * d4^4

where all base numbers (a, b1, b2, c1, c2, c3, d1..d4) are pairwise distinct,
and order within equal-exponent groups is not distinguished.

We compute a labelled count with inclusion–exclusion (bases distinct),
then divide by 2!*3!*4! to account for indistinguishable permutations
inside equal-exponent groups.
"""

import math
from collections import defaultdict, Counter

MOD = 1_000_000_007

# Slot weights (exponents) for the 10 factors:
#   1x (power 1), 2x squares, 3x cubes, 4x fourth powers
SLOT_WEIGHTS = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
TOTAL_WEIGHT = sum(SLOT_WEIGHTS)  # 30


# --------------------------
# Prime sieve and valuations
# --------------------------


def primes_upto(n: int):
    """Return list of primes <= n using a bytearray sieve."""
    sieve = bytearray(b"\x01") * (n + 1)
    sieve[:2] = b"\x00\x00"
    r = int(math.isqrt(n))
    for i in range(2, r + 1):
        if sieve[i]:
            step = i
            start = i * i
            sieve[start : n + 1 : step] = b"\x00" * (((n - start) // step) + 1)
    return [i for i in range(n + 1) if sieve[i]]


def factorial_prime_exp(n: int, p: int) -> int:
    """v_p(n!) via Legendre formula."""
    e = 0
    while n:
        n //= p
        e += n
    return e


def exponent_frequencies_factorial(n: int, primes):
    """Return Counter{ exponent -> number of primes with that exponent in n! }."""
    freq = Counter()
    for p in primes:
        if p > n:
            break
        e = factorial_prime_exp(n, p)
        freq[e] += 1
    return freq


# ---------------------------------------
# Set partitions (for inclusion–exclusion)
# ---------------------------------------


def gen_partitions(n: int):
    """
    Generate all set partitions of {0..n-1}.
    Standard recursive construction; n=10 so it's fine.
    """

    def helper(i, blocks):
        if i == n:
            yield [b[:] for b in blocks]
            return
        # put i in existing blocks
        for b in blocks:
            b.append(i)
            yield from helper(i + 1, blocks)
            b.pop()
        # put i in a new block
        blocks.append([i])
        yield from helper(i + 1, blocks)
        blocks.pop()

    yield from helper(0, [])


def build_partition_coefficients():
    """
    For each partition, Möbius coefficient is:

        mu(π) = Π_{blocks B} (-1)^{|B|-1} (|B|-1)!

    The prime-wise solution count depends only on the multiset of
    block-weight-sums, so we aggregate mu over identical keys.
    """
    coeff = defaultdict(int)

    for blocks in gen_partitions(10):
        mu = 1
        sums = []
        for b in blocks:
            s = len(b)
            mu *= (-1) ** (s - 1) * math.factorial(s - 1)
            wsum = 0
            for idx in b:
                wsum += SLOT_WEIGHTS[idx]
            sums.append(wsum)
        key = tuple(sorted(sums))
        coeff[key] += mu

    return coeff


# --------------------------
# Small coefficient generation
# --------------------------


def coeffs_up_to(key, limit):
    """
    Coefficients of:
        prod_{w in key} 1/(1-x^w)
    up to x^limit, via "coin-change" DP.
    """
    dp = [0] * (limit + 1)
    dp[0] = 1
    for w in key:
        for i in range(w, limit + 1):
            v = dp[i] + dp[i - w]
            if v >= MOD:
                v -= MOD
            dp[i] = v
    return dp


# --------------------------
# Polynomial recurrence tools
# --------------------------

D = 30  # Always 30 because sum of weights is 30.


def poly_Q_from_key(key):
    """
    Q(x) = Π (1 - x^w), degree 30.
    Stored as integer list q[0..30] (not reduced mod yet).
    """
    q = [0] * (TOTAL_WEIGHT + 1)
    q[0] = 1
    for w in key:
        for i in range(TOTAL_WEIGHT - w, -1, -1):
            q[i + w] -= q[i]
    return q


def mul_mod_poly(a, b, r):
    """
    Multiply two degree<30 polynomials in the quotient ring defined by:
        x^30 = r1*x^29 + r2*x^28 + ... + r30
    where recurrence is:
        A[n] = r1*A[n-1] + ... + r30*A[n-30]
    """
    tmp = [0] * (2 * D - 1)  # length 59
    # convolution
    for i in range(D):
        ai = a[i]
        if ai:
            for j in range(D):
                tmp[i + j] = (tmp[i + j] + ai * b[j]) % MOD
    # reduction from degree 58 down to 30
    for k in range(2 * D - 2, D - 1, -1):
        coef = tmp[k]
        if coef:
            # coef*x^k = coef*x^{k-30}*x^30
            # substitute x^30 and distribute into lower degrees
            for i in range(1, D + 1):
                tmp[k - i] = (tmp[k - i] + coef * r[i - 1]) % MOD
    return tmp[:D]


def precompute_powers_of_x(r, maxbit=20):
    """
    Precompute polys for x^(2^b) mod characteristic, b=0..maxbit-1.
    """
    pow_polys = [[0] * D for _ in range(maxbit)]
    pow_polys[0][1] = 1  # x
    for b in range(1, maxbit):
        pow_polys[b] = mul_mod_poly(pow_polys[b - 1], pow_polys[b - 1], r)
    return pow_polys


def poly_x_n(pow_polys, n, r):
    """Compute x^n mod characteristic using precomputed powers."""
    res = [0] * D
    res[0] = 1  # x^0
    bit = 0
    while n:
        if n & 1:
            res = mul_mod_poly(res, pow_polys[bit], r)
        n >>= 1
        bit += 1
    return res


def term_from_poly(init, poly):
    """Given init[0..29], compute sum(poly[i]*init[i])."""
    s = 0
    for ci, ai in zip(poly, init):
        s = (s + ci * ai) % MOD
    return s


# --------------------------
# Main computation F(n!)
# --------------------------


def compute_F_factorial(n: int, primes, coeff_dict, cutoff=13_000) -> int:
    """
    Compute F(n!) mod MOD.

    Uses:
    - inclusion–exclusion over set partitions (aggregated into keys)
    - for each key, coefficient extraction per prime exponent:
        #solutions of sum(w_i * x_i) = e
    - DP up to cutoff, recurrence for larger e.
    """
    freq = exponent_frequencies_factorial(n, primes)
    inv288 = pow(288, MOD - 2, MOD)  # 2!*3!*4!

    exps_sorted = sorted(freq)
    max_exp = exps_sorted[-1]

    use_cutoff = min(cutoff, max_exp)
    large_exps = [e for e in exps_sorted if e > use_cutoff]

    # If exponent=1 occurs (it does for all n>=5), keys without 1 contribute 0.
    if freq.get(1, 0):
        keys = [k for k in coeff_dict if 1 in k]
    else:
        keys = list(coeff_dict.keys())

    items = list(freq.items())

    total = 0
    maxbit = 20  # since max exponent < 2^20 for n<=1e6

    for key in keys:
        # DP up to cutoff gives coefficients for small exponents and init[0..29]
        dp = coeffs_up_to(key, use_cutoff)

        large_vals = None
        if large_exps:
            q = poly_Q_from_key(key)
            # r_i = -q[i] mod MOD for i=1..30
            r = [(-q[i]) % MOD for i in range(1, TOTAL_WEIGHT + 1)]
            pow_polys = precompute_powers_of_x(r, maxbit=maxbit)
            init = dp[:D] + [0] * max(0, D - len(dp))
            large_vals = {}
            for e in large_exps:
                poly = poly_x_n(pow_polys, e, r)
                large_vals[e] = term_from_poly(init, poly)

        prod = 1
        for e, cnt in items:
            if e <= use_cutoff:
                val = dp[e]
            else:
                val = large_vals[e]
            if val == 0:
                prod = 0
                break
            prod = (prod * pow(val, cnt, MOD)) % MOD

        if prod:
            total = (total + (coeff_dict[key] % MOD) * prod) % MOD

    return (total * inv288) % MOD


def main():
    # Precomputation shared for all test cases
    coeff_dict = build_partition_coefficients()

    # prime list up to 1,000,000
    primes = primes_upto(1_000_000)

    # ---- Asserts from the problem statement ----
    assert compute_F_factorial(25, primes, coeff_dict, cutoff=2000) == 4933
    assert compute_F_factorial(100, primes, coeff_dict, cutoff=5000) == 693_952_493
    assert compute_F_factorial(1000, primes, coeff_dict, cutoff=20_000) == 6_364_496

    # ---- Required final result ----
    ans = compute_F_factorial(1_000_000, primes, coeff_dict, cutoff=13_000)
    print(ans)


if __name__ == "__main__":
    main()
