#!/usr/bin/env python3
"""
Project Euler 440: GCD and Tiling

We tile a 1×n board with:
- 1×2 dominoes (1 type)
- 1×1 monominoes labeled with a decimal digit (10 types)

Let T(n) be the number of tilings.
Define S(L) = sum_{1<=a,b,c<=L} gcd(T(c^a), T(c^b)).

We compute S(2000) mod 987898789.
"""

from math import gcd

MOD = 987_898_789
P = 10  # recurrence parameter
TARGET_L = 2000


# -------------------------
# Small exact checks (from the statement)
# -------------------------
def _tilings_T_up_to(max_n: int) -> list[int]:
    # T(0)=1 (empty), T(1)=10, T(n)=10*T(n-1)+T(n-2)
    T = [0] * (max_n + 1)
    T[0] = 1
    if max_n >= 1:
        T[1] = 10
    for n in range(2, max_n + 1):
        T[n] = 10 * T[n - 1] + T[n - 2]
    return T


def _S_bruteforce(L: int) -> int:
    max_n = 0
    for c in range(1, L + 1):
        x = 1
        for _ in range(L):
            x *= c
            if x > max_n:
                max_n = x

    T = _tilings_T_up_to(max_n)

    total = 0
    for a in range(1, L + 1):
        for b in range(1, L + 1):
            for c in range(1, L + 1):
                total += gcd(T[c**a], T[c**b])
    return total


def _run_statement_asserts() -> None:
    assert _S_bruteforce(2) == 10444
    assert _S_bruteforce(3) == 1292115238446807016106539989
    assert _S_bruteforce(4) % MOD == 670616280


# -------------------------
# Main fast solver
# -------------------------
def _mobius_upto(n: int) -> list[int]:
    """Linear sieve for Möbius mu(1..n)."""
    mu = [0] * (n + 1)
    mu[1] = 1
    primes: list[int] = []
    is_comp = [False] * (n + 1)

    for i in range(2, n + 1):
        if not is_comp[i]:
            primes.append(i)
            mu[i] = -1
        for p in primes:
            ip = i * p
            if ip > n:
                break
            is_comp[ip] = True
            if i % p == 0:
                mu[ip] = 0
                break
            mu[ip] = -mu[i]
    return mu


def _counts_N_and_rest(L: int) -> tuple[list[int], int]:
    """
    For each g, let N[g] be the number of ordered pairs (a,b) with:
      1<=a,b<=L, gcd(a,b)=g, and (a/g) and (b/g) are both odd.

    Then for fixed c, pairs not counted in N contribute gcd(...) = 1 (c even) or 2 (c odd),
    hence a small constant Lucas term.

    Returns (N, rest) where rest = L^2 - sum_g N[g].
    """
    mu = _mobius_upto(L)

    # f(n) = #{(x,y): 1<=x,y<=n, x,y odd, gcd(x,y)=1}
    # f(n) = sum_{d odd<=n} mu(d) * ((floor(n/d)+1)//2)^2
    f = [0] * (L + 1)
    for n in range(1, L + 1):
        s = 0
        for d in range(1, n + 1, 2):  # odd d only
            md = mu[d]
            if md:
                t = (n // d + 1) // 2  # number of odd multiples of d up to n
                s += md * t * t
        f[n] = s

    N = [0] * (L + 1)
    sumN = 0
    for g in range(1, L + 1):
        v = f[L // g]
        N[g] = v
        sumN += v

    rest = L * L - sumN
    return N, rest


def _U_small_mod_upto(L: int, mod: int) -> list[int]:
    """
    Lucas U-sequence for (P,Q=-1):
      U_0=0, U_1=1, U_n = P*U_{n-1} + U_{n-2}.
    We only need U up to L+1 for initialization.
    """
    U = [0] * (L + 2)
    U[0] = 0
    U[1] = 1
    for i in range(2, L + 2):
        U[i] = (P * U[i - 1] + U[i - 2]) % mod
    return U


# We represent A^n (where A = [[P,1],[1,0]]) by the pair (U_n, U_{n+1}) mod MOD.
# Group operation corresponds to adding indices (matrix multiplication).
def _mul_pair(a0: int, a1: int, b0: int, b1: int, mod: int) -> tuple[int, int]:
    # Using: U_{m+n}   = U_{m+1}U_n + U_m U_{n-1}
    #       U_{m+n+1} = U_{m+1}U_{n+1} + U_m U_n
    t = (b1 - P * b0) % mod  # U_{n-1}
    w0 = (a1 * b0 + a0 * t) % mod
    w1 = (a1 * b1 + a0 * b0) % mod
    return w0, w1


def _sq_pair(a0: int, a1: int, mod: int) -> tuple[int, int]:
    # Doubling formulas:
    # U_{2n}   = U_n * (2*U_{n+1} - P*U_n)
    # U_{2n+1} = U_{n+1}^2 + U_n^2
    v = (2 * a1 - P * a0) % mod
    w0 = (a0 * v) % mod
    w1 = (a1 * a1 + a0 * a0) % mod
    return w0, w1


def _pow_pair_by_bits(
    base0: int, base1: int, bits_lsb_to_msb: list[int], mod: int
) -> tuple[int, int]:
    """
    Compute (A^n)^e = A^{n*e} where base is A^n represented as (U_n, U_{n+1}).
    Exponent e is fixed for the call and provided as bits (LSB->MSB).
    """
    r0, r1 = 0, 1  # identity: A^0 -> (U_0,U_1) = (0,1)
    b0, b1 = base0, base1
    last = len(bits_lsb_to_msb) - 1

    for i, bit in enumerate(bits_lsb_to_msb):
        if bit:
            r0, r1 = _mul_pair(r0, r1, b0, b1, mod)
        if i != last:
            b0, b1 = _sq_pair(b0, b1, mod)
    return r0, r1


def S_mod(L: int, mod: int = MOD) -> int:
    """
    Fast computation of S(L) mod mod.

    Key reductions:
      T(n) = U_{n+1} where U is Lucas U-sequence (P=10,Q=-1).
      gcd(U_m, U_n) = U_gcd(m,n) (strong divisibility).
      gcd(c^a+1, c^b+1) is either c^g+1 (if a/g and b/g are odd) or (c odd ? 2 : 1).
    """
    N, rest = _counts_N_and_rest(L)
    U_small = _U_small_mod_upto(L, mod)

    Nmod = [0] * (L + 1)
    for g in range(1, L + 1):
        Nmod[g] = N[g] % mod

    rest_mod = rest % mod
    U2 = U_small[2]  # 10

    total = 0
    for c in range(1, L + 1):
        # bits of exponent c for repeated powering
        bits: list[int] = []
        x = c
        while x:
            bits.append(x & 1)
            x >>= 1

        # start at n = c^1 = c, so we need (U_c, U_{c+1})
        pair0, pair1 = U_small[c], U_small[c + 1]

        # Pairs where gcd(c^a+1,c^b+1) collapses to 1 or 2:
        small = 1 if (c & 1) == 0 else U2  # U_1=1 if c even, U_2=10 if c odd
        contrib = (rest_mod * small) % mod

        for g in range(1, L + 1):
            contrib = (contrib + Nmod[g] * pair1) % mod
            pair0, pair1 = _pow_pair_by_bits(pair0, pair1, bits, mod)

        total = (total + contrib) % mod

    return total


def main() -> None:
    _run_statement_asserts()
    print(S_mod(TARGET_L, MOD))


if __name__ == "__main__":
    main()
