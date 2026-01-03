#!/usr/bin/env python3
"""
Project Euler 427: n-sequences

We need:
  f(n) = sum over all sequences S of length n with values in {1..n} of L(S),
where L(S) is the longest run of equal consecutive values.

Compute f(7_500_000) mod 1_000_000_009.

No external libraries are used.
"""

from __future__ import annotations

from array import array

MOD = 1_000_000_009


def f_via_compositions(n: int) -> int:
    """
    Exact f(n) for small n using run-length compositions.

    Any sequence can be described by a composition of n (run lengths).
    For a composition with b parts, the number of sequences realizing it is:
        n * (n-1)^(b-1)
    because the first run can be any value (n choices) and each next run must
    differ from the previous ((n-1) choices).

    Then f(n) is the sum over compositions of:
        [number of sequences] * [max part length]
    """
    if n <= 0:
        return 0
    total = 0
    # A composition of n is determined by the cut set among the n-1 gaps.
    # mask bit i == 1 means a cut after position i (0-indexed gap).
    for mask in range(1 << (n - 1)):
        parts = 1
        cur = 1
        mx = 1
        for i in range(n - 1):
            if (mask >> i) & 1:
                if cur > mx:
                    mx = cur
                parts += 1
                cur = 1
            else:
                cur += 1
        if cur > mx:
            mx = cur

        weight = n * pow(n - 1, parts - 1)
        total += weight * mx
    return total


def _poly_mul_mod(
    p: list[int],
    q: list[int],
    k: int,
    n_mod: int,
    a_mod: int,
    mod: int,
) -> list[int]:
    """
    Multiply polynomials p and q modulo the sparse characteristic polynomial:
        x^k - n*x^(k-1) - a = 0
    i.e. x^k ≡ n*x^(k-1) + a  (mod P)

    Degree of p,q < k. Returned polynomial has degree < k.

    This is used only for small k (an optional micro-optimization).
    """
    lp, lq = len(p), len(q)
    r = [0] * (lp + lq - 1)
    for i in range(lp):
        pi = p[i]
        if pi:
            for j in range(lq):
                r[i + j] = (r[i + j] + pi * q[j]) % mod

    # Reduce degrees >= k using x^i = x^(i-k) * x^k ≡ n*x^(i-1) + a*x^(i-k)
    for deg in range(len(r) - 1, k - 1, -1):
        val = r[deg]
        if val:
            r[deg - 1] = (r[deg - 1] + val * n_mod) % mod
            r[deg - k] = (r[deg - k] + val * a_mod) % mod
            r[deg] = 0

    if len(r) < k:
        r.extend([0] * (k - len(r)))
    return r[:k]


def _rec_term_sparse(n: int, k: int, idx: int, mod: int = MOD) -> int:
    """
    Compute h_idx for the recurrence (order k):
        h_0 = 1
        h_i = n^i  for 0 <= i < k
        h_i = n*h_{i-1} + (1-n)*h_{i-k}   for i >= k

    Using polynomial exponentiation to compute x^idx mod P(x), where:
        P(x) = x^k - n*x^(k-1) - (1-n).

    Only intended for small k.
    """
    if idx < 0:
        return 0
    if k <= 0:
        raise ValueError("k must be positive")
    n_mod = n % mod
    a_mod = (1 - n_mod) % mod

    # initial terms h_0..h_{k-1} are n^i
    if idx < k:
        return pow(n_mod, idx, mod)

    init = [1] * k
    pwr = 1
    for i in range(1, k):
        pwr = (pwr * n_mod) % mod
        init[i] = pwr

    # Compute poly representing x^idx mod P(x)
    res = [1]  # 1
    base = [0, 1]  # x
    e = idx
    while e:
        if e & 1:
            res = _poly_mul_mod(res, base, k, n_mod, a_mod, mod)
        base = _poly_mul_mod(base, base, k, n_mod, a_mod, mod)
        e >>= 1

    # Dot with initial vector
    ans = 0
    for i in range(k):
        ans = (ans + res[i] * init[i]) % mod
    return ans


def solve_euler_427(n: int = 7_500_000, mod: int = MOD, small_k_opt: int = 0) -> int:
    """
    Compute f(n) mod mod.

    Core identities:
      Let A_k be the number of sequences with L(S) < k (i.e. no run of length k).
      Then:
          f(n) = n^{n+1} - sum_{k=1..n} A_k

      For each k>=1, define h_N(k) as the coefficient sequence:
          h_0 = 1, h_i = n^i for i<k,
          h_i = n*h_{i-1} + (1-n)*h_{i-k} for i>=k.
      Then:
          A_k = h_n(k) - h_{n-k}(k).

      A closed form for h_N(k) is:
          h_N(k) = sum_{t=0..floor(N/k)} n^{N-tk} (1-n)^t * C(N-tk+t, t).

    We evaluate all A_k modulo mod using factorial / inverse factorial precomputation.
    Complexity: O(n log n) arithmetic operations due to sum_{k} floor(n/k).

    small_k_opt:
      If >0, use the sparse-recurrence polynomial method for k<=small_k_opt to
      skip the largest inner summations. Set to 0 for the simplest approach.
    """
    if n <= 0:
        return 0
    if mod <= 1:
        raise ValueError("mod must be > 1")

    n_mod = n % mod
    a_mod = (1 - n_mod) % mod

    # factorials mod mod
    fac = array("I", [1]) * (n + 1)
    for i in range(1, n + 1):
        fac[i] = (fac[i - 1] * i) % mod

    # inverse factorials
    ifac = array("I", [0]) * (n + 1)
    ifac[n] = pow(int(fac[n]), mod - 2, mod)
    for i in range(n, 0, -1):
        ifac[i - 1] = (ifac[i] * i) % mod

    # Precompute:
    #   A[m] = n^m / m!   (mod)
    #   B[t] = (1-n)^t / t!  (mod)
    # so that:
    #   n^{m} (1-n)^t * C(m+t, t)  == fac[m+t] * A[m] * B[t] (mod)
    A = array("I", [0]) * (n + 1)
    B = array("I", [0]) * (n + 1)
    pow_n = 1
    pow_a = 1
    for i in range(0, n + 1):
        if i == 0:
            pow_n = 1
            pow_a = 1
        else:
            pow_n = (pow_n * n_mod) % mod
            pow_a = (pow_a * a_mod) % mod
        A[i] = (pow_n * ifac[i]) % mod
        B[i] = (pow_a * ifac[i]) % mod

    # Free inverse factorial array; it's no longer needed.
    del ifac

    sum_Ak = 0

    # A_1 = 0 always; start from k=2.
    start_k = 2

    # Optional: handle very small k using sparse recurrence evaluation (no inner sums).
    if small_k_opt and small_k_opt >= 2:
        opt_end = min(small_k_opt, n)
        for k in range(2, opt_end + 1):
            hn = _rec_term_sparse(n, k, n, mod)
            hnk = _rec_term_sparse(n, k, n - k, mod)
            sum_Ak += (hn - hnk) % mod
        start_k = opt_end + 1
        sum_Ak %= mod

    fac_local = fac
    A_local = A
    B_local = B
    mod_local = mod

    for k in range(start_k, n + 1):
        q = n // k
        km1 = k - 1

        m = n
        idx = n  # idx == m + t == n - t*(k-1)
        res = 0

        # t = 0..q-1 contribute to both solve(n,k) and solve(n-k,k)
        for t in range(q):
            bt = B_local[t]

            tmp = (fac_local[idx] * A_local[m]) % mod_local
            res += (tmp * bt) % mod_local

            tmp2 = (fac_local[idx - k] * A_local[m - k]) % mod_local
            res -= (tmp2 * bt) % mod_local

            m -= k
            idx -= km1

        # last term t=q appears only in solve(n,k)
        tmp = (fac_local[idx] * A_local[m]) % mod_local
        res += (tmp * B_local[q]) % mod_local

        sum_Ak += res % mod_local
        # occasional reduction keeps integers small
        if (k & 1023) == 0:
            sum_Ak %= mod_local

    sum_Ak %= mod
    return (pow(n_mod, n + 1, mod) - sum_Ak) % mod


def main() -> None:
    # Test values from the problem statement:
    assert f_via_compositions(3) == 45
    assert f_via_compositions(7) == 1403689
    assert f_via_compositions(11) == 481496895121

    # Main answer:
    print(solve_euler_427(7_500_000, MOD, small_k_opt=0))


if __name__ == "__main__":
    main()
