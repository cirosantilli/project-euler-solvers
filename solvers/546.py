#!/usr/bin/env python3
"""
Project Euler 546 - The Floor's Revenge

We need:
  f_k(n) = sum_{i=0..n} f_k(floor(i/k)),  with f_k(0)=1
and compute:
  (sum_{k=2..10} f_k(10^14)) mod (1e9+7)

No external libraries are used.
"""

MOD = 1_000_000_007


def brute_fk(k: int, n: int) -> int:
    """
    Exact (big-int) computation for small n using the simplified recurrence:
      f(n) - f(n-1) = f(floor(n/k))
      => f(n) = f(n-1) + f(n//k)
    """
    f = [0] * (n + 1)
    f[0] = 1
    for i in range(1, n + 1):
        f[i] = f[i - 1] + f[i // k]
    return f[n]


def _build_coeffs(k: int, max_j: int):
    """
    Build coefficients for the linear "lifting" rule.

    Define A_0(n) = f_k(n), and for j>=1:
      A_j(n) = sum_{i=0..n} A_{j-1}(i)   (j-fold prefix sums)

    Then for each j>=0 and digit r in [0..k-1] there exist constants c_{j,r,p}
    such that for all n:
      A_j(k*n + r) = sum_{p=0..j+1} c_{j,r,p} * A_p(n)   (mod MOD)

    We compute these constants recursively.
    """
    coeffs = [None] * (max_j + 1)

    # Base: j=0
    # A_0(k*n + r) = k*A_1(n) + (r+1-k)*A_0(n)
    coeffs[0] = [None] * k
    for r in range(k):
        coeffs[0][r] = [(r + 1 - k) % MOD, k % MOD]  # [A0, A1]

    # Induction:
    # Assume for level (j-1): A_{j-1}(k*n + u) = sum_{p=0..j} a[u][p]*A_p(n)
    # Derive for level j by summing over complete blocks and the final partial block.
    for j in range(1, max_j + 1):
        coeffs[j] = [None] * k
        a = coeffs[j - 1]  # a[u] length j+1 for each u

        totals = [0] * (j + 1)  # totals[p] = sum_{u=0..k-1} a[u][p]
        for u in range(k):
            au = a[u]
            for p in range(j + 1):
                totals[p] = (totals[p] + au[p]) % MOD

        # prefix[r][p] = sum_{u=0..r} a[u][p]
        prefix = [[0] * (j + 1) for _ in range(k)]
        run = [0] * (j + 1)
        for u in range(k):
            au = a[u]
            for p in range(j + 1):
                run[p] = (run[p] + au[p]) % MOD
                prefix[u][p] = run[p]

        for r in range(k):
            pref = prefix[r]
            b = [0] * (j + 2)  # coefficients for A_0..A_{j+1}

            # p=0 has no "totals[p-1]" term
            b[0] = (pref[0] - totals[0]) % MOD
            # 1..j include the carry from A_{p}(n) coming via totals[p-1]*A_p(n)
            for p in range(1, j + 1):
                b[p] = (pref[p] - totals[p] + totals[p - 1]) % MOD
            # highest level (A_{j+1}) comes only from complete-block sums
            b[j + 1] = totals[j] % MOD

            coeffs[j][r] = b

    return coeffs


def _prepare_factorials(nmax: int):
    fact = [1] * (nmax + 1)
    for i in range(1, nmax + 1):
        fact[i] = fact[i - 1] * i % MOD
    invfact = [1] * (nmax + 1)
    invfact[nmax] = pow(fact[nmax], MOD - 2, MOD)
    for i in range(nmax, 0, -1):
        invfact[i - 1] = invfact[i] * i % MOD
    return fact, invfact


def _nCk(n: int, r: int, fact, invfact) -> int:
    if r < 0 or r > n:
        return 0
    return fact[n] * invfact[r] % MOD * invfact[n - r] % MOD


def fk_mod(k: int, N: int) -> int:
    """
    Compute f_k(N) mod MOD for huge N.

    We build the chain:
      n0=N, n1=floor(n0/k), n2=floor(n1/k), ... until nd<k.
    At depth i we maintain the vector [A_0(ni), A_1(ni), ..., A_i(ni)].
    The base (nd<k) is easy because then f_k(x)=x+1 for x<=nd, so:
      A_j(nd) = C(nd + j + 1, j + 1)
    Then we lift back up using the precomputed coefficients.
    """
    ns = [N]
    while ns[-1] >= k:
        ns.append(ns[-1] // k)
    d = len(ns) - 1  # maximum level needed

    coeffs = _build_coeffs(k, d)

    # Factorials are only needed up to about (k-1) + (d+1) + 1, which is small (< 100).
    fact, invfact = _prepare_factorials((k - 1) + d + 10)

    base = ns[d]  # base < k
    vec = [_nCk(base + j + 1, j + 1, fact, invfact) for j in range(d + 1)]

    # Lift from depth i+1 to depth i
    for i in range(d - 1, -1, -1):
        r = ns[i] % k
        m_vec = vec  # length i+2
        new = [0] * (i + 1)
        for j in range(i + 1):
            co = coeffs[j][r]  # length j+2
            s = 0
            for p, c in enumerate(co):
                s = (s + c * m_vec[p]) % MOD
            new[j] = s
        vec = new

    return vec[0]


def solve() -> int:
    N = 10**14
    ans = 0
    for k in range(2, 11):
        ans = (ans + fk_mod(k, N)) % MOD
    return ans


if __name__ == "__main__":
    # Test values from the problem statement (exact, not modulo).
    assert brute_fk(5, 10) == 18
    assert brute_fk(7, 100) == 1003
    assert brute_fk(2, 10**3) == 264830889564

    print(solve())
