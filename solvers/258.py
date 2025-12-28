#!/usr/bin/env python3
"""Project Euler 258: A Lagged Fibonacci Sequence.

The sequence is:
  g_k = 1                      for 0 <= k <= 1999
  g_k = g_{k-2000} + g_{k-1999} for k >= 2000

We need g_{10^18} mod 20092010.

Key idea:
The characteristic polynomial is x^2000 - x - 1, i.e. x^2000 == x + 1.
Compute x^n modulo this polynomial (as a degree < 2000 polynomial) using
binary exponentiation. With initial terms all equal to 1, g_n is simply the
sum of the coefficients of x^n (mod MOD).

For speed we use NumPy's C-accelerated convolution. If NumPy is unavailable,
we fall back to a pure-Python convolution (likely too slow for the full n,
but still correct).
"""

from __future__ import annotations

from typing import List


MOD = 20092010
D = 2000  # order


try:
    import numpy as _np  # type: ignore

    _HAVE_NUMPY = True
except Exception:  # pragma: no cover
    _np = None
    _HAVE_NUMPY = False


def _mul_poly_mod_numpy(a: "_np.ndarray", b: "_np.ndarray") -> "_np.ndarray":
    """Multiply two degree< D polynomials modulo x^D - x - 1 over Z_MOD."""
    # Convolution length is 2D-1 (<= 3999). Values fit in int64 safely.
    c = _np.convolve(a, b).astype(_np.int64, copy=False)
    # Fold degrees >= D using x^D = x + 1:
    # for i >= D: c[i] * x^i -> c[i] added to x^(i-D) and x^(i-D+1)
    hi = c[D:]  # length D-1
    res = c[:D].copy()
    res[: D - 1] += hi
    res[1:] += hi
    res %= MOD
    return res


def _mul_poly_mod_py(a: List[int], b: List[int]) -> List[int]:
    """Pure-Python multiply; correct but slow."""
    # Full convolution (0..2D-2)
    c = [0] * (2 * D - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                if bj:
                    c[i + j] += ai * bj
    # Fold once (max degree 3998 so one pass suffices)
    for i in range(2 * D - 2, D - 1, -1):
        t = c[i] % MOD
        if t:
            c[i - D] = (c[i - D] + t) % MOD
            c[i - D + 1] = (c[i - D + 1] + t) % MOD
    return [x % MOD for x in c[:D]]


def x_pow_mod(n: int):
    """Return coefficients of x^n modulo (x^D - x - 1), degree < D.

    The result is a length-D vector p such that:
        x^n ≡ sum_{i=0..D-1} p[i] x^i (mod x^D - x - 1).
    """
    if n < 0:
        raise ValueError("n must be non-negative")

    if _HAVE_NUMPY:
        one = _np.zeros(D, dtype=_np.int64)
        one[0] = 1
        x = _np.zeros(D, dtype=_np.int64)
        if D > 1:
            x[1] = 1
        else:
            # Not used here (D=2000), but kept for completeness.
            x[0] = 0

        res = one
        base = x
        e = n
        while e:
            if e & 1:
                res = _mul_poly_mod_numpy(res, base)
            e >>= 1
            if e:
                base = _mul_poly_mod_numpy(base, base)
        return res

    # Pure Python fallback
    res = [0] * D
    res[0] = 1
    base = [0] * D
    if D > 1:
        base[1] = 1
    e = n
    while e:
        if e & 1:
            res = _mul_poly_mod_py(res, base)
        e >>= 1
        if e:
            base = _mul_poly_mod_py(base, base)
    return res


def g_mod(n: int) -> int:
    """Compute g_n mod MOD."""
    # Base definition from the problem statement.
    if 0 <= n <= D - 1:
        return 1

    coeffs = x_pow_mod(n)
    if _HAVE_NUMPY:
        return int(coeffs.sum() % MOD)
    return sum(coeffs) % MOD


def _self_test() -> None:
    # Asserts from the problem definition.
    assert g_mod(0) == 1
    assert g_mod(1999) == 1

    # A few quick derived checks (sanity).
    # g_2000 = g_0 + g_1 = 2
    assert g_mod(2000) == 2
    assert g_mod(2001) == 2
    # g_3999 = g_1999 + g_2000 = 3
    assert g_mod(3999) == 3

    # Cross-check fast method vs naive for a small prefix.
    limit = 6000
    g = [1] * D
    for k in range(D, limit + 1):
        g.append((g[k - D] + g[k - D + 1]) % MOD)
    for k in (0, 1, 2, 1999, 2000, 2001, 2500, 3999, 4000, 5432, 6000):
        assert g_mod(k) == g[k]


def main() -> None:
    _self_test()
    print(g_mod(10**18))


if __name__ == "__main__":
    main()
