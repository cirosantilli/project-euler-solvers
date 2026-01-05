#!/usr/bin/env python3
"""
Project Euler 344: Silver Dollar Game
------------------------------------

Compute W(1_000_000, 100) modulo 1000036000099.

No external libraries are used (standard library only).
"""

from __future__ import annotations

from array import array
import math


MOD = 1000036000099
P1 = 1000003
P2 = 1000033


# ---------- Core combinatorics: count q-tuples with XOR == 0 and fixed sum ----------


def _coeff_even_choose(q: int, mod: int) -> list[int]:
    """Return coeff[j] = C(q, 2*j) mod mod, for j=0..q//2."""
    return [math.comb(q, 2 * j) % mod for j in range(q // 2 + 1)]


def count_xor0_by_sum(q: int, s_max: int, mod: int) -> array:
    """
    Let F[s] = #{(x_1..x_q) in Z_{\ge0}^q : x_1 xor ... xor x_q = 0 and sum x_i = s} (mod mod),
    for s=0..s_max.

    Key recurrence (LSB split):
      write x_i = 2*u_i + v_i, v_i in {0,1}.
      For XOR==0 we need an even number of odd x_i (v_i=1), so sum parity is even.
      After dividing by 2, the higher-bit XOR condition is again XOR(u_i)==0.

    This yields a halving recursion on s_max. Using a small convolution:
      For even s = 2*t:
        F[2*t] = sum_{j=0..min(q//2, t)} C(q, 2*j) * G[t-j],
      where G is the same distribution for s_max//2.

    Odd indices are always 0.
    """
    coeff = _coeff_even_choose(q, mod)

    def rec(S: int) -> array:
        if S == 0:
            return array("Q", [1])
        G = rec(S // 2)
        F = array("Q", [0]) * (S + 1)

        G_local = G
        coeff_local = coeff
        mod_local = mod
        jmax_global = q // 2
        # Only even sums can occur
        for t in range(S // 2 + 1):
            # F[2*t] = sum_j coeff[j] * G[t-j]
            total = 0
            maxj = jmax_global if t >= jmax_global else t
            # small (<=26) inner loop
            for j in range(maxj + 1):
                total += coeff_local[j] * G_local[t - j]
            F[2 * t] = total % mod_local
        return F

    return rec(s_max)


def reduce_mod(arr: array, mod: int) -> array:
    """Reduce an array('Q') modulo mod into array('I')."""
    out = array("I", [0]) * len(arr)
    for i, v in enumerate(arr):
        out[i] = v % mod
    return out


# ---------- Binomial helpers (k is small: <= 101) ----------


def nCk_mod_prime_smallk(n: int, k: int, p: int) -> int:
    """Compute C(n,k) mod prime p for small k via multiplicative formula."""
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    num = 1
    den = 1
    nk = n - k
    for i in range(1, k + 1):
        num = (num * (nk + i)) % p
        den = (den * i) % p
    return (num * pow(den, p - 2, p)) % p


def inv_table_prime(p: int, nmax: int) -> array:
    """inv[i] = i^{-1} mod prime p for i=1..nmax (O(nmax))."""
    inv = array("I", [0]) * (nmax + 1)
    inv[1] = 1
    for i in range(2, nmax + 1):
        inv[i] = (p - (p // i) * inv[p % i] % p) % p
    return inv


# ---------- Count winning configurations (even c only, which is what PE344 uses) ----------


def W_exact_even_c(n: int, c: int) -> int:
    """
    Exact W(n,c) for even c (works fast for the small test cases in the statement).
    """
    if c % 2 != 0:
        raise ValueError(
            "This implementation focuses on even c (the Euler problem uses c=100)."
        )

    p = c // 2
    m = c + 1
    S = n - m  # total empty squares among all gaps

    q = p + 1  # number of 'even gaps' (Nim heaps)

    # exact F arrays via the same recursion, but with Python ints
    def count_xor0_exact(q_: int, s_max_: int) -> list[int]:
        coeff2 = [math.comb(q_, 2 * j) for j in range(q_ // 2 + 1)]

        def rec(S_: int) -> list[int]:
            if S_ == 0:
                return [1]
            G_ = rec(S_ // 2)
            F_ = [0] * (S_ + 1)
            jmax_g = q_ // 2
            for t in range(S_ // 2 + 1):
                total = 0
                maxj = jmax_g if t >= jmax_g else t
                for j in range(maxj + 1):
                    total += coeff2[j] * G_[t - j]
                F_[2 * t] = total
            return F_

        return rec(s_max_)

    Fq = count_xor0_exact(q, S + 1)
    Fp = count_xor0_exact(p, S + 1)

    def weight(sumA: int) -> int:
        # Distribute remaining empties among (p+1) odd gaps: C((S-sumA)+p, p)
        return math.comb((S - sumA) + p, p)

    # Losing positions split (for even c):
    #   L2:   silver is the 2nd coin from the left  -> XOR(even gaps) == 0
    #   Loth: silver is any of the other c-1 coins  -> XOR(rest) == a0+1
    # The key bijection: replace a0 with b0=a0+1, then XOR(b0, rest) == 0 and b0>=1
    L2 = 0
    Loth = 0
    for s in range(S + 1):
        w = weight(s)
        L2 += Fq[s] * w
        Loth += (Fq[s + 1] - Fp[s + 1]) * w

    total = m * math.comb(n, m)
    losing = L2 + (c - 1) * Loth
    return total - losing


def W_mod_even_c(n: int, c: int) -> int:
    """
    Compute W(n,c) mod MOD for even c via:
      1) compute F distributions mod MOD (composite),
      2) reduce them mod each prime factor,
      3) compute answer mod each prime (needs inverses),
      4) CRT to MOD.
    """
    if c % 2 != 0:
        raise ValueError(
            "This implementation focuses on even c (the Euler problem uses c=100)."
        )

    p = c // 2
    m = c + 1
    S = n - m
    q = p + 1

    # Step 1: compute F arrays modulo MOD once (safe: only +/* operations)
    Fq_modM = count_xor0_by_sum(q, S + 1, MOD)
    Fp_modM = count_xor0_by_sum(p, S + 1, MOD)

    # Step 2: reduce to each prime
    Fq1 = reduce_mod(Fq_modM, P1)
    Fp1 = reduce_mod(Fp_modM, P1)
    Fq2 = reduce_mod(Fq_modM, P2)
    Fp2 = reduce_mod(Fp_modM, P2)

    # Step 3: answer modulo a prime
    def solve_prime(pr: int, Fq: array, Fp: array) -> int:
        # weights w_s = C((S-s)+p, p), we only need even s for L2 and odd s for Loth,
        # so we iterate in pairs (s=2t and s=2t+1) to halve loop overhead.
        inv = inv_table_prime(pr, S + p)

        n0 = S + p
        w_even = nCk_mod_prime_smallk(n0, p, pr)  # s = 0
        w_odd = (w_even * (n0 - p) % pr) * inv[n0] % pr  # s = 1

        L2 = 0
        Loth = 0

        n_even = n0
        n_odd = n0 - 1

        tmax = S // 2
        for t in range(tmax + 1):
            s_even = 2 * t
            # L2 uses even s (Fq[odd] = 0 anyway)
            L2 = (L2 + (Fq[s_even] * w_even)) % pr

            # Loth uses odd s, and needs Fq[s+1] - Fp[s+1] which is nonzero only when s+1 is even
            if s_even + 1 <= S:
                idx = s_even + 2  # (s_odd + 1)
                diff = (Fq[idx] - Fp[idx]) % pr
                Loth = (Loth + (diff * w_odd)) % pr

            if t != tmax:
                # Update w_even: n_even -> n_even-2
                w_even = (w_even * (n_even - p)) % pr
                w_even = (w_even * (n_even - p - 1)) % pr
                w_even = (w_even * inv[n_even]) % pr
                w_even = (w_even * inv[n_even - 1]) % pr
                n_even -= 2

                # Update w_odd: n_odd -> n_odd-2
                w_odd = (w_odd * (n_odd - p)) % pr
                w_odd = (w_odd * (n_odd - p - 1)) % pr
                w_odd = (w_odd * inv[n_odd]) % pr
                w_odd = (w_odd * inv[n_odd - 1]) % pr
                n_odd -= 2

        total = (m * nCk_mod_prime_smallk(n, m, pr)) % pr
        losing = (L2 + (c - 1) * Loth) % pr
        return (total - losing) % pr

    a1 = solve_prime(P1, Fq1, Fp1)
    a2 = solve_prime(P2, Fq2, Fp2)

    # Step 4: CRT for two primes
    inv_p1_mod_p2 = pow(P1, -1, P2)
    t = ((a2 - a1) % P2) * inv_p1_mod_p2 % P2
    return (a1 + P1 * t) % MOD


def main() -> None:
    # Asserts from the problem statement
    assert W_exact_even_c(10, 2) == 324
    assert W_exact_even_c(100, 10) == 1514704946113500

    print(W_mod_even_c(1_000_000, 100))


if __name__ == "__main__":
    main()
