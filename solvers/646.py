#!/usr/bin/env python3
"""
Project Euler 646 - Bounded Divisors

We need:
  S(n, L, H) = sum_{d | n, L <= d <= H} lambda(d) * d
where lambda is Liouville: lambda(n)=(-1)^{Omega(n)} and Omega counts prime factors with multiplicity.

For this problem n = 70!, L=10^20, H=10^60, answer mod 1_000_000_007.

No external libraries are used.
"""

from bisect import bisect_right
from math import isqrt

MOD = 1_000_000_007


def sieve_primes(n: int) -> list[int]:
    """Simple sieve of Eratosthenes up to n (inclusive)."""
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


def factorial_prime_exponents(n: int) -> tuple[list[int], dict[int, int]]:
    """Return primes <= n and exponent of each prime in n!."""
    primes = sieve_primes(n)
    exps: dict[int, int] = {}
    for p in primes:
        e = 0
        m = n
        while m:
            m //= p
            e += m
        exps[p] = e
    return primes, exps


def choose_store_subset(
    primes: list[int], exps: dict[int, int], max_store: int
) -> list[int]:
    """
    Choose a subset of primes whose divisor-count product (∏(e_p+1)) is:
      - <= max_store (memory constraint),
      - <= its complement size (so we store the smaller side),
      - as close as possible to sqrt(total_divisors) (roughly balances work).
    Brute force over up to 2^19 masks for n<=70.
    """
    eplus = [exps[p] + 1 for p in primes]
    total = 1
    for v in eplus:
        total *= v
    target = isqrt(total)

    m = len(primes)
    best_diff = None
    best_mask = 0

    for mask in range(1 << m):
        prod = 1
        for i in range(m):
            if (mask >> i) & 1:
                prod *= eplus[i]
                if prod > max_store:
                    break
        else:
            comp = total // prod
            if prod > comp:
                continue
            diff = prod - target
            if diff < 0:
                diff = -diff
            if best_diff is None or diff < best_diff:
                best_diff = diff
                best_mask = mask

    return [primes[i] for i in range(m) if (best_mask >> i) & 1]


def precompute_powers(p: int, e: int, mod: int | None):
    """
    Precompute:
      pow_val[k]  = p^k (positive integer)
      pow_coef[k] = (-p)^k  (mod M if mod provided, else exact integer)
    Note: f(d)=lambda(d)*d is completely multiplicative and f(p^k)=(-p)^k.
    """
    pow_val = [1] * (e + 1)
    pow_coef = [1] * (e + 1)
    if mod is None:
        for k in range(1, e + 1):
            pow_val[k] = pow_val[k - 1] * p
            pow_coef[k] = pow_coef[k - 1] * (-p)
    else:
        negp = (mod - (p % mod)) % mod
        for k in range(1, e + 1):
            pow_val[k] = pow_val[k - 1] * p
            pow_coef[k] = (pow_coef[k - 1] * negp) % mod
    return pow_val, pow_coef


def gen_divisors_lists(primes: list[int], exps: dict[int, int], mod: int | None):
    """
    Generate all divisors from the given prime set.

    Returns parallel lists:
      vals[i]  = divisor value (positive integer)
      coefs[i] = f(divisor) where f(d)=lambda(d)*d, modded if mod != None
    """
    vals = [1]
    coefs = [1]
    for p in primes:
        e = exps[p]
        pow_val, pow_coef = precompute_powers(p, e, mod)

        new_vals = []
        new_coefs = []
        append_v = new_vals.append
        append_c = new_coefs.append

        if mod is None:
            for v, c in zip(vals, coefs):
                for pv, pc in zip(pow_val, pow_coef):
                    append_v(v * pv)
                    append_c(c * pc)
        else:
            for v, c in zip(vals, coefs):
                for pv, pc in zip(pow_val, pow_coef):
                    append_v(v * pv)
                    append_c((c * pc) % mod)

        vals, coefs = new_vals, new_coefs

    return vals, coefs


def split_loop_base(
    iter_primes: list[int], exps: dict[int, int], base_limit: int = 200_000
):
    """
    Split iter_primes into:
      - loop_primes: a few primes with largest (e+1),
      - base_primes: the rest,
    such that product_{p in base_primes}(e_p+1) <= base_limit.

    This keeps the stored 'base' list small, and enumerates the remaining combinations
    via nested loops.
    """
    factors = sorted(((exps[p] + 1, p) for p in iter_primes), reverse=True)
    total = 1
    for f, _ in factors:
        total *= f

    base_count = total
    loop = []
    base = set(iter_primes)

    for f, p in factors:
        if base_count <= base_limit:
            break
        loop.append(p)
        base.remove(p)
        base_count //= f

    base_primes = sorted(base)
    loop_primes = sorted(loop, key=lambda p: exps[p] + 1, reverse=True)
    return base_primes, loop_primes


def bounded_divisor_sum_factorial(
    n: int, L: int, H: int, mod: int | None = None, max_store: int = 1_200_000
):
    """
    Compute S(n!, L, H) = sum_{d|n!, L<=d<=H} lambda(d)*d.
    If mod is provided, result is modulo mod.

    Technique: meet-in-the-middle on prime factors of n!
      - split primes into STORE and ITER groups
      - precompute all STORE divisors b sorted with prefix sums of f(b)
      - iterate all ITER divisors a and use:
          sum_{a} f(a) * (sum_{b<=H/a} f(b) - sum_{b< L/a} f(b))
        (implemented as sum_{b<=H/a} - sum_{b<= (L-1)/a})
    """
    primes, exps = factorial_prime_exponents(n)
    store_primes = choose_store_subset(primes, exps, max_store=max_store)
    store_set = set(store_primes)
    iter_primes = [p for p in primes if p not in store_set]

    # Build STORE divisors (b) + prefix sums of f(b)
    b_vals, b_coefs = gen_divisors_lists(store_primes, exps, mod)
    pairs = list(zip(b_vals, b_coefs))
    pairs.sort(key=lambda t: t[0])

    b_vals = [v for v, _ in pairs]

    if mod is None:
        prefix = [0]
        s = 0
        for _, c in pairs:
            s += c
            prefix.append(s)
    else:
        prefix = [0]
        s = 0
        for _, c in pairs:
            s = (s + c) % mod
            prefix.append(s)

    # Split ITER primes to speed enumeration
    base_primes, loop_primes = split_loop_base(iter_primes, exps, base_limit=200_000)
    base_vals, base_coefs = gen_divisors_lists(base_primes, exps, mod)

    loop_pow = [precompute_powers(p, exps[p], mod) for p in loop_primes]

    x_low = L - 1
    bis = bisect_right

    def pref(limit: int):
        return prefix[bis(b_vals, limit)]

    # Enumerate
    if mod is None:
        total = 0
        lp = len(loop_pow)

        if lp == 0:
            for v, c in zip(base_vals, base_coefs):
                total += c * (pref(H // v) - pref(x_low // v))
        elif lp == 1:
            pv1, pc1 = loop_pow[0]
            for bv, bc in zip(base_vals, base_coefs):
                for p1, c1 in zip(pv1, pc1):
                    v = bv * p1
                    c = bc * c1
                    total += c * (pref(H // v) - pref(x_low // v))
        elif lp == 2:
            pv1, pc1 = loop_pow[0]
            pv2, pc2 = loop_pow[1]
            for bv, bc in zip(base_vals, base_coefs):
                for p1, c1 in zip(pv1, pc1):
                    v1 = bv * p1
                    c1b = bc * c1
                    for p2, c2 in zip(pv2, pc2):
                        v = v1 * p2
                        c = c1b * c2
                        total += c * (pref(H // v) - pref(x_low // v))
        else:
            # Fallback for >=3 loop primes (won't happen for n<=70 with current limits)
            def rec(idx: int, v: int, c: int):
                nonlocal total
                if idx == lp:
                    total += c * (pref(H // v) - pref(x_low // v))
                    return
                pvs, pcs = loop_pow[idx]
                for pv, pc in zip(pvs, pcs):
                    rec(idx + 1, v * pv, c * pc)

            for bv, bc in zip(base_vals, base_coefs):
                rec(0, bv, bc)

        return total

    # modded version
    M = mod
    total = 0
    lp = len(loop_pow)

    if lp == 0:
        for v, c in zip(base_vals, base_coefs):
            d = pref(H // v) - pref(x_low // v)
            total = (total + c * (d % M)) % M
    elif lp == 1:
        pv1, pc1 = loop_pow[0]
        for bv, bc in zip(base_vals, base_coefs):
            for p1, c1 in zip(pv1, pc1):
                v = bv * p1
                coef = (bc * c1) % M
                d = pref(H // v) - pref(x_low // v)
                total = (total + coef * (d % M)) % M
    elif lp == 2:
        pv1, pc1 = loop_pow[0]
        pv2, pc2 = loop_pow[1]
        for bv, bc in zip(base_vals, base_coefs):
            for p1, c1 in zip(pv1, pc1):
                v1 = bv * p1
                c1b = (bc * c1) % M
                for p2, c2 in zip(pv2, pc2):
                    v = v1 * p2
                    coef = (c1b * c2) % M
                    d = pref(H // v) - pref(x_low // v)
                    total = (total + coef * (d % M)) % M
    else:

        def rec(idx: int, v: int, c: int):
            nonlocal total
            if idx == lp:
                d = pref(H // v) - pref(x_low // v)
                total = (total + c * (d % M)) % M
                return
            pvs, pcs = loop_pow[idx]
            for pv, pc in zip(pvs, pcs):
                rec(idx + 1, v * pv, (c * pc) % M)

        for bv, bc in zip(base_vals, base_coefs):
            rec(0, bv, bc % M)

    return total % M


def main() -> None:
    # Test values given in the problem statement:
    assert bounded_divisor_sum_factorial(10, 100, 1000, mod=None) == 1457
    assert bounded_divisor_sum_factorial(15, 10**3, 10**5, mod=None) == -107974
    assert bounded_divisor_sum_factorial(30, 10**8, 10**12, mod=None) == 9766732243224

    # Required answer:
    ans = bounded_divisor_sum_factorial(70, 10**20, 10**60, mod=MOD)
    print(ans)


if __name__ == "__main__":
    main()
