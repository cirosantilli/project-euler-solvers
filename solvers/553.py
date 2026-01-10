#!/usr/bin/env python3
"""
Project Euler 553: Power Sets of Power Sets
Compute C(10^4, 10) mod 1_000_000_007.

No external libraries are used.
"""

MOD = 1_000_000_007

# NTT-friendly primes (all have primitive root 3)
_NTT_MODS = (
    (998244353, 3),
    (1004535809, 3),
    (469762049, 3),
)

# ---------- NTT implementation (iterative Cooley–Tukey) ----------

_ntt_cache = {}  # (mod, n) -> (rev, roots_fwd, roots_inv)


def _prepare_ntt(mod: int, root: int, n: int):
    key = (mod, n)
    cached = _ntt_cache.get(key)
    if cached is not None:
        return cached

    logn = n.bit_length() - 1
    rev = [0] * n
    for i in range(1, n):
        rev[i] = (rev[i >> 1] >> 1) | ((i & 1) << (logn - 1))

    roots_fwd = []
    roots_inv = []
    length = 2
    while length <= n:
        wlen = pow(root, (mod - 1) // length, mod)
        roots_fwd.append(wlen)
        roots_inv.append(pow(wlen, mod - 2, mod))
        length <<= 1

    cached = (rev, roots_fwd, roots_inv)
    _ntt_cache[key] = cached
    return cached


def _ntt_inplace(a, invert: bool, mod: int, root: int):
    n = len(a)
    rev, roots_fwd, roots_inv = _prepare_ntt(mod, root, n)

    # Bit-reversal permutation
    for i in range(n):
        j = rev[i]
        if i < j:
            a[i], a[j] = a[j], a[i]

    length = 2
    stage = 0
    while length <= n:
        wlen = roots_inv[stage] if invert else roots_fwd[stage]
        half = length >> 1

        for i in range(0, n, length):
            w = 1
            for j in range(i, i + half):
                u = a[j]
                v = (a[j + half] * w) % mod

                x = u + v
                if x >= mod:
                    x -= mod
                a[j] = x

                y = u - v
                if y < 0:
                    y += mod
                a[j + half] = y

                w = (w * wlen) % mod

        stage += 1
        length <<= 1

    if invert:
        inv_n = pow(n, mod - 2, mod)
        for i in range(n):
            a[i] = (a[i] * inv_n) % mod


def _convolution_ntt_mod(a, b, mod: int, root: int):
    if not a or not b:
        return []

    need = len(a) + len(b) - 1
    n = 1
    while n < need:
        n <<= 1

    fa = [0] * n
    fb = [0] * n
    for i, x in enumerate(a):
        fa[i] = x % mod
    for i, x in enumerate(b):
        fb[i] = x % mod

    _ntt_inplace(fa, False, mod, root)
    _ntt_inplace(fb, False, mod, root)

    for i in range(n):
        fa[i] = (fa[i] * fb[i]) % mod

    _ntt_inplace(fa, True, mod, root)
    return fa[:need]


# CRT precomputation for combining three NTT moduli into MOD
_m1, _m2, _m3 = (_NTT_MODS[0][0], _NTT_MODS[1][0], _NTT_MODS[2][0])
_inv_m1_mod_m2 = pow(_m1, _m2 - 2, _m2)
_m1m2 = _m1 * _m2
_inv_m1m2_mod_m3 = pow(_m1m2 % _m3, _m3 - 2, _m3)


def _convolution_mod(a, b, limit=None, naive_threshold=20000):
    """
    Convolution modulo MOD. Uses:
      - naive O(n*m) for small sizes,
      - 3-NTT + CRT for larger sizes.
    If limit is given, returns only the first 'limit' coefficients.
    """
    if not a or not b:
        return []
    need = len(a) + len(b) - 1
    if limit is not None and limit < need:
        need = limit

    # Naive is faster for small products
    if len(a) * len(b) <= naive_threshold:
        res = [0] * need
        for i, ai in enumerate(a):
            if ai == 0:
                continue
            maxj = min(len(b), need - i)
            for j in range(maxj):
                res[i + j] = (res[i + j] + ai * b[j]) % MOD
        return res

    r1 = _convolution_ntt_mod(a, b, _NTT_MODS[0][0], _NTT_MODS[0][1])
    r2 = _convolution_ntt_mod(a, b, _NTT_MODS[1][0], _NTT_MODS[1][1])
    r3 = _convolution_ntt_mod(a, b, _NTT_MODS[2][0], _NTT_MODS[2][1])

    res_len = min(need, len(r1))
    res = [0] * res_len

    for i in range(res_len):
        x1 = r1[i]

        t1 = (r2[i] - x1) % _m2
        t1 = (t1 * _inv_m1_mod_m2) % _m2
        x12 = x1 + _m1 * t1  # exact modulo m1*m2

        t2 = (r3[i] - (x12 % _m3)) % _m3
        t2 = (t2 * _inv_m1m2_mod_m3) % _m3

        x = x12 + _m1m2 * t2  # exact modulo m1*m2*m3
        res[i] = x % MOD

    return res


# ---------- Formal power series utilities ----------


def _poly_inv(f, deg: int):
    """Inverse of a power series f modulo x^deg, assuming f[0] != 0."""
    if deg <= 0:
        return []
    f0 = f[0] % MOD
    if f0 == 0:
        raise ValueError("Series is not invertible (constant term is 0).")
    g = [pow(f0, MOD - 2, MOD)]
    m = 1
    while m < deg:
        m2 = min(2 * m, deg)
        f_cut = f[:m2]
        t = _convolution_mod(f_cut, g, limit=m2)  # t = f*g (mod x^m2)
        # t = 2 - t
        t[0] = (2 - t[0]) % MOD
        for i in range(1, len(t)):
            t[i] = (-t[i]) % MOD
        g = _convolution_mod(g, t, limit=m2)  # g = g*(2 - f*g)
        m = m2
    return g[:deg]


def _poly_log(f, deg: int, inv_int):
    """Natural log of a power series with f[0]=1, modulo x^deg."""
    if deg <= 0:
        return []
    if f[0] != 1:
        raise ValueError("poly_log requires f[0] == 1.")
    # derivative
    df = [(i * f[i]) % MOD for i in range(1, min(len(f), deg))]
    invf = _poly_inv(f[:deg], deg)
    prod = _convolution_mod(df, invf, limit=deg - 1)  # (f'/f) mod x^(deg-1)
    res = [0] * deg
    for i in range(1, deg):
        res[i] = prod[i - 1] * inv_int[i] % MOD
    return res


def _poly_pow(a, exp: int, deg: int):
    """Power of a power series modulo x^deg (ordinary power series multiplication)."""
    res = [0] * deg
    res[0] = 1
    base = a[:deg]
    e = exp
    while e > 0:
        if e & 1:
            res = _convolution_mod(res, base, limit=deg)
        e >>= 1
        if e:
            base = _convolution_mod(base, base, limit=deg)
    return res


# ---------- Problem-specific computation ----------


def _precompute_factorials(n: int):
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = (fact[i - 1] * i) % MOD

    inv_fact = [1] * (n + 1)
    inv_fact[n] = pow(fact[n], MOD - 2, MOD)
    for i in range(n, 0, -1):
        inv_fact[i - 1] = (inv_fact[i] * i) % MOD

    inv_int = [0] * (n + 1)
    if n >= 1:
        inv_int[1] = 1
        for i in range(2, n + 1):
            inv_int[i] = MOD - (MOD // i) * inv_int[MOD % i] % MOD

    return fact, inv_fact, inv_int


def _compute_A_series(max_n: int, inv_fact, inv_int):
    """
    Build A(x) = log(H(x)) up to degree max_n, where:
      H(x) = sum_{n>=0} G(n) x^n/n!
      G(n) = number of (simple) hypergraphs on n labeled vertices with no isolated vertices
    A's coefficients are a_n = F(n)/n!, where F(n) counts connected such hypergraphs.
    """
    modm1 = MOD - 1

    # exp2[i] = 2^i mod (MOD-1)
    exp2 = [1] * (max_n + 1)
    for i in range(1, max_n + 1):
        exp2[i] = (exp2[i - 1] * 2) % modm1

    # A0[i] = 2^(2^i - 1) mod MOD
    A0 = [0] * (max_n + 1)
    for i in range(max_n + 1):
        A0[i] = pow(2, (exp2[i] - 1) % modm1, MOD)

    # Using inclusion–exclusion (binomial transform) in EGF space:
    #   H(x) = sum A0[n]/n! * x^n  convolved with  exp(-x) = sum (-1)^n/n! * x^n
    p = [(A0[i] * inv_fact[i]) % MOD for i in range(max_n + 1)]
    q = [inv_fact[i] if (i & 1) == 0 else (MOD - inv_fact[i]) for i in range(max_n + 1)]
    H = _convolution_mod(p, q, limit=max_n + 1)  # H[n] = G(n)/n!
    H[0] = 1  # safety

    # A(x) = log(H(x))
    A = _poly_log(H, max_n + 1, inv_int)
    return A


def C(n: int, k: int, A_series, fact, inv_fact):
    """
    Compute C(n,k) modulo MOD using:
      C(n,k) = n! * [x^n] exp(x) * (A(x))^k / k!
    where A(x) = sum_{m>=1} F(m) x^m/m! (connected part).
    """
    deg = n + 1
    A = A_series[:deg]
    Ak = _poly_pow(A, k, deg)
    expx = inv_fact[:deg]  # exp(x) has coefficients 1/n!
    prod = _convolution_mod(Ak, expx, limit=deg)
    return fact[n] * prod[n] % MOD * inv_fact[k] % MOD


def solve():
    N = 10_000
    K = 10

    fact, inv_fact, inv_int = _precompute_factorials(N)
    A_series = _compute_A_series(N, inv_fact, inv_int)

    # Test values from the problem statement
    assert C(2, 1, A_series, fact, inv_fact) == 6
    assert C(3, 1, A_series, fact, inv_fact) == 111
    assert C(4, 2, A_series, fact, inv_fact) == 486
    assert C(100, 10, A_series, fact, inv_fact) == 728209718

    ans = C(N, K, A_series, fact, inv_fact)
    print(ans)


if __name__ == "__main__":
    solve()
