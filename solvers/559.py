#!/usr/bin/env python3
"""
Project Euler 559 - Permuted Matrices

We compute:
  Q(n) = sum_{k=1..n} P(k, n, n) (mod 1000000123)

No external libraries are used.
"""

from array import array

MOD = 1000000123

# We multiply polynomials modulo MOD using Kronecker substitution:
# pack coefficients (after splitting) into a huge base-2^64 integer and use Python's
# fast big-integer multiplication, then unpack 64-bit limbs.
_BASE_BITS = 23
_BASE = 1 << _BASE_BITS
_MASK = _BASE - 1


def _conv_u64(a, b):
    """
    Convolution of nonnegative integer sequences a and b.

    Preconditions:
      - All elements are >= 0 and fit in 64 bits.
      - The true convolution coefficients are guaranteed to be < 2^64
        (so base-2^64 packing produces no carries between limbs).
    Returns:
      array('Q') of length len(a)+len(b)-1 with exact convolution coefficients.
    """
    n = len(a)
    m = len(b)
    if n == 0 or m == 0:
        return array("Q")

    A_int = int.from_bytes(array("Q", a).tobytes(), "little", signed=False)
    B_int = int.from_bytes(array("Q", b).tobytes(), "little", signed=False)
    C_int = A_int * B_int

    out_len = n + m - 1
    bs = C_int.to_bytes(8 * out_len, "little", signed=False)
    res = array("Q")
    res.frombytes(bs)
    return res


def _poly_mul_naive(A, B, mod=MOD):
    n = len(A)
    m = len(B)
    res = [0] * (n + m - 1)
    for i, ai in enumerate(A):
        if ai:
            for j, bj in enumerate(B):
                res[i + j] = (res[i + j] + ai * bj) % mod
    return res


def poly_mul_mod(A, B, mod=MOD):
    """
    Multiply two polynomials modulo mod.

    Uses a naive method for tiny sizes, otherwise:
      - split coefficients into low/high 23-bit parts
      - use Karatsuba (3 convolutions)
      - do each convolution via base-2^64 Kronecker substitution.
    """
    if not A or not B:
        return []
    n = len(A)
    m = len(B)

    # Heuristic cutoff: for small work, naive wins in Python.
    if n * m <= 40000 or min(n, m) <= 40:
        return _poly_mul_naive(A, B, mod)

    a0 = [x & _MASK for x in A]
    a1 = [x >> _BASE_BITS for x in A]
    b0 = [x & _MASK for x in B]
    b1 = [x >> _BASE_BITS for x in B]

    z0 = _conv_u64(a0, b0)
    z2 = _conv_u64(a1, b1)

    sa = [a0[i] + a1[i] for i in range(n)]
    sb = [b0[i] + b1[i] for i in range(m)]
    z1 = _conv_u64(sa, sb)  # = (a0+a1)*(b0+b1)

    out_len = n + m - 1
    res = [0] * out_len
    shift1 = _BASE_BITS
    shift2 = 2 * _BASE_BITS
    for i in range(out_len):
        cross = int(z1[i]) - int(z0[i]) - int(z2[i])  # a0*b1 + a1*b0
        res[i] = (int(z0[i]) + (cross << shift1) + (int(z2[i]) << shift2)) % mod
    return res


def poly_inv_mod(f, n, mod=MOD):
    """
    Invert a power series f modulo x^n using Newton iteration.
    Requires f[0] != 0.
    """
    inv0 = pow(f[0], mod - 2, mod)
    g = [inv0]
    m = 1
    while m < n:
        m2 = min(2 * m, n)
        fg = poly_mul_mod(f[:m2], g, mod)[:m2]

        # fg := (2 - fg) mod
        for i in range(len(fg)):
            fg[i] = (-fg[i]) % mod
        fg[0] = (fg[0] + 2) % mod

        g = poly_mul_mod(g, fg, mod)[:m2]
        m = m2
    return g


def precompute_factorial_powers(n, r, mod=MOD):
    """
    fac_pow[i]  = (i!)^r mod
    inv_fac_pow[i] = (i!)^{-r} mod
    """
    fac_pow = [1] * (n + 1)
    for i in range(1, n + 1):
        fac_pow[i] = (fac_pow[i - 1] * pow(i, r, mod)) % mod

    inv_fac_pow = [1] * (n + 1)
    inv_fac_pow[n] = pow(fac_pow[n], mod - 2, mod)
    for i in range(n - 1, -1, -1):
        inv_fac_pow[i] = (inv_fac_pow[i + 1] * pow(i + 1, r, mod)) % mod

    return fac_pow, inv_fac_pow


def P_via_dp(k, r, n, fac_pow, inv_fac_pow, mod=MOD):
    """
    Direct O(m^2) DP on the block decomposition of n by size k.
    This is fast when m=ceil(n/k) is small.
    """
    q, rem = divmod(n, k)
    blocks = [k] * q + ([rem] if rem else [])
    m = len(blocks)

    f = [0] * (m + 1)
    f[0] = fac_pow[n]

    for i in range(1, m + 1):
        seg = 0
        acc = 0
        for j in range(i - 1, -1, -1):
            seg += blocks[j]
            term = f[j] * inv_fac_pow[seg] % mod
            if (i - j) & 1:
                acc += term
            else:
                acc -= term
        f[i] = acc % mod

    return f[m]


def P_via_inverse(k, r, n, fac_pow, inv_fac_pow, mod=MOD):
    """
    Faster method for small k / large q = n//k:
      - build p(x) = sum_{d=0..q} (-1)^d * ( (d*k)! )^{-r} * x^d
      - compute s(x) = 1/p(x) mod x^{q+1}
      - g[d] = (n!)^r * s[d]
      - adjust for remainder block (if any).
    """
    q, rem = divmod(n, k)

    # p(x) = Σ (-1)^d inv_fac_pow[d*k] x^d
    p = [0] * (q + 1)
    p[0] = 1
    for d in range(1, q + 1):
        coeff = inv_fac_pow[d * k]
        if d & 1:
            coeff = mod - coeff
        p[d] = coeff

    s = poly_inv_mod(p, q + 1, mod)
    g0 = fac_pow[n]
    g = [(g0 * si) % mod for si in s]

    if rem == 0:
        return g[q]

    # Final block of size rem
    ans = 0
    for t in range(q + 1):
        seg_len = (q - t) * k + rem
        term = g[t] * inv_fac_pow[seg_len] % mod
        if (q - t) & 1:
            ans -= term
        else:
            ans += term
    return ans % mod


def Q(n, mod=MOD):
    """
    Compute Q(n) = Σ_{k=1..n} P(k,n,n) mod mod.
    """
    r = n
    fac_pow, inv_fac_pow = precompute_factorial_powers(n, r, mod)

    # For k <= n//200, q is large enough that series inversion is worthwhile.
    # For k > n//200, m = ceil(n/k) <= 201, so the O(m^2) DP is tiny overall.
    k_inv_max = n // 200

    ans = 0
    for k in range(1, n + 1):
        q = n // k
        if k <= k_inv_max and q > 200:
            ans = (ans + P_via_inverse(k, r, n, fac_pow, inv_fac_pow, mod)) % mod
        else:
            ans = (ans + P_via_dp(k, r, n, fac_pow, inv_fac_pow, mod)) % mod
    return ans


def _run_asserts():
    # Test values from the problem statement
    fac, inv = precompute_factorial_powers(3, 2, MOD)
    assert P_via_dp(1, 2, 3, fac, inv, MOD) == 19

    fac, inv = precompute_factorial_powers(6, 4, MOD)
    assert P_via_dp(2, 4, 6, fac, inv, MOD) == 65508751

    fac, inv = precompute_factorial_powers(30, 5, MOD)
    assert P_via_dp(7, 5, 30, fac, inv, MOD) == 161858102

    assert Q(50, MOD) == 819573537


def solve():
    _run_asserts()
    return Q(50000, MOD)


if __name__ == "__main__":
    print(solve())
