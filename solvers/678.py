#!/usr/bin/env python3
"""
Project Euler 678: Fermat-like Equations

Count tuples (a,b,c,e,f) such that:
    a^e + b^e = c^f
    0 < a < b
    e >= 2
    f >= 3
    c^f <= N

We compute F(10^18).

High-level approach
-------------------
1) Enumerate all perfect powers n = c^f <= N with f>=3 and store multiplicity mult[n]
   (= number of (c,f) representations with f>=3).

2) e = 2:
   Count representations a^2 + b^2 = n using the sum-of-two-squares theorem:
     r2(n) = 4 * Π_{p≡1 (mod 4)} (E_p + 1),
   provided all primes p≡3 (mod 4) appear with even exponent in n.
   Convert r2(n) (ordered integer representations) to #solutions with 0<a<b.

3) e = 3:
   Use divisor reconstruction from:
     a^3 + b^3 = (a+b)(a^2 - ab + b^2).
   Let s=a+b (a divisor of n). From s we reconstruct (a,b) by checking a discriminant.
   Skip n that are perfect cubes (FLT implies a^3+b^3=d^3 has no positive solutions).

4) e = 4:
   - For n that has some representation with f>=5: brute test sum of two 4th powers by lookup.
   - Additionally, handle the missed case n = c^3 where n is NOT a higher perfect power:
     find all (a,b) with a^4+b^4 being a perfect cube using modular filtering.

5) e >= 5:
   Bounds are small, so brute-force pairs (a,b) and check if a^e+b^e is in mult.

No external libraries are used (only Python stdlib).
"""

import math
from collections import Counter
from typing import Dict, List, Tuple


# ------------------ integer root utilities ------------------


def iroot(n: int, k: int) -> int:
    """Floor integer k-th root of n (n>=0, k>=1)."""
    if n < 2:
        return n
    x = int(round(n ** (1.0 / k)))
    while (x + 1) ** k <= n:
        x += 1
    while x**k > n:
        x -= 1
    return x


# ------------------ sieve / factoring for bases <= N^(1/3) ------------------


def sieve_spf(limit: int) -> List[int]:
    """Smallest prime factor sieve up to limit."""
    spf = list(range(limit + 1))
    r = int(limit**0.5)
    for i in range(2, r + 1):
        if spf[i] == i:
            for j in range(i * i, limit + 1, i):
                if spf[j] == j:
                    spf[j] = i
    return spf


def factorize_small(x: int, spf: List[int]) -> Dict[int, int]:
    """Factorize x <= len(spf)-1 into {prime: exponent} using SPF."""
    fac: Dict[int, int] = {}
    while x > 1:
        p = spf[x]
        cnt = 0
        while x % p == 0:
            x //= p
            cnt += 1
        fac[p] = fac.get(p, 0) + cnt
    return fac


# ------------------ perfect powers enumeration ------------------


def build_perfect_power_mult(N: int) -> Tuple[Counter, Dict[int, Tuple[int, int]], set]:
    """
    Enumerate n=c^f <= N for f>=3.

    Returns:
      mult[n] = number of (c,f) representations (f>=3)
      rep[n]  = one representative (c,f) for factoring n
      has_ge5 = set of n with some representation f>=5 (used for e=4 optimization)
    """
    mult: Counter = Counter()
    rep: Dict[int, Tuple[int, int]] = {}
    has_ge5 = set()

    for f in range(3, 61):
        maxc = iroot(N, f)
        if maxc < 2:
            break
        for c in range(2, maxc + 1):
            n = pow(c, f)
            mult[n] += 1
            if n not in rep:
                rep[n] = (c, f)
            if f >= 5:
                has_ge5.add(n)

    return mult, rep, has_ge5


# ------------------ e=2 counting: sum of two squares ------------------


def count_e2(mult: Counter, rep: Dict[int, Tuple[int, int]], spf: List[int]) -> int:
    """
    Count solutions a^2+b^2=n with 0<a<b, multiplied by mult[n].

    Uses:
      r2(n)=4*Π_{p≡1 mod4}(E_p+1)  if all p≡3 mod4 have even exponent.
    Then:
      #positive a<b = (r2 - axis - diagonal)/8
    """
    isqrt = math.isqrt
    total = 0

    for n, mn in mult.items():
        c, f = rep[n]
        fac_c = factorize_small(c, spf)

        prod = 1
        ok = True
        for p, e in fac_c.items():
            E = e * f
            if (p & 3) == 3 and (E & 1):
                ok = False
                break
            if (p & 3) == 1:
                prod *= E + 1

        if not ok:
            continue

        r2 = 4 * prod

        # axis solutions: (±sqrt(n),0),(0,±sqrt(n))
        sq = isqrt(n)
        axis = 4 if sq * sq == n else 0

        # diagonal solutions: (±t,±t) occurs iff n=2t^2
        if (n & 1) == 0:
            h = n >> 1
            t = isqrt(h)
            diag = 4 if t * t == h else 0
        else:
            diag = 0

        cnt = (r2 - axis - diag) // 8
        total += cnt * mn

    return total


# ------------------ e=3 counting: sum of two cubes via divisors ------------------


def gen_divisors_limited(prime_pows: List[Tuple[int, int]], limit: int) -> List[int]:
    """Generate all divisors <= limit from prime_pows=[(p,exp),...] with pruning."""
    divs = [1]
    for p, e in prime_pows:
        new = []
        pe = 1
        for _ in range(e + 1):
            for d in divs:
                v = d * pe
                if v <= limit:
                    new.append(v)
            pe *= p
            if pe > limit:
                break
        divs = new
    return divs


def prime_pows_of_n(
    n: int, rep: Dict[int, Tuple[int, int]], spf: List[int]
) -> List[Tuple[int, int]]:
    """Return [(p, exponent_in_n)] from rep[n]=(c,f)."""
    c, f = rep[n]
    fac_c = factorize_small(c, spf)
    return [(p, e * f) for p, e in fac_c.items()]


def count_sum_two_cubes_for_n(n: int, prime_pows: List[Tuple[int, int]]) -> int:
    """
    Count a<b, a,b>0 such that a^3+b^3=n.

    Let s=a+b, then s | n. Put q=n/s. Then:
      q = s^2 - 3ab
      D = (4q - s^2)/3 must be a perfect square
      a = (s - sqrt(D))/2, b = (s + sqrt(D))/2
    """
    limit = 2 * iroot(n, 3)
    divs = gen_divisors_limited(prime_pows, limit)
    isqrt = math.isqrt
    cnt = 0

    for s in divs:
        q = n // s
        ss = s * s

        diff = ss - q
        if diff <= 0 or diff % 3:
            continue

        dnum = 4 * q - ss
        if dnum <= 0 or dnum % 3:
            continue

        D = dnum // 3
        r = isqrt(D)
        if r * r != D:
            continue

        if (s - r) & 1:
            continue

        a = (s - r) // 2
        b = (s + r) // 2
        if a > 0 and a < b and a * a * a + b * b * b == n:
            cnt += 1

    return cnt


def count_e3(mult: Counter, rep: Dict[int, Tuple[int, int]], spf: List[int]) -> int:
    """
    For e=3, if n is a perfect cube then a^3+b^3=n implies a^3+b^3=d^3, impossible
    for positive a,b by FLT. So skip cubes.
    """
    total = 0
    for n, mn in mult.items():
        r = iroot(n, 3)
        if r >= 2 and r**3 == n:
            continue
        pp = prime_pows_of_n(n, rep, spf)
        cnt = count_sum_two_cubes_for_n(n, pp)
        if cnt:
            total += cnt * mn
    return total


# ------------------ e=4 counting ------------------


def precompute_pow4(N: int) -> Tuple[List[int], Dict[int, int]]:
    lim = iroot(N, 4)
    pow4 = [i**4 for i in range(1, lim + 1)]
    val_to_base = {v: i + 1 for i, v in enumerate(pow4)}
    return pow4, val_to_base


def count_e4_highpowers(N: int, mult: Counter, has_ge5: set) -> int:
    """
    Count e=4 solutions only for n that has some perfect-power representation with f>=5.
    This set is small; test representability as sum of two 4th powers by lookup.
    """
    pow4, val_to_base = precompute_pow4(N)
    total = 0

    for n in has_ge5:
        mn = mult[n]
        # Skip exact 4th powers (no solutions a^4+b^4=c^4)
        r = iroot(n, 4)
        if r >= 2 and r**4 == n:
            continue

        maxa = iroot(n - 1, 4)
        cnt = 0
        for a in range(1, maxa + 1):
            rem = n - pow4[a - 1]
            b = val_to_base.get(rem)
            if b and b > a:
                cnt += 1

        if cnt:
            total += cnt * mn

    return total


def count_e4_cubes_only(N: int, mult: Counter, excluded: set) -> int:
    """
    Count e=4 solutions where RHS is a perfect cube, but the cube value is NOT in excluded.
    (In this solution, excluded is has_ge5 so we don't double-count.)

    We find all (a,b) with a^4+b^4 being a perfect cube <= N using modular filtering.

    Modulus choice:
      M = 5*7*13*19 = 8645
    This cuts candidate pairs drastically because only ~2.9% of sums of two 4th powers
    can be cubic residues mod M.
    """
    L = iroot(N, 4)
    if L < 2:
        return 0

    M = 8645  # 5*7*13*19

    # cubes mod M
    cube_bool = [False] * M
    for i in range(M):
        cube_bool[pow(i, 3, M)] = True

    # Precompute b^4 and group b by residue r=b^4 mod M
    b4 = [0] * (L + 1)
    res_to_bs: Dict[int, List[int]] = {}
    present_rbs = set()
    for b in range(1, L + 1):
        v = b * b
        v *= v  # b^4
        b4[b] = v
        r = v % M
        res_to_bs.setdefault(r, []).append(b)
        present_rbs.add(r)
    present_rbs = sorted(present_rbs)

    # Precompute a^4 and residue ra=a^4 mod M
    a4 = [0] * (L + 1)
    a_res = [0] * (L + 1)
    r4_occ = set()
    for a in range(1, L + 1):
        v = a * a
        v *= v  # a^4
        a4[a] = v
        r = v % M
        a_res[a] = r
        r4_occ.add(r)

    # For each possible ra, flatten candidate b list that passes the mod filter.
    cand_b_by_ra: Dict[int, List[int]] = {}
    for ra in r4_occ:
        cand: List[int] = []
        for rb in present_rbs:
            if cube_bool[(ra + rb) % M]:
                cand.extend(res_to_bs[rb])
        cand_b_by_ra[ra] = cand

    total = 0
    for a in range(1, L):
        ra = a_res[a]
        va = a4[a]
        cand = cand_b_by_ra[ra]
        for b in cand:
            if b <= a:
                continue
            s = va + b4[b]
            if s > N:
                continue
            c = iroot(s, 3)
            if c * c * c == s and s not in excluded:
                total += mult.get(s, 0)

    return total


def count_e4(N: int, mult: Counter, has_ge5: set) -> int:
    # High perfect powers (f>=5 rep) + cube-only values not covered there.
    return count_e4_highpowers(N, mult, has_ge5) + count_e4_cubes_only(N, mult, has_ge5)


# ------------------ e>=5 brute force ------------------


def count_e_ge5(N: int, mult: Counter) -> int:
    total = 0
    for e in range(5, 61):
        lim = iroot(N, e)
        if lim < 2:
            break
        pows = [pow(i, e) for i in range(1, lim + 1)]
        for i in range(lim - 1):
            pi = pows[i]
            for j in range(i + 1, lim):
                s = pi + pows[j]
                if s > N:
                    break
                total += mult.get(s, 0)
    return total


# ------------------ main solver ------------------


def F(N: int) -> int:
    mult, rep, has_ge5 = build_perfect_power_mult(N)
    spf = sieve_spf(iroot(N, 3))
    return (
        count_e2(mult, rep, spf)
        + count_e3(mult, rep, spf)
        + count_e4(N, mult, has_ge5)
        + count_e_ge5(N, mult)
    )


def main() -> None:
    # Test values given in the problem statement
    assert F(10**3) == 7
    assert F(10**5) == 53
    assert F(10**7) == 287

    print(F(10**18))


if __name__ == "__main__":
    main()
