#!/usr/bin/env python3
"""Project Euler 305 - Reflexive Position

Let S be the infinite string formed by concatenating the positive integers:
  S = 123456789101112131415...

For a positive integer n, let f(n) be the 1-indexed starting position of the n-th
occurrence of the decimal string str(n) in S.

Compute:
  sum_{k=1..13} f(3^k)

The implementation:
- Builds a small KMP automaton for the pattern (length <= 7 for this problem).
- Counts occurrences in prefixes of S without building S, by splitting counting into:
  * A small brute prefix up to A = 10^(m-2) (covers early multi-boundary matches).
  * An analytic tail that counts:
      - occurrences fully inside one number (digit-DP over integers), and
      - occurrences spanning exactly one boundary i|i+1 (modular arithmetic per split).
- Uses binary search on the start position L, using the monotone predicate:
    starts <= L  <=>  ends <= L + m - 1

Running:
  python3 main.py
prints the answer.
"""

from __future__ import annotations


def build_kmp_trans(pattern: str):
    """Return (pi, trans) where trans[state][digit] -> (next_state, match_inc)."""
    m = len(pattern)
    pat = [ord(c) - 48 for c in pattern]

    # Prefix function
    pi = [0] * m
    j = 0
    for i in range(1, m):
        while j > 0 and pat[i] != pat[j]:
            j = pi[j - 1]
        if pat[i] == pat[j]:
            j += 1
        pi[i] = j

    # KMP transition table for states 0..m-1
    trans = [[None] * 10 for _ in range(m)]
    for state in range(m):
        for dig in range(10):
            s = state
            while s > 0 and pat[s] != dig:
                s = pi[s - 1]
            if pat[s] == dig:
                s += 1
            inc = 0
            if s == m:
                inc = 1
                s = pi[m - 1]  # allow overlaps
            trans[state][dig] = (s, inc)
    return pi, trans


def prefix_to_N(P: int):
    """Map prefix length P of S to (N_full, rem).

    S[:P] contains all numbers 1..N_full fully, plus `rem` leading digits of str(N_full+1).
    """
    if P <= 0:
        return 0, 0
    cum = 0
    d = 1
    start = 1
    while True:
        block_count = 9 * start
        block_len = block_count * d
        if cum + block_len < P:
            cum += block_len
            d += 1
            start *= 10
        else:
            break
    R = P - cum
    t_full = R // d
    rem = R - t_full * d
    if t_full == 0:
        return start - 1, rem
    return start + t_full - 1, rem


def count_arith_progression(lo: int, hi: int, mod: int, rem: int) -> int:
    """Count x in [lo, hi] with x % mod == rem."""
    if hi < lo:
        return 0
    first = lo + ((rem - lo) % mod)
    if first > hi:
        return 0
    return 1 + (hi - first) // mod


class PatternCounter:
    """Counts occurrences of a fixed pattern p in S, and provides f(p) via binary search."""

    def __init__(self, pattern: str):
        self.pat = pattern
        self.m = len(pattern)
        _, self.trans = build_kmp_trans(pattern)

        # Powers of 10 for small exponents
        self.pow10 = [1]
        for _ in range(1, 30):
            self.pow10.append(self.pow10[-1] * 10)

        # Threshold where len(x) >= m-1 for all x >= A:
        # A = 10^(m-2) for m>=2; A=1 for m=1.
        self.A = 1 if self.m < 2 else self.pow10[self.m - 2]

        # Brute-count all matches in C(n) = "123...n" for n <= A.
        self.brute_counts = self._build_brute_counts(self.A)
        self.brute_A = self.brute_counts[self.A]

        # Precompute internal matches in all d-digit numbers for d up to max_digits.
        self.max_digits = 20
        self.internal_len = [0] * (self.max_digits + 1)
        self._precompute_internal_len()

        # Cache these once for fast differences.
        self.internal_A = self.internal_upto(self.A)
        self.boundary_A = self.boundary_upto(self.A)

    def _build_brute_counts(self, upto: int):
        counts = [0] * (upto + 1)
        state = 0
        total = 0
        for n in range(1, upto + 1):
            for ch in str(n):
                state, inc = self.trans[state][ord(ch) - 48]
                total += inc
            counts[n] = total
        return counts

    def _precompute_internal_len(self):
        m = self.m
        for d in range(1, self.max_digits + 1):
            # DP over all d-digit numbers (first digit 1..9)
            dp_count = [0] * m
            dp_match = [0] * m

            for dig in range(1, 10):
                ns, inc = self.trans[0][dig]
                dp_count[ns] += 1
                dp_match[ns] += inc

            for _ in range(1, d):
                newc = [0] * m
                newm = [0] * m
                for st in range(m):
                    c = dp_count[st]
                    if not c:
                        continue
                    cm = dp_match[st]
                    tr = self.trans[st]
                    for dig in range(10):
                        ns, inc = tr[dig]
                        newc[ns] += c
                        newm[ns] += cm + c * inc
                dp_count, dp_match = newc, newm

            self.internal_len[d] = sum(dp_match)

    def internal_upto(self, N: int) -> int:
        """Total occurrences of pattern inside the decimal strings of numbers 1..N."""
        if N <= 0:
            return 0
        sN = str(N)
        D = len(sN)

        res = 0
        for d in range(1, D):
            # D <= 20 in this problem, so internal_len[d] is available.
            res += self.internal_len[d]

        # bounded DP for length D (numbers from 10^(D-1) to N, or 1..N if D=1)
        m = self.m
        dpC_t = [0] * m  # tight counts
        dpM_t = [0] * m  # tight match totals
        dpC_l = [0] * m  # loose counts
        dpM_l = [0] * m  # loose match totals
        dpC_t[0] = 1
        digits = [ord(c) - 48 for c in sN]

        for pos, lim in enumerate(digits):
            newCt = [0] * m
            newMt = [0] * m
            newCl = [0] * m
            newMl = [0] * m
            mind = 1 if pos == 0 else 0

            # from tight
            for st in range(m):
                c = dpC_t[st]
                if not c:
                    continue
                cm = dpM_t[st]
                tr = self.trans[st]
                for dig in range(mind, lim + 1):
                    ns, inc = tr[dig]
                    if dig == lim:
                        newCt[ns] += c
                        newMt[ns] += cm + c * inc
                    else:
                        newCl[ns] += c
                        newMl[ns] += cm + c * inc

            # from loose
            for st in range(m):
                c = dpC_l[st]
                if not c:
                    continue
                cm = dpM_l[st]
                tr = self.trans[st]
                for dig in range(mind if pos == 0 else 0, 10):
                    ns, inc = tr[dig]
                    newCl[ns] += c
                    newMl[ns] += cm + c * inc

            dpC_t, dpM_t, dpC_l, dpM_l = newCt, newMt, newCl, newMl

        res += sum(dpM_t) + sum(dpM_l)
        return res

    def boundary_upto(self, N: int) -> int:
        """Total occurrences that span exactly one boundary i|i+1 for i in [1, N-1]."""
        if self.m <= 1 or N <= 1:
            return 0

        m = self.m
        pow10 = self.pow10
        max_d = len(str(N - 1))
        total = 0

        for k in range(1, m):  # k digits from i, m-k digits from i+1
            p1 = self.pat[:k]
            p2 = self.pat[k:]
            if p2[0] == "0":
                continue  # no positive integer has prefix starting with 0
            suf_val = int(p1)
            L = m - k
            pre_val = int(p2)
            mod = pow10[k]

            # same-digit-length case (i has d digits, i+1 has d digits)
            for d in range(1, max_d + 1):
                x_lo = 1 if d == 1 else pow10[d - 1]
                x_hi = min(N - 1, pow10[d] - 2)  # exclude 10^d - 1
                if x_hi < x_lo or d < L:
                    continue

                # y = i+1 must be d-digit and have prefix p2 of length L
                y_lo = pre_val * pow10[d - L]
                y_hi = (pre_val + 1) * pow10[d - L] - 1

                lo = max(x_lo, y_lo - 1)
                hi = min(x_hi, y_hi - 1)
                if hi >= lo:
                    total += count_arith_progression(lo, hi, mod, suf_val)

            # transition case: i = 10^d - 1, i+1 = 10^d (digits increase)
            if p1 == "9" * k:
                need = "1" + "0" * (L - 1)
                if p2 == need:
                    # d must satisfy 10^d <= N and d >= L-1 and d >= 1
                    dmax = len(str(N)) - 1  # floor(log10(N))
                    dmin = max(1, L - 1)
                    if dmax >= dmin:
                        total += dmax - dmin + 1

        return total

    def count_full_concat(self, N: int) -> int:
        """Total matches in concatenation C(N) = '123...N'."""
        if N <= 0:
            return 0
        if N <= self.A:
            return self.brute_counts[N]
        return (
            self.brute_A
            + (self.internal_upto(N) - self.internal_A)
            + (self.boundary_upto(N) - self.boundary_A)
        )

    def tail_digits(self, N: int, need: int | None = None) -> str:
        """Return the last `need` digits of C(N), computed from the last few numbers."""
        if need is None:
            need = self.m - 1
        if need <= 0 or N <= 0:
            return ""
        s = ""
        x = N
        while len(s) < need and x >= 1:
            s = str(x) + s
            x -= 1
        return s[-need:]

    def count_matches_in_prefix(self, P: int) -> int:
        """Total matches fully contained in the first P digits of S."""
        if P <= 0:
            return 0
        N_full, rem = prefix_to_N(P)
        cnt = self.count_full_concat(N_full)
        if rem == 0:
            return cnt

        # Count matches whose end lies in the appended partial digits.
        tail = self.tail_digits(N_full, self.m - 1)
        ext = str(N_full + 1)[:rem]
        combined = tail + ext
        tlen = len(tail)

        state = 0
        add = 0
        for i, ch in enumerate(combined):
            state, inc = self.trans[state][ord(ch) - 48]
            if inc and i >= tlen:  # match ends in ext
                add += 1
        return cnt + add

    def count_starts_leq(self, L: int) -> int:
        """Occurrences with start position <= L."""
        return self.count_matches_in_prefix(L + self.m - 1)

    def f(self, occurrence_index: int) -> int:
        """Return start position (1-indexed) of the occurrence_index-th occurrence."""
        target = occurrence_index
        lo, hi = 1, 1
        while self.count_starts_leq(hi) < target:
            hi *= 2
        while lo < hi:
            mid = (lo + hi) // 2
            if self.count_starts_leq(mid) >= target:
                hi = mid
            else:
                lo = mid + 1
        return lo


def f(n: int) -> int:
    """Compute f(n) from the problem statement."""
    pc = PatternCounter(str(n))
    return pc.f(n)


def solve() -> int:
    total = 0
    for k in range(1, 14):
        n = 3**k
        total += f(n)
    return total


if __name__ == "__main__":
    # Asserts for the examples given in the problem statement:
    assert f(1) == 1
    assert f(5) == 81
    assert f(12) == 271
    assert f(7780) == 111111365

    print(solve())
