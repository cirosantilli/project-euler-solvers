#!/usr/bin/env python3
"""Project Euler 592: Factorial trailing digits 2

For any N, let f(N) be the last twelve hexadecimal digits before the trailing
zeroes in N!.

Key idea:
- In base 16, trailing zeroes correspond to factors of 16 = 2^4.
- Write N! = 2^{v2} * odd_part, where odd_part is odd.
- The number of trailing hex zeroes is floor(v2/4). Removing them divides by
  2^{4*floor(v2/4)}, leaving an extra factor 2^{v2 mod 4}.

Therefore:
  f(N) = (odd_part(N!) * 2^{v2(N!) mod 4}) mod 2^{48}
(and printed as 12 hex digits).

The hard part is computing odd_part(N!) modulo 2^{48} for very large N
(here N = 20!).

We use the identity:
  odd_part(n!) = odd_part((n//2)!) * oddprod(n)
where oddprod(n) = product of all odd integers <= n.
Iterating this gives:
  odd_part(n!) = Π_{j>=0} oddprod(n // 2^j)  (until n becomes 0)

So we only need ~log2(n) evaluations of oddprod(x) modulo 2^{48}.

To compute oddprod(x) efficiently, note that it is the product of the first r
odd numbers where r = (x+1)//2, but taken modulo 2^{48}. The odd residues mod
2^{48} repeat with period 2^{47} and their full product is 1, so we reduce r
mod 2^{47}.

The remaining computation is done with 2-adic series on principal units:
- Split each odd (2j+1) into a sign * a unit congruent to 1 (mod 4).
  This makes the log/exp series converge quickly.
- The needed sums of powers over arithmetic progressions are computed using
  Stirling numbers of the second kind and small binomial coefficients.

No external libraries are used.
"""

MOD_BITS = 48
MOD = 1 << MOD_BITS
PERIOD = 1 << (MOD_BITS - 1)  # period of odd residues for the 1,3,5,... sequence


def _v2_int(x: int) -> int:
    """2-adic valuation v2(x) for x>0."""
    return (x & -x).bit_length() - 1


def _comb_small(n: int, k: int) -> int:
    """Exact binomial coefficient C(n,k) for small k (k <= ~60)."""
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    res = 1
    # Multiplicative formula; exact division at each step.
    for i in range(1, k + 1):
        res = res * (n - k + i) // i
    return res


def _precompute_stirling2(max_n: int) -> list[list[int]]:
    """Stirling numbers of the 2nd kind S(n,k) for 0<=n<=max_n."""
    s = [[0] * (max_n + 1) for _ in range(max_n + 1)]
    s[0][0] = 1
    for n in range(1, max_n + 1):
        for k in range(1, n + 1):
            s[n][k] = s[n - 1][k - 1] + k * s[n - 1][k]
    return s


MAX_LOG = 24  # enough because 4^m / m has v2 >= 48 for m >= 25
MAX_EXP = 60  # safe upper bound for exp series when argument is divisible by 4

_STIRLING2 = _precompute_stirling2(MAX_LOG)

_FACT = [1] * (MAX_LOG + 1)
for i in range(1, MAX_LOG + 1):
    _FACT[i] = _FACT[i - 1] * i

# Binomial coefficients for small m used in polynomial expansions
_BINOM = [[0] * (MAX_LOG + 1) for _ in range(MAX_LOG + 1)]
for n in range(MAX_LOG + 1):
    _BINOM[n][0] = _BINOM[n][n] = 1
    for k in range(1, n):
        _BINOM[n][k] = _BINOM[n - 1][k - 1] + _BINOM[n - 1][k]

# Precompute odd parts and v2 of factorials for exp series terms
_FACT_V2 = [0] * (MAX_EXP + 1)
_FACT_ODD_MOD = [1] * (MAX_EXP + 1)  # odd part of n! modulo MOD
for n in range(1, MAX_EXP + 1):
    t = _v2_int(n)
    _FACT_V2[n] = _FACT_V2[n - 1] + t
    _FACT_ODD_MOD[n] = (_FACT_ODD_MOD[n - 1] * (n >> t)) % MOD

_FACT_ODD_INV = [0] * (MAX_EXP + 1)
for n in range(0, MAX_EXP + 1):
    _FACT_ODD_INV[n] = pow(_FACT_ODD_MOD[n], -1, MOD)


def _power_sums_upto(n: int, max_p: int = MAX_LOG) -> list[int]:
    """Return S_p = sum_{i=0}^{n-1} i^p mod MOD for p=0..max_p."""
    # Precompute C(n, k) for k up to max_p+1 (small, exact then mod).
    comb_mod = [0] * (max_p + 2)
    for k in range(1, max_p + 2):
        comb_mod[k] = _comb_small(n, k) % MOD

    sums = [0] * (max_p + 1)
    sums[0] = n % MOD
    for p in range(1, max_p + 1):
        total = 0
        # sum i^p = Σ_{t=0..p} S(p,t) * t! * C(n, t+1)
        for t in range(0, p + 1):
            if _STIRLING2[p][t]:
                total = (
                    total + (_STIRLING2[p][t] * _FACT[t] % MOD) * comb_mod[t + 1]
                ) % MOD
        sums[p] = total
    return sums


def _exp_principal_unit(x: int) -> int:
    """Compute exp(x) modulo 2^48 for x divisible by 4 (principal units).

    Uses the 2-adic exponential series, which converges quickly on 4Z_2.
    """
    x %= MOD
    # exp(0) = 1
    res = 1
    pow_x = 1  # exact integer x^n

    for n in range(1, MAX_EXP + 1):
        pow_x *= x
        v = _FACT_V2[n]
        # term = x^n / n! = (x^n / 2^v) * inv(odd_part(n!))
        shifted = (pow_x >> v) % MOD
        term = (shifted * _FACT_ODD_INV[n]) % MOD
        res = (res + term) % MOD

        # Once the term is 0 modulo MOD, subsequent terms will also be 0
        # for our convergence domain, so we can stop.
        if term == 0:
            break

    return res


# Cache for prod_first_r_odds
_PROD_CACHE: dict[int, int] = {0: 1}


def _prod_first_r_odds(r: int) -> int:
    """Return product_{j=0..r-1} (2j+1) mod 2^48, with r reduced modulo 2^47."""
    r %= PERIOD
    if r in _PROD_CACHE:
        return _PROD_CACHE[r]

    # Split (2j+1) into (-1)^{j} * u_j where u_j == 1 (mod 4):
    # - If j even: u_j = 2j+1.
    # - If j odd:  u_j = -(2j+1) (mod 2^48).
    # Then product = (-1)^{count_odd_j} * Π u_j.
    sign_flip = (r // 2) & 1  # parity of count of odd j in 0..r-1

    E = (r + 1) // 2  # number of even j
    O = r // 2  # number of odd j

    sumsE = _power_sums_upto(E, MAX_LOG)
    sumsO = _power_sums_upto(O, MAX_LOG)

    A = (1 << (MOD_BITS - 2)) - 1  # equals 2^(46) - 1, used for odd-j transform

    # Precompute powers of A up to MAX_LOG
    A_pows = [1] * (MAX_LOG + 1)
    A_mod = A % MOD
    for i in range(1, MAX_LOG + 1):
        A_pows[i] = (A_pows[i - 1] * A_mod) % MOD

    # Compute log(Π u_j) where each u_j = 1 + 4*t_j.
    # log(1+4t) = Σ_{m>=1} (-1)^{m+1} (4t)^m / m.
    log_sum = 0
    for m in range(1, MAX_LOG + 1):
        # sum_t = Σ t_j^m = Σ_{even j} (j/2)^m + Σ_{odd j} (2^(46)-1 - o)^m
        sum_even = sumsE[m]
        # sum_{o=0..O-1} (A - o)^m
        sum_odd = 0
        for t in range(0, m + 1):
            c = _BINOM[m][t]
            term = c * A_pows[m - t]
            if t & 1:
                term = -term
            sum_odd = (sum_odd + term * sumsO[t]) % MOD

        sum_t = (sum_even + sum_odd) % MOD

        # coefficient = (-1)^{m+1} * 4^m / m
        mm = m
        twos = _v2_int(mm)
        odd = mm >> twos
        coef = (1 << (2 * m - twos)) % MOD
        coef = (coef * pow(odd, -1, MOD)) % MOD
        if m % 2 == 0:
            coef = (-coef) % MOD

        log_sum = (log_sum + coef * sum_t) % MOD

    # Now exp(log_sum) gives Π u_j (in the principal unit subgroup)
    prod_u = _exp_principal_unit(log_sum)
    if sign_flip:
        prod_u = (-prod_u) % MOD

    _PROD_CACHE[r] = prod_u
    return prod_u


def _oddprod(n: int) -> int:
    """Product of all odd integers <= n, modulo 2^48."""
    r = (n + 1) // 2
    return _prod_first_r_odds(r)


def _odd_part_factorial_mod(n: int) -> int:
    """Return odd_part(n!) modulo 2^48."""
    res = 1
    while n > 0:
        res = (res * _oddprod(n)) % MOD
        n //= 2
    return res


def f_hex(n: int) -> str:
    """Compute f(n) and return as 12 uppercase hex digits."""
    odd_part = _odd_part_factorial_mod(n)
    # v2(n!) mod 4 = (n - popcount(n)) mod 4
    v2_mod4 = (n - n.bit_count()) & 3
    val = (odd_part * (1 << v2_mod4)) % MOD
    return f"{val:012X}"


def _factorial_small(n: int) -> int:
    res = 1
    for i in range(2, n + 1):
        res *= i
    return res


def solve() -> str:
    n = _factorial_small(20)
    return f_hex(n)


if __name__ == "__main__":
    # Test value from the problem statement.
    assert f_hex(20) == "21C3677C82B4"

    print(solve())
