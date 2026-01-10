#!/usr/bin/env python3
"""
Project Euler 658: Incomplete Words II

Compute S(10^7, 10^12) mod 1_000_000_007.

No external libraries are used (standard library only).
"""

from array import array

MOD = 1_000_000_007


def I_small(alpha: int, n: int, mod: int = MOD) -> int:
    """
    Direct inclusion-exclusion for I(alpha, n) for small alpha (used for asserts).

    I(alpha,n) = sum_{t=1..alpha} (-1)^{t+1} C(alpha,t) * sum_{l=0..n} (alpha-t)^l
    """
    from math import comb

    res = 0
    for t in range(1, alpha + 1):
        m = alpha - t
        if m == 1:
            g = (n + 1) % mod
        else:
            # g = (m^(n+1) - 1)/(m-1)
            g = (pow(m, n + 1, mod) - 1) * pow(m - 1, mod - 2, mod) % mod
        term = comb(alpha, t) * g
        if t & 1:
            res += term
        else:
            res -= term
    return res % mod


def S_fast(k: int, n: int, mod: int = MOD) -> int:
    """
    O(k) time / O(k) memory solution for S(k,n) = sum_{alpha=1..k} I(alpha,n) (mod mod).

    Works efficiently for k up to 1e7 and n up to 1e12.
    """
    if k <= 0:
        return 0

    limit = k - 1  # m ranges 0..k-1
    e = (n + 1) % (mod - 1)  # Fermat reduction, since bases < mod

    # Modular inverses up to k+1 (needed for term update and for 1/(m-1))
    inv = array("I", [0]) * (k + 2)
    inv[1] = 1
    mmod = mod
    for i in range(2, k + 2):
        inv[i] = (mmod - (mmod // i) * inv[mmod % i] % mmod) % mmod

    # Linear sieve to get smallest prime factor and all x^e mod mod for x<=limit.
    # We compute powe[x] for every x with only one multiplication per composite,
    # and only one pow() call per prime.
    spf = array("I", [0]) * (limit + 1)
    powe = array("I", [0]) * (limit + 1)
    powe[0] = 0
    if limit >= 1:
        powe[1] = 1

    primes = []  # list of primes <= limit
    for i in range(2, limit + 1):
        if spf[i] == 0:
            spf[i] = i
            primes.append(i)
            powe[i] = pow(i, e, mmod)
        pi = powe[i]
        si = spf[i]
        for p in primes:
            v = i * p
            if v > limit:
                break
            spf[v] = p
            powe[v] = (pi * powe[p]) % mmod  # (i*p)^e = i^e * p^e
            if p == si:
                break

    # Now compute:
    #   S(k,n) = sum_{m=0..k-1} G(m) * A(m,k)
    # where G(m)=sum_{l=0..n} m^l, and A(m,k) is a coefficient computed via
    # a binomial-generating-function identity.
    inv2 = (mmod + 1) // 2
    inv2pow = inv2  # 2^{-(m+1)} for m=0
    neg2 = mmod - 2
    k1 = k + 1
    s = 1 if (k & 1) else (mmod - 1)  # s = (-1)^(k+1) in modulo arithmetic

    # T_m = sum_{t=0..m} C(k+1,t) * (-2)^t (prefix), updated in O(1) each step.
    term = 1  # term_0
    T = 1  # T_0
    n1 = (n + 1) % mmod

    ans = 0
    for m in range(0, limit + 1):
        # G(m) = 1 + m + ... + m^n
        if m == 0:
            G = 1
        elif m == 1:
            G = n1
        else:
            G = ((powe[m] - 1) % mmod) * inv[m - 1] % mmod

        # General form:
        #   A(m,k) = 1 - 2^{-(m+1)} * (1 - s*T_m), where s = (-1)^(k+1).
        # For this problem k=10^7 (even) => s = -1 => A = 1 - 2^{-(m+1)}*(1+T_m).
        A = (1 - (inv2pow * ((1 - s * T) % mmod) % mmod)) % mmod
        ans = (ans + G * A) % mmod

        if m == limit:
            break

        # Update term_{m+1} from term_m:
        # term_{m+1} = term_m * (k+1 - m)/(m+1) * (-2)
        term = term * (k1 - m) % mmod
        term = term * inv[m + 1] % mmod
        term = term * neg2 % mmod
        T = (T + term) % mmod

        inv2pow = (inv2pow * inv2) % mmod

    return ans


def _self_test() -> None:
    # Test values from the problem statement
    assert I_small(3, 0) == 1
    assert I_small(3, 2) == 13
    assert I_small(3, 4) == 79

    assert S_fast(4, 4) == 406
    assert S_fast(8, 8) == 27902680
    assert S_fast(10, 100) == 983602076


def main() -> None:
    _self_test()
    print(S_fast(10**7, 10**12))


if __name__ == "__main__":
    main()
