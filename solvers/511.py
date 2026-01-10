#!/usr/bin/env python3
"""
Project Euler 511: Sequences with nice divisibility / congruence condition.

We need the last nine digits of:
    Seq(1234567898765, 4321)

Definitions (from the problem statement):
- A sequence (a1..an) is "nice" if:
    1) n is divisible by ai for every i (so each ai is a positive divisor of n)
    2) n + a1 + ... + an is divisible by k
- Seq(n,k) is the number of nice sequences of length n.

This program computes Seq(n,k) modulo 10^9 and prints the answer as 9 digits.
No third-party libraries are used.
"""

from __future__ import annotations

import math
from typing import List, Tuple


MOD = 1_000_000_000
TARGET_N = 1234567898765
TARGET_K = 4321


# ----------------------------- Number theory helpers -----------------------------


def _egcd(a: int, b: int) -> Tuple[int, int, int]:
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = _egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)


def _inv_mod(a: int, m: int) -> int:
    g, x, _ = _egcd(a, m)
    if g != 1:
        raise ValueError("Inverse does not exist")
    return x % m


def factorize(n: int) -> List[Tuple[int, int]]:
    """Trial division factorization; fast enough for n <= ~1e12."""
    fac: List[Tuple[int, int]] = []
    cnt = 0
    while n % 2 == 0:
        n //= 2
        cnt += 1
    if cnt:
        fac.append((2, cnt))

    cnt = 0
    while n % 3 == 0:
        n //= 3
        cnt += 1
    if cnt:
        fac.append((3, cnt))

    f = 5
    step = 2
    while f * f <= n:
        cnt = 0
        while n % f == 0:
            n //= f
            cnt += 1
        if cnt:
            fac.append((f, cnt))
        f += step
        step = 6 - step  # 2,4,2,4,... (checks 6k±1)
    if n > 1:
        fac.append((n, 1))
    return fac


def divisor_residue_counts(n: int, k: int) -> List[int]:
    """Return counts[r] = #{d | n : d mod k = r}."""
    fac = factorize(n)
    counts = [0] * k

    def rec(i: int, cur: int) -> None:
        if i == len(fac):
            counts[cur % k] += 1
            return
        p, e = fac[i]
        v = cur
        for _ in range(e + 1):
            rec(i + 1, v)
            v *= p

    rec(0, 1)
    return counts


# ----------------------------- Fast cyclic convolution for k=4321 -----------------------------


class _FFT4321:
    """
    Implements a length-4321 DFT using the Good-Thomas / Prime Factor Algorithm
    with 4321 = 29 * 149 (coprime factors). Used to compute cyclic convolutions.

    We deliberately use floating point complex arithmetic, but keep the numbers
    small enough (via coefficient splitting) that rounding back to exact integers
    is reliable.
    """

    N = 4321
    N1 = 29
    N2 = 149

    def __init__(self) -> None:
        N1 = self.N1
        N2 = self.N2
        N = self.N

        # CRT-based permutation used by Good-Thomas
        m1 = _inv_mod(N1 % N2, N2)
        m2 = _inv_mod(N2 % N1, N1)
        idx_map = [0] * N
        for i1 in range(N1):
            base = i1 * N2
            term1 = i1 * N2 * m2
            for i2 in range(N2):
                pos = base + i2
                idx_map[pos] = (term1 + i2 * N1 * m1) % N
        self._idx_map = idx_map

        # Precompute DFT weight tables (transposed) for sizes 29 and 149.
        # W_T[t][j] = exp(sign * 2πi * j*t / m), where sign is -1 (forward) or +1 (inverse).
        self._W29T_fwd = self._build_weights_T(N1, inverse=False)
        self._W29T_inv = self._build_weights_T(N1, inverse=True)
        self._W149T_fwd = self._build_weights_T(N2, inverse=False)
        self._W149T_inv = self._build_weights_T(N2, inverse=True)

        self._inv_sqrtN = 1.0 / math.sqrt(N)

        # Handy ranges
        self._r29 = range(N1)
        self._r149 = range(N2)
        self._rN = range(N)

    @staticmethod
    def _build_weights_T(m: int, inverse: bool) -> List[List[complex]]:
        sign = 1.0 if inverse else -1.0
        twopi = 2.0 * math.pi
        # Allocate transposed directly
        WT: List[List[complex]] = [[0j] * m for _ in range(m)]
        for t in range(m):
            for j in range(m):
                ang = sign * twopi * j * t / m
                WT[t][j] = complex(math.cos(ang), math.sin(ang))
        return WT

    def _dft_pfa(
        self, x: List[complex] | List[float] | List[int], inverse: bool
    ) -> List[complex]:
        """
        PFA DFT. If inverse=True, uses + exponent (sum-only inverse DFT, no 1/N scaling).
        """
        idx_map = self._idx_map
        N1 = self.N1
        N2 = self.N2

        W1T = self._W29T_inv if inverse else self._W29T_fwd
        W2T = self._W149T_inv if inverse else self._W149T_fwd

        # Input permutation into (N1 x N2) matrix (flattened).
        mat = [0j] * self.N
        for pos, idx in enumerate(idx_map):
            mat[pos] = x[idx]

        # Stage 1: DFT of size 29 down columns (N2 columns).
        tmp1 = [0j] * N1
        step = N2
        r29 = self._r29
        for i2 in self._r149:
            # zero tmp1
            for j in r29:
                tmp1[j] = 0j
            off = i2
            for t in r29:
                xt = mat[off]
                off += step
                wt = W1T[t]
                for j in r29:
                    tmp1[j] += xt * wt[j]
            off = i2
            for j in r29:
                mat[off] = tmp1[j]
                off += step

        # Stage 2: DFT of size 149 across rows (N1 rows).
        tmp2 = [0j] * N2
        r149 = self._r149
        for i1 in r29:
            base = i1 * N2
            for j in r149:
                tmp2[j] = 0j
            for t in r149:
                xt = mat[base + t]
                wt = W2T[t]
                for j in r149:
                    tmp2[j] += xt * wt[j]
            for j in r149:
                mat[base + j] = tmp2[j]

        # Output permutation back to 1D order.
        out = [0j] * self.N
        for pos, idx in enumerate(idx_map):
            out[idx] = mat[pos]
        return out

    def fft_scaled_real(self, a: List[int] | List[float]) -> List[complex]:
        """Forward DFT, then scale by 1/sqrt(N)."""
        A = self._dft_pfa(a, inverse=False)
        s = self._inv_sqrtN
        return [z * s for z in A]

    def ifft_noscale(self, A: List[complex]) -> List[complex]:
        """Sum-only inverse DFT (no 1/N scaling)."""
        return self._dft_pfa(A, inverse=True)

    def cyclic_convolution_int(self, a: List[int], b: List[int]) -> List[int]:
        """Exact cyclic convolution over Z, via FFT with rounding."""
        Af = self.fft_scaled_real(a)
        Bf = self.fft_scaled_real(b)
        prod = [Af[i] * Bf[i] for i in self._rN]
        c = self.ifft_noscale(prod)
        out = [0] * self.N
        # custom rounding (avoids banker's rounding)
        for i, z in enumerate(c):
            x = z.real
            out[i] = int(x + 0.5) if x >= 0 else int(x - 0.5)
        return out


_FFT = None  # lazy singleton


def _get_fft() -> _FFT4321:
    global _FFT
    if _FFT is None:
        _FFT = _FFT4321()
    return _FFT


def mul_mod_4321(a: List[int], b: List[int]) -> List[int]:
    """
    Cyclic convolution mod 1e9 for length 4321, using splitting into 15-bit chunks:
        x = x0 + x1*B, B=2^15
    We compute:
        c00 = conv(x0,y0)
        c11 = conv(x1,y1)
        cs  = conv(x0+x1, y0+y1)
        cross = cs - c00 - c11 = conv(x0,y1) + conv(x1,y0)
    Then combine modulo MOD.
    """
    fft = _get_fft()
    N = fft.N
    mask = (1 << 15) - 1
    B = 1 << 15
    B2 = (B * B) % MOD

    a0 = [x & mask for x in a]
    a1 = [x >> 15 for x in a]
    b0 = [x & mask for x in b]
    b1 = [x >> 15 for x in b]

    A0 = fft.fft_scaled_real(a0)
    A1 = fft.fft_scaled_real(a1)
    B0 = fft.fft_scaled_real(b0)
    B1 = fft.fft_scaled_real(b1)

    rN = range(N)

    def ifft_round_from_freq(P: List[complex]) -> List[int]:
        c = fft.ifft_noscale(P)
        out = [0] * N
        for i, z in enumerate(c):
            x = z.real
            out[i] = int(x + 0.5) if x >= 0 else int(x - 0.5)
        return out

    c00 = ifft_round_from_freq([A0[i] * B0[i] for i in rN])
    c11 = ifft_round_from_freq([A1[i] * B1[i] for i in rN])

    AS = [A0[i] + A1[i] for i in rN]
    BS = [B0[i] + B1[i] for i in rN]
    cs = ifft_round_from_freq([AS[i] * BS[i] for i in rN])

    res = [0] * N
    for i in rN:
        cross = cs[i] - c00[i] - c11[i]
        res[i] = (c00[i] + (cross % MOD) * B + (c11[i] % MOD) * B2) % MOD
    return res


def square_mod_4321(a: List[int]) -> List[int]:
    """Faster path for squaring (a * a) modulo MOD (2 FFTs instead of 4)."""
    fft = _get_fft()
    N = fft.N
    mask = (1 << 15) - 1
    B = 1 << 15
    B2 = (B * B) % MOD

    a0 = [x & mask for x in a]
    a1 = [x >> 15 for x in a]

    A0 = fft.fft_scaled_real(a0)
    A1 = fft.fft_scaled_real(a1)

    rN = range(N)

    def ifft_round_from_freq(P: List[complex]) -> List[int]:
        c = fft.ifft_noscale(P)
        out = [0] * N
        for i, z in enumerate(c):
            x = z.real
            out[i] = int(x + 0.5) if x >= 0 else int(x - 0.5)
        return out

    c00 = ifft_round_from_freq([A0[i] * A0[i] for i in rN])
    c11 = ifft_round_from_freq([A1[i] * A1[i] for i in rN])

    AS = [A0[i] + A1[i] for i in rN]
    cs = ifft_round_from_freq([AS[i] * AS[i] for i in rN])

    res = [0] * N
    for i in rN:
        cross = cs[i] - c00[i] - c11[i]
        res[i] = (c00[i] + (cross % MOD) * B + (c11[i] % MOD) * B2) % MOD
    return res


# ----------------------------- Generic cyclic convolution (naive fallback) -----------------------------


def mul_cyclic_mod(a: List[int], b: List[int], k: int) -> List[int]:
    if k == TARGET_K:
        return mul_mod_4321(a, b)
    # naive O(k^2) (only used for small k in asserts)
    res = [0] * k
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    res[(i + j) % k] = (res[(i + j) % k] + ai * bj) % MOD
    return res


def square_cyclic_mod(a: List[int], k: int) -> List[int]:
    if k == TARGET_K:
        return square_mod_4321(a)
    return mul_cyclic_mod(a, a, k)


def pow_cyclic_mod(base: List[int], exp: int, k: int) -> List[int]:
    res = [0] * k
    res[0] = 1
    b = base[:]
    e = exp
    while e:
        if e & 1:
            res = mul_cyclic_mod(res, b, k)
        e >>= 1
        if e:
            b = square_cyclic_mod(b, k)
    return res


# ----------------------------- Problem function -----------------------------


def seq_last9(n: int, k: int) -> int:
    v = divisor_residue_counts(n, k)
    v = [x % MOD for x in v]
    dist = pow_cyclic_mod(v, n, k)
    need = (-n) % k
    return dist[need] % MOD


def main() -> None:
    # Asserts from the problem statement
    assert seq_last9(3, 4) == 4
    assert seq_last9(4, 11) == 8
    assert seq_last9(1111, 24) == 840643584

    ans = seq_last9(TARGET_N, TARGET_K)
    print(f"{ans:09d}")


if __name__ == "__main__":
    main()
