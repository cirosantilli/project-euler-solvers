#!/usr/bin/env python3
"""
Project Euler 506 - Clock Sequence

We parse the infinite repeating digit stream 123432123432...
into values v_n such that the sum of digits in v_n equals n.

We need S(10^14) mod 123454321, where S(n) = sum_{k=1..n} v_k.
"""

MOD = 123454321
DIGITS = (1, 2, 3, 4, 3, 2)
L = 6


def pow_sum(base: int, n: int, mod: int) -> tuple[int, int]:
    """
    Returns (base^n mod mod, sum_{k=0..n-1} base^k mod mod)
    via exponentiation by squaring (no modular inverses needed).
    """
    if n == 0:
        return 1 % mod, 0
    if n == 1:
        return base % mod, 1 % mod
    if n % 2 == 0:
        p, s = pow_sum(base, n // 2, mod)
        p2 = (p * p) % mod
        s2 = (s * (1 + p)) % mod  # s + p*s
        return p2, s2
    # odd
    p, s = pow_sum(base, n - 1, mod)
    p2 = (p * base) % mod
    s2 = (s + p) % mod
    return p2, s2


def pow_sum_idx(base: int, n: int, mod: int) -> tuple[int, int, int]:
    """
    Returns (base^n mod mod,
             S = sum_{k=0..n-1} base^k mod mod,
             T = sum_{k=0..n-1} k*base^k mod mod)
    using exponentiation by squaring.
    """
    if n == 0:
        return 1 % mod, 0, 0
    if n == 1:
        return base % mod, 1 % mod, 0
    if n % 2 == 0:
        p, s, t = pow_sum_idx(base, n // 2, mod)
        m = n // 2

        p2 = (p * p) % mod
        s2 = (s * (1 + p)) % mod

        # T(2m) = T(m) + sum_{j=0..m-1} (j+m) * base^{j+m}
        #       = t + p*(t + m*s) = t*(1+p) + p*m*s
        t2 = (t * (1 + p) + p * (m % mod) * s) % mod
        return p2, s2, t2

    # odd: n = (n-1)+1
    p, s, t = pow_sum_idx(base, n - 1, mod)
    p2 = (p * base) % mod
    s2 = (s + p) % mod
    t2 = (t + ((n - 1) % mod) * p) % mod
    return p2, s2, t2


def brute_prefix(n_max: int, mod: int) -> tuple[int, int]:
    """
    Brute-generate v_1..v_{n_max} by streaming digits.
    Returns (S(n_max) mod mod, next stream position in [0..5]).
    """
    pos = 0
    total = 0
    for n in range(1, n_max + 1):
        s = 0
        val = 0
        while s < n:
            d = DIGITS[pos]
            pos = (pos + 1) % L
            s += d
            val = (val * 10 + d) % mod
        # The construction guarantees exact equality.
        if s != n:
            raise RuntimeError("Digit-sum overshoot (should be impossible).")
        total = (total + val) % mod
    return total, pos


def build_tables():
    """
    Precompute, for each start position:
      - rotated 6-digit block as int (length 6)
      - prefix sums and prefix ints for lengths 0..6
      - for each residue mod 15, the optimal prefix length i (1..6) to finish a chunk,
        and the corresponding digit-sum prefix p.
    """
    rot = []
    block = [0] * L
    prefix_sum = [[0] * 7 for _ in range(L)]
    prefix_int = [[0] * 7 for _ in range(L)]

    for pos in range(L):
        r = [DIGITS[(pos + i) % L] for i in range(L)]
        rot.append(r)

        b = 0
        s = 0
        v = 0
        prefix_sum[pos][0] = 0
        prefix_int[pos][0] = 0
        for i, d in enumerate(r, start=1):
            b = b * 10 + d
            s += d
            v = v * 10 + d
            prefix_sum[pos][i] = s
            prefix_int[pos][i] = v
        block[pos] = b

    best_i = [[None] * 15 for _ in range(L)]
    best_p = [[None] * 15 for _ in range(L)]

    # For n >= 15, the shortest way to reach digit-sum n from a fixed start position
    # is determined only by n mod 15 (because each full 6-digit cycle adds 15 to the sum).
    for pos in range(L):
        for r in range(15):
            candidates = [i for i in range(1, 7) if prefix_sum[pos][i] % 15 == r]
            if not candidates:
                continue

            # Compare lengths:
            # len = 6*((n - p)/15) + i, where p is the prefix digit-sum at length i.
            # For fixed residue class, minimizing len is equivalent to minimizing (5*i - 2*p).
            def key(i: int) -> tuple[int, int]:
                p = prefix_sum[pos][i]
                return (5 * i - 2 * p, i)

            i_best = min(candidates, key=key)
            best_i[pos][r] = i_best
            best_p[pos][r] = prefix_sum[pos][i_best]

    return block, prefix_sum, prefix_int, best_i, best_p


def solve(N: int) -> int:
    """
    Compute S(N) mod MOD.
    """
    # Handle small prefix directly to reach the stable regime (n >= 15).
    n0 = 15
    small = min(N, n0 - 1)
    ans, pos = brute_prefix(small, MOD)
    if N <= n0 - 1:
        return ans

    block, prefix_sum, prefix_int, best_i, best_p = build_tables()

    # Build the 15-term state cycle starting at n=15 (it returns to the same stream position).
    P = 15
    seq = []
    cur_pos = pos
    for j in range(P):
        n = n0 + j
        r = n % 15
        i = best_i[cur_pos][r]
        p = best_p[cur_pos][r]
        if i is None or p is None:
            raise RuntimeError(
                "Incompatible state (should not happen in the true sequence)."
            )
        b = block[cur_pos]
        pre = prefix_int[cur_pos][i]
        seq.append((n, cur_pos, i, p, b, pre))
        cur_pos = (cur_pos + i) % L

    if cur_pos != pos:
        raise RuntimeError("Expected a 15-step cycle in the stream position.")

    total_terms = N - (n0 - 1)  # number of terms from n=15..N inclusive
    K, rem = divmod(total_terms, P)  # K full 15-term cycles, then rem extra terms

    a = pow(10, 6, MOD)  # each full digit-block is 6 digits

    # Precompute 10^i (i in 0..6).
    pow10 = [1] * 7
    for i in range(1, 7):
        pow10[i] = pow(10, i, MOD)

    # H(K) = sum_{m=0..K-1} sum_{k=0..m-1} a^k
    #      = sum_{k=0..K-2} (K-1-k) a^k
    if K <= 1:
        H = 0
    else:
        n = K - 1
        _, S_a, T_a = pow_sum_idx(a, n, MOD)  # sums up to a^(n-1)
        H = ((n % MOD) * S_a - T_a) % MOD

    # sum_aK = sum_{k=0..K-1} a^k
    _, sum_aK, _ = pow_sum_idx(a, K, MOD)

    K_mod = K % MOD

    # Add contributions of full cycles.
    if K:
        for n, _pos, i, p, b, pre in seq:
            t0 = (n - p) // 15  # always 0 or 1 within the base 15-term cycle
            at0, G0 = pow_sum(a, t0, MOD)  # at0=a^t0, G0=sum_{u=0..t0-1} a^u

            # delta=1 (t increases by 1 each 15-term cycle), and G(1)=1.
            # Sum_{m=0..K-1} G(t0+m) = K*G0 + a^t0 * H
            sumG = (K_mod * G0 + at0 * H) % MOD

            term_sum = (b * pow10[i] % MOD) * sumG % MOD
            term_sum = (term_sum + pre * K_mod) % MOD
            ans = (ans + term_sum) % MOD

    # Add remainder terms (cycle index = K, so t increases by K).
    if rem:
        for idx in range(rem):
            (n, _pos, i, p, b, pre) = seq[idx]
            t0 = (n - p) // 15
            at0, G0 = pow_sum(a, t0, MOD)
            # G(t0+K) = G0 + a^t0 * sum_{k=0..K-1} a^k
            G = (G0 + at0 * sum_aK) % MOD
            v = (b * pow10[i] % MOD) * G % MOD
            v = (v + pre) % MOD
            ans = (ans + v) % MOD

    return ans


def main() -> None:
    # Problem statement checks:
    assert solve(11) == 36120
    assert solve(1000) == 18232686

    print(solve(10**14))


if __name__ == "__main__":
    main()
