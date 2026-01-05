#!/usr/bin/env python3
# Project Euler 502: Counting Castles
# Pure Python, no external libraries.

MOD = 1_000_000_007
INV2 = (MOD + 1) // 2

# ---------- Small exact arithmetic helpers (for assertions) ----------


def build_PQ_exact(h, y, deg_limit):
    # Build P_h(x), Q_h(x) over integers (no mod), truncated to deg_limit.
    if h <= 0:
        return [0], [1]
    P = [0, y]  # y*x
    Q = [1, -1]  # 1-x
    if deg_limit == 0:
        return [0], [1]

    for _ in range(2, h + 1):
        old_len = len(P)
        new_len = min(old_len + 1, deg_limit + 1)
        newP = [0] * new_len
        newQ = [0] * new_len
        newQ[0] = Q[0]

        for i in range(1, new_len):
            s = P[i - 1] + Q[i - 1]
            p_i = P[i] if i < old_len else 0
            q_i = Q[i] if i < old_len else 0
            newP[i] = y * (p_i + s)
            newQ[i] = q_i - s

        P, Q = newP, newQ

    return P, Q


def series_coeff_exact(P, Q, w):
    # Coefficient of x^w in P/Q, with Q[0]=1
    n = w + 1
    f = [0] * n
    for i in range(n):
        val = P[i] if i < len(P) else 0
        for j in range(1, min(i + 1, len(Q))):
            val -= Q[j] * f[i - j]
        f[i] = val
    return f[w]


def F_exact(w, h):
    # Exact F(w,h) for small parameters
    def E_leq(w, h):
        if h <= 0:
            return 0
        P1, Q1 = build_PQ_exact(h, 1, w)
        Pm, Qm = build_PQ_exact(h, -1, w)
        T = series_coeff_exact(P1, Q1, w)
        S = series_coeff_exact(Pm, Qm, w)
        return (T + S) // 2

    return E_leq(w, h) - E_leq(w, h - 1)


# ---------- NTT multiplication mod MOD via 3 primes (exact CRT) ----------

P1, G1 = 998244353, 3
P2, G2 = 1004535809, 3
P3, G3 = 469762049, 3


def modinv(a, mod):
    return pow(a, mod - 2, mod)


INV_P1_MOD_P2 = modinv(P1 % P2, P2)
P12 = P1 * P2
INV_P12_MOD_P3 = modinv(P12 % P3, P3)


def ntt(a, invert, mod, root):
    n = len(a)
    j = 0
    for i in range(1, n):
        bit = n >> 1
        while j & bit:
            j ^= bit
            bit >>= 1
        j ^= bit
        if i < j:
            a[i], a[j] = a[j], a[i]

    length = 2
    while length <= n:
        wlen = pow(root, (mod - 1) // length, mod)
        if invert:
            wlen = pow(wlen, mod - 2, mod)
        half = length >> 1
        for i in range(0, n, length):
            w = 1
            for j in range(i, i + half):
                u = a[j]
                v = (a[j + half] * w) % mod
                a[j] = (u + v) % mod
                a[j + half] = (u - v) % mod
                w = (w * wlen) % mod
        length <<= 1

    if invert:
        n_inv = pow(n, mod - 2, mod)
        for i in range(n):
            a[i] = (a[i] * n_inv) % mod


def convolve_mod(a, b):
    if not a or not b:
        return []
    n1, n2 = len(a), len(b)
    n = 1
    while n < n1 + n2 - 1:
        n <<= 1

    fa1 = [0] * n
    fb1 = [0] * n
    fa2 = [0] * n
    fb2 = [0] * n
    fa3 = [0] * n
    fb3 = [0] * n

    for i, x in enumerate(a):
        fa1[i] = x % P1
        fa2[i] = x % P2
        fa3[i] = x % P3
    for i, x in enumerate(b):
        fb1[i] = x % P1
        fb2[i] = x % P2
        fb3[i] = x % P3

    ntt(fa1, False, P1, G1)
    ntt(fb1, False, P1, G1)
    ntt(fa2, False, P2, G2)
    ntt(fb2, False, P2, G2)
    ntt(fa3, False, P3, G3)
    ntt(fb3, False, P3, G3)

    for i in range(n):
        fa1[i] = fa1[i] * fb1[i] % P1
        fa2[i] = fa2[i] * fb2[i] % P2
        fa3[i] = fa3[i] * fb3[i] % P3

    ntt(fa1, True, P1, G1)
    ntt(fa2, True, P2, G2)
    ntt(fa3, True, P3, G3)

    m = n1 + n2 - 1
    res = [0] * m
    for i in range(m):
        r1, r2, r3 = fa1[i], fa2[i], fa3[i]

        t2 = (r2 - r1) % P2
        t2 = (t2 * INV_P1_MOD_P2) % P2
        x12 = r1 + P1 * t2

        t3 = (r3 - (x12 % P3)) % P3
        t3 = (t3 * INV_P12_MOD_P3) % P3
        x = x12 + P12 * t3

        res[i] = x % MOD

    return res


def poly_mul_trunc(a, b, n):
    res = convolve_mod(a, b)
    if len(res) < n:
        res += [0] * (n - len(res))
    return res[:n]


def inv_series(q, n):
    invq = [pow(q[0], MOD - 2, MOD)]
    m = 1
    while m < n:
        m2 = min(2 * m, n)
        t = poly_mul_trunc(q[:m2], invq, m2)
        t[0] = (2 - t[0]) % MOD
        for i in range(1, m2):
            t[i] = (-t[i]) % MOD
        invq = poly_mul_trunc(invq, t, m2)
        m = m2
    return invq[:n]


# ---------- Build P/Q mod MOD for moderate sizes ----------


def build_PQ_mod(h, y, deg_limit, need_prev=False):
    if h <= 0:
        if need_prev:
            return [0], [1], [0], [1]
        return [0], [1]

    y_mod = 1 if y == 1 else MOD - 1
    P = [0, y_mod]
    Q = [1, MOD - 1]

    if h == 1:
        if need_prev:
            return [0], [1], P[: deg_limit + 1], Q[: deg_limit + 1]
        return P[: deg_limit + 1], Q[: deg_limit + 1]

    prevP = prevQ = None
    for step in range(2, h + 1):
        if need_prev and step == h:
            prevP, prevQ = P, Q

        old_len = len(P)
        new_len = min(old_len + 1, deg_limit + 1)
        newP = [0] * new_len
        newQ = [0] * new_len
        newQ[0] = 1

        if y == 1:
            for i in range(1, new_len):
                s = P[i - 1] + Q[i - 1]
                if s >= MOD:
                    s -= MOD
                p_i = P[i] if i < old_len else 0
                v = p_i + s
                if v >= MOD:
                    v -= MOD
                newP[i] = v

                q_i = Q[i] if i < old_len else 0
                qv = q_i - s
                if qv < 0:
                    qv += MOD
                newQ[i] = qv
        else:
            for i in range(1, new_len):
                s = P[i - 1] + Q[i - 1]
                if s >= MOD:
                    s -= MOD
                p_i = P[i] if i < old_len else 0
                v = p_i + s
                if v >= MOD:
                    v -= MOD
                newP[i] = 0 if v == 0 else MOD - v

                q_i = Q[i] if i < old_len else 0
                qv = q_i - s
                if qv < 0:
                    qv += MOD
                newQ[i] = qv

        P, Q = newP, newQ

    if need_prev:
        return prevP, prevQ, P, Q
    return P, Q


def series_coeff_mod(P, Q, w):
    n = w + 1
    if w < 2048:
        f = [0] * n
        for i in range(n):
            val = P[i] if i < len(P) else 0
            for j in range(1, min(i + 1, len(Q))):
                val -= Q[j] * f[i - j]
            f[i] = val % MOD
        return f[w]
    invQ = inv_series(Q[:n], n)
    prod = poly_mul_trunc(P[:n], invQ, n)
    return prod[w]


# ---------- Kitamasa for huge width, small height ----------


def kitamasa(init, coef, k):
    d = len(coef)
    if k < d:
        return init[k]

    def mul_reduce(a, b):
        tmp = [0] * (2 * d - 1)
        for i in range(d):
            ai = a[i]
            if ai:
                for j in range(d):
                    tmp[i + j] = (tmp[i + j] + ai * b[j]) % MOD

        for i in range(2 * d - 2, d - 1, -1):
            t = tmp[i]
            if t:
                for j in range(d):
                    tmp[i - 1 - j] = (tmp[i - 1 - j] + t * coef[j]) % MOD
        return tmp[:d]

    pol = [0] * d
    pol[0] = 1
    base = [0] * d
    base[1] = 1 if d > 1 else 0

    e = k
    while e:
        if e & 1:
            pol = mul_reduce(pol, base)
        base = mul_reduce(base, base)
        e >>= 1

    ans = 0
    for i in range(d):
        ans = (ans + pol[i] * init[i]) % MOD
    return ans


def coeff_large_w_small_h(w, h, y):
    # build full deg h polynomials, then compute coefficient via recurrence
    P, Q = build_PQ_mod(h, y, h)
    # compute f[0..h]
    f = []
    for n in range(h + 1):
        val = P[n] if n < len(P) else 0
        for j in range(1, min(n + 1, len(Q))):
            val -= Q[j] * (f[n - j])
        f.append(val % MOD)

    if w <= h:
        return f[w]

    # recurrence valid for n >= h+1:
    # f_n = -sum_{i=1..h} Q[i]*f_{n-i}
    coef = [(-Q[i]) % MOD for i in range(1, h + 1)]
    init = f[1 : h + 1]  # shift to make recurrence valid from index h onward
    return kitamasa(init, coef, w - 1)


# ---------- Matrix power for huge height, small width ----------


def poly_mul_small(a, b, limit):
    res = [0] * min(limit, len(a) + len(b) - 1)
    for i, ai in enumerate(a):
        if ai:
            for j, bj in enumerate(b):
                ij = i + j
                if ij >= limit:
                    break
                res[ij] = (res[ij] + ai * bj) % MOD
    return res


def poly_add_small(a, b, limit):
    res = [0] * limit
    for i in range(limit):
        res[i] = ((a[i] if i < len(a) else 0) + (b[i] if i < len(b) else 0)) % MOD
    return res


def mat_mul(A, B, limit):
    a00, a01 = A[0]
    a10, a11 = A[1]
    b00, b01 = B[0]
    b10, b11 = B[1]
    c00 = poly_add_small(
        poly_mul_small(a00, b00, limit), poly_mul_small(a01, b10, limit), limit
    )
    c01 = poly_add_small(
        poly_mul_small(a00, b01, limit), poly_mul_small(a01, b11, limit), limit
    )
    c10 = poly_add_small(
        poly_mul_small(a10, b00, limit), poly_mul_small(a11, b10, limit), limit
    )
    c11 = poly_add_small(
        poly_mul_small(a10, b01, limit), poly_mul_small(a11, b11, limit), limit
    )
    return [[c00, c01], [c10, c11]]


def mat_pow(M, e, limit):
    I = [
        [[1] + [0] * (limit - 1), [0] * limit],
        [[0] * limit, [1] + [0] * (limit - 1)],
    ]
    while e:
        if e & 1:
            I = mat_mul(I, M, limit)
        M = mat_mul(M, M, limit)
        e >>= 1
    return I


def apply_mat(M, P, Q, limit):
    a, b = M[0]
    c, d = M[1]
    Pn = poly_add_small(poly_mul_small(a, P, limit), poly_mul_small(b, Q, limit), limit)
    Qn = poly_add_small(poly_mul_small(c, P, limit), poly_mul_small(d, Q, limit), limit)
    return Pn, Qn


def coeff_large_h_small_w(w, h, y):
    if h <= 0:
        return 0
    limit = w + 1
    y_mod = 1 if y == 1 else MOD - 1

    # base (h=1)
    P = [0] * limit
    Q = [0] * limit
    if w >= 1:
        P[1] = y_mod
        Q[1] = MOD - 1
    Q[0] = 1

    if h == 1:
        return series_coeff_mod(P, Q, w)

    one = [1] + [0] * (limit - 1)
    xpoly = [0, 1] + [0] * (limit - 2) if limit >= 2 else [0]

    one_plus_x = one[:]
    if limit >= 2:
        one_plus_x[1] = (one_plus_x[1] + 1) % MOD

    y_one_plus_x = [(c * y_mod) % MOD for c in one_plus_x]
    y_x = [(c * y_mod) % MOD for c in xpoly]

    minus_x = [0] * limit
    if limit >= 2:
        minus_x[1] = MOD - 1

    one_minus_x = one[:]
    if limit >= 2:
        one_minus_x[1] = (one_minus_x[1] - 1) % MOD

    A = [[y_one_plus_x, y_x], [minus_x, one_minus_x]]
    Mp = mat_pow(A, h - 1, limit)
    Pn, Qn = apply_mat(Mp, P, Q, limit)
    return series_coeff_mod(Pn, Qn, w)


# ---------- Unified coefficient accessor ----------


def coeff_C_mod(w, h, y):
    if h <= 0:
        return 0
    # heuristic routing based on which dimension is huge
    if w <= 200 and h > 2000:
        return coeff_large_h_small_w(w, h, y)
    if h <= 200 and w > 2000:
        return coeff_large_w_small_h(w, h, y)

    P, Q = build_PQ_mod(h, y, w)
    return series_coeff_mod(P, Q, w)


def E_leq_mod(w, h):
    if h <= 0:
        return 0
    T = coeff_C_mod(w, h, 1)
    S = coeff_C_mod(w, h, -1)
    return ((T + S) * INV2) % MOD


def F_mod(w, h):
    return (E_leq_mod(w, h) - E_leq_mod(w, h - 1)) % MOD


# ---------- Main ----------


def main():
    # Assertions from the problem statement
    assert F_exact(4, 2) == 10
    assert F_exact(13, 10) == 3729050610636
    assert F_exact(10, 13) == 37959702514
    assert F_mod(100, 100) == 841913936

    ans = (F_mod(10**12, 100) + F_mod(10000, 10000) + F_mod(100, 10**12)) % MOD
    print(ans)


if __name__ == "__main__":
    main()
