#!/usr/bin/env python3
"""
Project Euler 544 - Chromatic Conundrum

Compute S(9, 10, 1112131415) mod 1e9+7 where
F(r,c,n) is the number of proper colourings of an r x c grid with at most n colours,
and S(r,c,n) = sum_{k=1..n} F(r,c,k).

No external libraries are used.
"""

MOD = 1_000_000_007
EMPTY = -1


def poly_eval(coeffs, x, mod=MOD):
    """Evaluate polynomial sum_{i>=0} coeffs[i] * x^i mod mod."""
    x %= mod
    res = 0
    p = 1
    for a in coeffs:
        res = (res + a * p) % mod
        p = (p * x) % mod
    return res


def lagrange_eval_0_to_n(values, x, mod=MOD):
    """
    Given values[i] = f(i) for i=0..n and deg(f) <= n, evaluate f(x) mod mod.
    Uses O(n) Lagrange interpolation tailored to x_i = i.
    """
    n = len(values) - 1
    if 0 <= x <= n:
        return values[x] % mod

    x %= mod

    # factorials
    fac = [1] * (n + 1)
    for i in range(1, n + 1):
        fac[i] = (fac[i - 1] * i) % mod
    invfac = [1] * (n + 1)
    invfac[n] = pow(fac[n], mod - 2, mod)
    for i in range(n, 0, -1):
        invfac[i - 1] = (invfac[i] * i) % mod

    # prefix/suffix products of (x - i)
    pre = [1] * (n + 2)
    for i in range(n + 1):
        pre[i + 1] = (pre[i] * (x - i)) % mod
    suf = [1] * (n + 2)
    for i in range(n, -1, -1):
        suf[i] = (suf[i + 1] * (x - i)) % mod

    ans = 0
    for i in range(n + 1):
        num = (pre[i] * suf[i + 1]) % mod
        den = (invfac[i] * invfac[n - i]) % mod
        if (n - i) & 1:
            den = (-den) % mod
        ans = (ans + values[i] * num % mod * den) % mod
    return ans


def chromatic_poly_grid(r, c, mod=MOD):
    """
    Return coefficients (power basis) of the chromatic polynomial P(q) = F(r,c,q) mod mod
    for an r x c grid graph.

    Frontier DP:
      - sweep column-major, replacing one frontier position at a time,
      - keep a canonical relabelling of colours on the frontier (up to permutation),
      - assigning a brand-new colour contributes a factor (q - m) where m is the number
        of distinct frontier colours currently present, which we track symbolically as a polynomial.
    """
    # Canonicalise a state: relabel colours by first appearance, keep EMPTY as-is.
    canon_cache = {}

    def canon(state):
        res = canon_cache.get(state)
        if res is not None:
            return res
        # Labels are always in [-1..r] here, so a small list map is fastest.
        mp = [-1] * (r + 1)
        nxt = 0
        out = [0] * r
        for idx, x in enumerate(state):
            if x == EMPTY:
                out[idx] = EMPTY
            else:
                y = mp[x]
                if y == -1:
                    y = nxt
                    mp[x] = y
                    nxt += 1
                out[idx] = y
        res = tuple(out)
        canon_cache[state] = res
        return res

    # Cache transitions "set frontier position i to label lab (including lab=m as the new label)"
    trans_cache = {}

    def trans(st, i):
        key = (st, i)
        res = trans_cache.get(key)
        if res is not None:
            return res
        mx = max(st)
        m = 0 if mx == EMPTY else mx + 1  # number of distinct labels 0..m-1
        base = list(st)
        nexts = [None] * (m + 1)
        for lab in range(m + 1):
            base[i] = lab
            nexts[lab] = canon(tuple(base))
        base[i] = st[i]
        res = (m, nexts)
        trans_cache[key] = res
        return res

    # Cache forgetting (removing) a frontier position
    forget_cache = {}

    def forget(st, i):
        key = (st, i)
        res = forget_cache.get(key)
        if res is not None:
            return res
        base = list(st)
        base[i] = EMPTY
        res = canon(tuple(base))
        forget_cache[key] = res
        return res

    def add_poly(tgt, poly):
        """tgt += poly (in place)."""
        if len(tgt) < len(poly):
            tgt.extend([0] * (len(poly) - len(tgt)))
        for j, v in enumerate(poly):
            x = tgt[j] + v
            if x >= mod:
                x -= mod
            tgt[j] = x

    def add_q_minus_m_mul(tgt, poly, m):
        """tgt += (q - m) * poly (in place), where q is the polynomial variable."""
        need = len(poly) + 1
        if len(tgt) < need:
            tgt.extend([0] * (need - len(tgt)))
        mm = m % mod
        for j, v in enumerate(poly):
            # coefficient for q^j gets -m*v
            tgt[j] = (tgt[j] - (mm * v) % mod) % mod
            # coefficient for q^(j+1) gets +v
            x = tgt[j + 1] + v
            if x >= mod:
                x -= mod
            tgt[j + 1] = x

    start = tuple([EMPTY] * r)
    dp = {start: [1]}  # state -> polynomial in q

    for col in range(c):
        for row in range(r):
            i = row
            has_up = row > 0
            has_left = col > 0
            ndp = {}
            for st, poly in dp.items():
                m, nexts = trans(st, i)
                up = st[i - 1] if has_up else -2
                left = st[i] if has_left else -2

                # Reuse an existing label
                for lab in range(m):
                    if lab == up or lab == left:
                        continue
                    ns = nexts[lab]
                    tgt = ndp.get(ns)
                    if tgt is None:
                        tgt = []
                        ndp[ns] = tgt
                    add_poly(tgt, poly)

                # Pick a colour not currently on the frontier: (q - m) choices
                ns = nexts[m]
                tgt = ndp.get(ns)
                if tgt is None:
                    tgt = []
                    ndp[ns] = tgt
                add_q_minus_m_mul(tgt, poly, m)

            dp = ndp

    # After the last column, no vertices have future edges, so forget the frontier.
    for i in range(r):
        ndp = {}
        for st, poly in dp.items():
            ns = forget(st, i)
            tgt = ndp.get(ns)
            if tgt is None:
                tgt = []
                ndp[ns] = tgt
            add_poly(tgt, poly)
        dp = ndp

    return dp[start]


def solve():
    # Asserts from the problem statement
    p22 = chromatic_poly_grid(2, 2)
    assert poly_eval(p22, 3) == 18
    assert poly_eval(p22, 20) == 130340

    p34 = chromatic_poly_grid(3, 4)
    assert poly_eval(p34, 6) == 102923670

    p44 = chromatic_poly_grid(4, 4)
    s44 = sum(poly_eval(p44, k) for k in range(1, 16)) % MOD
    assert s44 == 325951319

    # Target
    r, c, n = 9, 10, 1112131415
    p = chromatic_poly_grid(r, c)

    # S(r,c,n) is a polynomial in n of degree (r*c)+1, so for 9*10=90 we need values 0..91.
    deg = r * c
    m = deg + 1  # 91
    prefix = [0] * (m + 1)  # prefix[t] = sum_{k=1..t} P(k)
    acc = 0
    for k in range(1, m + 1):
        acc = (acc + poly_eval(p, k)) % MOD
        prefix[k] = acc

    ans = lagrange_eval_0_to_n(prefix, n)
    print(ans)


if __name__ == "__main__":
    solve()
