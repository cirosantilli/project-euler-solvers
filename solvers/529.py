#!/usr/bin/env python3
"""Project Euler 529: 10-substrings

A 10-substring is a contiguous substring whose digit-sum is 10.
A number is 10-substring-friendly if every digit lies in at least one 10-substring.

Let T(n) be the count of 10-substring-friendly numbers from 1 to 10^n (inclusive).
We need T(10^18) mod 1_000_000_007.

This implementation contains **no precomputed tables**. It builds a DFA for
zero-free friendly strings (digits 1..9), derives a linear recurrence using
Berlekamp–Massey, then evaluates the binomial transform using polynomial
exponentiation in the quotient ring.
"""

from __future__ import annotations


MOD = 1_000_000_007
N = 10 ** 18


# -------------------- DFA for zero-free friendly strings --------------------

def _next_state(digs: tuple[int, ...], mask: int, d: int):
    """Append digit d (1..9) to a state.

    State representation:
      - digs: last m digits (oldest -> newest), where m in [0..9]
      - mask: m-bit mask (bit 0 is newest digit) indicating which of these digits
              are already covered by some 10-substring ending at or before the
              current position.

    Returns (new_digs, new_mask) or None if the transition is invalid.
    """
    digs2 = digs + (d,)
    m2 = len(digs2)
    mask2 = mask << 1  # existing digits become 1 step older; new digit has bit 0 = 0

    # Only new 10-substrings created now are those ending at the newest digit.
    # With digits 1..9, suffix sums strictly increase, so at most one suffix hits 10.
    s = 0
    for l in range(1, m2 + 1):
        s += digs2[-l]
        if s == 10:
            mask2 |= (1 << l) - 1  # cover the newest l digits
            break
        if s > 10:
            break

    if m2 == 10:
        # Oldest digit (bit 9) must be covered now; otherwise it can never be.
        if ((mask2 >> 9) & 1) == 0:
            return None
        # Drop the oldest digit, keep the newest 9.
        return digs2[1:], mask2 & ((1 << 9) - 1)
    else:
        return digs2, mask2


def _build_dfa():
    """Build reachable DFA states and transitions for digits 1..9."""
    start = ((), 0)
    state_id: dict[tuple[tuple[int, ...], int], int] = {start: 0}
    states: list[tuple[tuple[int, ...], int]] = [start]
    trans: list[list[int]] = []  # filled in later

    q = 0
    while q < len(states):
        digs, mask = states[q]
        row = [-1] * 9
        for di, digit in enumerate(range(1, 10)):
            nxt = _next_state(digs, mask, digit)
            if nxt is None:
                continue
            if nxt not in state_id:
                state_id[nxt] = len(states)
                states.append(nxt)
            row[di] = state_id[nxt]
        trans.append(row)
        q += 1

    accept_ids: list[int] = []
    outs: list[list[int]] = []
    for sid, (digs, mask) in enumerate(states):
        m = len(digs)
        if m > 0 and mask == (1 << m) - 1:
            accept_ids.append(sid)
        out = []
        for j in trans[sid]:
            if j != -1:
                out.append(j)
        outs.append(out)

    return outs, accept_ids


def _generate_E_terms(outs: list[list[int]], accept_ids: list[int], num_terms: int) -> list[int]:
    """Generate E(k) for k=0..num_terms-1 mod MOD, given a DFA."""
    S = len(outs)

    dp = [0] * S
    dp[0] = 1  # start state

    seq = [0] * num_terms
    # E(0) = 0 by definition
    for t in range(1, num_terms):
        ndp = [0] * S
        # transition
        for i, v in enumerate(dp):
            if v:
                for j in outs[i]:
                    x = ndp[j] + v
                    if x >= MOD:
                        x -= MOD
                    ndp[j] = x
        dp = ndp

        # accept sum
        total = 0
        for i in accept_ids:
            total += dp[i]
            if total >= MOD:
                total -= MOD
        seq[t] = total
    return seq


# -------------------- Berlekamp–Massey (mod prime) --------------------

def _berlekamp_massey(seq: list[int]):
    """Return minimal recurrence for seq over mod MOD.

    Returns REC where:
      seq[n] = sum_{i=1..L} REC[i-1] * seq[n-i]   for n >= L
    """
    C = [1]
    B = [1]
    L = 0
    m = 1
    b = 1

    for n in range(len(seq)):
        # discrepancy d = sum_{i=0..L} C[i] * seq[n-i]
        d = seq[n]
        for i in range(1, L + 1):
            d = (d + C[i] * seq[n - i]) % MOD
        if d == 0:
            m += 1
            continue

        coef = d * pow(b, MOD - 2, MOD) % MOD
        T = C[:]
        need = L + m
        if len(C) < need + 1:
            C.extend([0] * (need + 1 - len(C)))
        for i in range(len(B)):
            C[i + m] = (C[i + m] - coef * B[i]) % MOD
        if 2 * L <= n:
            L2 = n + 1 - L
            B = T
            L = L2
            b = d
            m = 1
        else:
            m += 1

    # Convert C to REC
    REC = [(-C[i]) % MOD for i in range(1, L + 1)]
    return REC


# -------------------- Big-int packed convolution --------------------

BASE_BITS = 72
BASE_MASK = (1 << BASE_BITS) - 1


def _pack(coeffs: list[int]) -> int:
    """Pack coefficients into one big integer in base 2^BASE_BITS (little-endian)."""
    x = 0
    for c in reversed(coeffs):
        x = (x << BASE_BITS) + c
    return x


def _unpack(x: int, n: int) -> list[int]:
    """Unpack n coefficients from packed big integer."""
    out = [0] * n
    for i in range(n):
        out[i] = x & BASE_MASK
        x >>= BASE_BITS
    return out


def _conv(a: list[int], b: list[int]) -> list[int]:
    """Exact convolution of a and b (no mod)."""
    return _unpack(_pack(a) * _pack(b), len(a) + len(b) - 1)


def _conv_with_const(a: list[int], packed_b: int, len_b: int) -> list[int]:
    """Exact convolution where the second operand is already packed."""
    return _unpack(_pack(a) * packed_b, len(a) + len_b - 1)


def _poly_inv_mod_xk(f: list[int], k: int) -> list[int]:
    """Invert f modulo x^k (Newton iteration), assuming f[0] != 0."""
    inv0 = pow(f[0], MOD - 2, MOD)
    g = [inv0]
    m = 1
    while m < k:
        m2 = 2 * m
        if m2 > k:
            m2 = k

        # t = f*g mod x^m2
        t = _conv(f[:m2], g)[:m2]
        for i in range(m2):
            t[i] %= MOD

        # t = (2 - t) mod MOD
        t[0] = (2 - t[0]) % MOD
        for i in range(1, m2):
            t[i] = (-t[i]) % MOD

        # g = g*t mod x^m2
        g = _conv(g, t)[:m2]
        for i in range(m2):
            g[i] %= MOD
        m = m2
    return g


# -------------------- Quotient-ring poly arithmetic --------------------

def _prepare_ring(REC: list[int]):
    """Build modulus and helpers for quotient ring mod characteristic polynomial."""
    L = len(REC)
    K = L - 1

    # C(x) = x^L - REC[0] x^(L-1) - ... - REC[L-1]
    C = [0] * (L + 1)
    C[L] = 1
    for i, c in enumerate(REC):
        C[L - 1 - i] = (-c) % MOD

    CR = list(reversed(C))  # CR[0] == 1
    INV_CR = _poly_inv_mod_xk(CR, K)

    packed_inv_cr = _pack(INV_CR)
    packed_c = _pack(C)
    len_inv_cr = len(INV_CR)
    len_c = len(C)

    def poly_mod(P: list[int]) -> list[int]:
        # Reduce P (len 2L-1) modulo C to degree < L
        PR = P[::-1]
        q_rev = _conv_with_const(PR[:K], packed_inv_cr, len_inv_cr)[:K]
        for i in range(K):
            q_rev[i] %= MOD
        q = q_rev[::-1]

        QC = _conv_with_const(q, packed_c, len_c)
        R = [0] * L
        for i in range(L):
            R[i] = (P[i] - QC[i]) % MOD
        return R

    def poly_mul_mod(a: list[int], b: list[int]) -> list[int]:
        P = _conv(a, b)  # len 2L-1
        for i in range(2 * L - 1):
            P[i] %= MOD
        return poly_mod(P)

    def poly_pow(base: list[int], exp: int) -> list[int]:
        res = [0] * L
        res[0] = 1
        b = base
        e = exp
        while e:
            if e & 1:
                res = poly_mul_mod(res, b)
            e >>= 1
            if e:
                b = poly_mul_mod(b, b)
        return res

    return L, poly_pow


# -------------------- T(n) computation --------------------

def _binom_transform_prefix(E: list[int], n: int) -> int:
    """Directly compute sum_{k=0..n} C(n,k)*E[k] mod MOD for small n."""
    total = 0
    comb = 1
    for k in range(n + 1):
        total = (total + comb * E[k]) % MOD
        if k != n:
            comb = comb * (n - k) % MOD
            comb = comb * pow(k + 1, MOD - 2, MOD) % MOD
    return total


def solve(n: int = N) -> int:
    # Build DFA and generate enough terms to recover a recurrence.
    # For an automaton with S states, the output sequence has linear recurrence of
    # length <= S, so 2S terms are sufficient for Berlekamp–Massey.
    outs, accept_ids = _build_dfa()
    S = len(outs)
    E_terms = _generate_E_terms(outs, accept_ids, 2 * S + 5)

    REC = _berlekamp_massey(E_terms)
    L, poly_pow = _prepare_ring(REC)
    E_init = E_terms[:L]

    # Problem statement checks
    assert _binom_transform_prefix(E_init, 2) == 9
    assert _binom_transform_prefix(E_init, 5) == 3492

    # Compute (1+x)^n mod characteristic polynomial
    base = [0] * L
    base[0] = 1
    if L > 1:
        base[1] = 1
    R = poly_pow(base, n)

    ans = 0
    for i in range(L):
        ans = (ans + R[i] * E_init[i]) % MOD
    return ans


def main() -> None:
    print(solve(N))


if __name__ == "__main__":
    main()
