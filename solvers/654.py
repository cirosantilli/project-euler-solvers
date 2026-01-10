#!/usr/bin/env python3
"""
Project Euler 654 - Neighbourly Constraints

Compute T(n, m): the number of m-tuples (a1..am) of positive integers such that
ai + a{i+1} <= n for all i, modulo 1_000_000_007.

This program prints T(5000, 10^12) mod 1_000_000_007.

No third-party libraries are used.
"""
from __future__ import annotations

import math
from typing import List, Dict


MOD = 1_000_000_007

# For FFT-based modular convolution, we split coefficients into 15-bit chunks.
B = 1 << 15
MASK = B - 1
BMOD = B % MOD
B2MOD = (B * B) % MOD


def _iround(x: float) -> int:
    """Round-to-nearest for values expected to be near an integer."""
    if x >= 0.0:
        return int(x + 0.5)
    return -int(-x + 0.5)


class _FFTPlan:
    """
    Reusable iterative FFT plan for a fixed power-of-two size.

    This is a plain complex FFT (Cooley-Tukey) with precomputed roots.
    """

    __slots__ = ("n", "rev", "roots_fwd", "roots_inv")

    def __init__(self, n: int):
        self.n = n
        lg = n.bit_length() - 1

        # Bit-reversal permutation.
        rev = [0] * n
        for i in range(1, n):
            rev[i] = (rev[i >> 1] >> 1) | ((i & 1) << (lg - 1))
        self.rev = rev

        # Precompute roots for each stage length.
        roots_fwd: Dict[int, List[complex]] = {}
        roots_inv: Dict[int, List[complex]] = {}
        two_pi = 2.0 * math.pi
        length = 2
        while length <= n:
            half = length >> 1
            ang = two_pi / length
            rl = [complex(math.cos(ang * k), math.sin(ang * k)) for k in range(half)]
            roots_fwd[length] = rl
            roots_inv[length] = [z.conjugate() for z in rl]
            length <<= 1
        self.roots_fwd = roots_fwd
        self.roots_inv = roots_inv

    def fft(self, a: List[complex], invert: bool) -> None:
        """In-place FFT."""
        n = self.n
        rev = self.rev

        # Bit-reversal reorder.
        for i in range(n):
            j = rev[i]
            if i < j:
                a[i], a[j] = a[j], a[i]

        roots = self.roots_inv if invert else self.roots_fwd

        length = 2
        while length <= n:
            half = length >> 1
            root_list = roots[length]
            for base in range(0, n, length):
                for k in range(half):
                    u = a[base + k]
                    v = a[base + k + half] * root_list[k]
                    a[base + k] = u + v
                    a[base + k + half] = u - v
            length <<= 1

        if invert:
            inv_n = 1.0 / n
            for i in range(n):
                a[i] *= inv_n


_plan_cache: Dict[int, _FFTPlan] = {}


def _get_plan(n: int) -> _FFTPlan:
    plan = _plan_cache.get(n)
    if plan is None:
        plan = _FFTPlan(n)
        _plan_cache[n] = plan
    return plan


def convolve_mod(a: List[int], b: List[int], mod: int = MOD) -> List[int]:
    """
    Convolution of integer polynomials modulo mod, using FFT over complex numbers.

    Coefficients are assumed to be already reduced to [0, mod).
    """
    la, lb = len(a), len(b)
    if la == 0 or lb == 0:
        return []
    need = la + lb - 1
    n = 1 << ((need - 1).bit_length())
    plan = _get_plan(n)

    fa = [0j] * n
    fb = [0j] * n
    for i, x in enumerate(a):
        fa[i] = complex(x & MASK, x >> 15)
    for i, x in enumerate(b):
        fb[i] = complex(x & MASK, x >> 15)

    plan.fft(fa, False)
    plan.fft(fb, False)

    # p = FFT(a0 + i a1) * FFT(b0 + i b1)  -> gives (c00 - c11) + i*(mid)
    p = [0j] * n
    for i in range(n):
        p[i] = fa[i] * fb[i]

    # q computes convolution of (a0+a1) and (b0+b1) using frequency-domain splitting.
    q = [0j] * n
    nmask = n - 1
    half = 0.5
    halfj = -0.5j
    for i in range(n):
        j = (-i) & nmask

        ai = fa[i]
        aj = fa[j].conjugate()
        bi = fb[i]
        bj = fb[j].conjugate()

        # Recover FFTs of real parts (a0) and imag parts (a1) from packed FFT.
        f0a = (ai + aj) * half
        f1a = (ai - aj) * halfj
        f0b = (bi + bj) * half
        f1b = (bi - bj) * halfj

        sa = f0a + f1a  # FFT(a0+a1)
        sb = f0b + f1b  # FFT(b0+b1)
        q[i] = sa * sb

    plan.fft(p, True)
    plan.fft(q, True)

    res = [0] * need
    for i in range(need):
        r = _iround(p[i].real)  # c00 - c11
        mid = _iround(p[i].imag)  # c01 + c10
        s = _iround(q[i].real)  # c00 + mid + c11

        c00_plus_c11 = s - mid  # c00 + c11
        c00 = (c00_plus_c11 + r) // 2
        c11 = c00_plus_c11 - c00

        res[i] = (c00 % mod + (mid % mod) * BMOD + (c11 % mod) * B2MOD) % mod
    return res


def berlekamp_massey(seq: List[int], mod: int = MOD) -> List[int]:
    """
    Berlekamp–Massey over F_mod.
    Returns recurrence coefficients rec of length L such that:
        a[n] = rec[0]*a[n-1] + ... + rec[L-1]*a[n-L]   (mod mod)
    """
    C = [1]
    Bp = [1]
    L = 0
    m = 1
    b = 1

    for n, sn in enumerate(seq):
        # discrepancy d
        d = sn
        for i in range(1, L + 1):
            d = (d + C[i] * seq[n - i]) % mod

        if d == 0:
            m += 1
            continue

        coef = d * pow(b, mod - 2, mod) % mod
        T = C.copy()

        need_len = len(Bp) + m
        if len(C) < need_len:
            C += [0] * (need_len - len(C))
        for i in range(len(Bp)):
            C[i + m] = (C[i + m] - coef * Bp[i]) % mod

        if 2 * L <= n:
            L = n + 1 - L
            Bp = T
            b = d
            m = 1
        else:
            m += 1

    # Convert connection polynomial to recurrence coefficients.
    return [(mod - C[i]) % mod for i in range(1, L + 1)]


def _build_P(init: List[int], rec: List[int], mod: int = MOD) -> List[int]:
    """
    Build P(x) such that sum a_n x^n = P(x) / Q(x),
    where Q(x) = 1 - rec[0]x - ... - rec[L-1]x^L.
    """
    L = len(rec)
    P = [0] * L
    for i in range(L):
        v = init[i]
        for j in range(1, i + 1):
            v = (v - rec[j - 1] * init[i - j]) % mod
        P[i] = v
    return P


def bostan_mori(P: List[int], Q: List[int], n: int, mod: int = MOD) -> int:
    """
    Bostan–Mori: return [x^n] P(x)/Q(x) (mod mod).
    """
    while n:
        # Q(-x)
        Qm = Q[:]
        for i in range(1, len(Qm), 2):
            qi = Qm[i]
            if qi:
                Qm[i] = mod - qi

        U = convolve_mod(P, Qm, mod)
        V = convolve_mod(Q, Qm, mod)

        P = U[1::2] if (n & 1) else U[0::2]
        Q = V[0::2]
        n >>= 1

        while P and P[-1] == 0:
            P.pop()
        while Q and Q[-1] == 0:
            Q.pop()

    return P[0] * pow(Q[0], mod - 2, mod) % mod


def T_mod(n: int, m: int, mod: int = MOD) -> int:
    """
    Compute T(n,m) mod mod.
    For small m we do direct DP; for huge m we use BM + Bostan-Mori.
    """
    N = n - 1
    if m <= 1:
        return N % mod

    # Direct DP is cheap whenever m is not too large.
    if m <= 20000 or N <= 400:
        dp = [1] * N
        prefix = [0] * (N + 1)
        for _ in range(1, m):
            s = 0
            prefix[0] = 0
            for i, x in enumerate(dp):
                s += x
                if s >= mod:
                    s -= mod
                prefix[i + 1] = s
            dp = prefix[:0:-1]  # [prefix[N], ..., prefix[1]]

        total = 0
        for x in dp:
            total += x
            if total >= mod:
                total -= mod
        return total

    # Build first 2N terms via O(N^2) DP.
    terms_needed = 2 * N
    dp = [1] * N
    prefix = [0] * (N + 1)
    seq = [0] * terms_needed
    for t in range(terms_needed):
        s = 0
        prefix[0] = 0
        for i, x in enumerate(dp):
            s += x
            if s >= mod:
                s -= mod
            prefix[i + 1] = s
        seq[t] = s
        dp = prefix[:0:-1]

    rec = berlekamp_massey(seq, mod)
    L = len(rec)
    init = seq[:L]
    P = _build_P(init, rec, mod)
    Q = [1] + [(mod - c) % mod for c in rec]  # 1 - rec[0]x - ... - rec[L-1]x^L

    # We indexed seq as T(n,1),T(n,2),... so we want term (m-1) (0-based).
    return bostan_mori(P, Q, m - 1, mod)


def main() -> None:
    # Problem statement test values
    assert T_mod(3, 4) == 8
    assert T_mod(5, 5) == 246
    assert T_mod(10, 10**2) == 862820094
    assert T_mod(10**2, 10) == 782136797

    print(T_mod(5000, 10**12))


if __name__ == "__main__":
    main()
