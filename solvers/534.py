#!/usr/bin/env python3
"""
Project Euler 534 — Weak Queens

Let Q(n,w) be the number of ways n weak queens with weakness factor w can be
placed on an n×n board so that no two queens threaten each other.

A weak queen:
- attacks horizontally any distance  (=> at most one per row; we place exactly one per row)
- attacks vertically/diagonally only up to distance L = n-1-w rows away

So we count sequences c[0..n-1], c[r] in [0..n-1], such that for any i<j with d=j-i <= L:
    c[i] != c[j]
    c[i] != c[j] + d
    c[i] != c[j] - d
For d > L there is no constraint between those rows.

We compute Q(n,w) for given n and w, and S(n)=sum_{w=0..n-1} Q(n,w).
"""

from collections import defaultdict


def _nqueens_count_classic(n: int) -> int:
    """Classic n-queens (full-range) solutions count, using bitmasks + vertical reflection symmetry."""
    all_mask = (1 << n) - 1

    def rec(cols: int, d1: int, d2: int) -> int:
        if cols == all_mask:
            return 1
        total = 0
        avail = all_mask & ~(cols | d1 | d2)
        while avail:
            bit = avail & -avail
            avail -= bit
            total += rec(cols | bit, ((d1 | bit) << 1) & all_mask, (d2 | bit) >> 1)
        return total

    half = n // 2
    total = 0
    # Place first-row queen in left half and double (for even n no fixed points).
    for col in range(half):
        bit = 1 << col
        total += rec(bit, (bit << 1) & all_mask, bit >> 1)
    total *= 2
    if n % 2 == 1:
        # Middle column is fixed under reflection; count it once.
        col = half
        bit = 1 << col
        total += rec(bit, (bit << 1) & all_mask, bit >> 1)
    return total


def _count_by_L(n: int, L: int) -> int:
    """
    Count placements with attack range L (i.e. weakness factor w = n-1-L).

    Uses a sliding-window DP over the last L rows. State is packed into an int:
    - each column index fits in 4 bits (n<=14 here), distance-1 queen stored in low nibble.
    """
    if L <= 0:
        # No vertical/diagonal attack at all (only horizontal), so each row independent.
        return n**n
    if L >= n - 1:
        # Full-range weak queen => classic queen.
        return _nqueens_count_classic(n)

    all_cols_mask = (1 << n) - 1
    shift = 4  # enough for n<=14
    keep_mask = (1 << (shift * L)) - 1

    # attack[col][d] = bitmask of columns attacked on current row by a queen
    # that is d rows above in column 'col' (vertical + the two diagonals).
    attack = [[0] * (L + 1) for _ in range(n)]
    for c in range(n):
        for d in range(1, L + 1):
            m = 1 << c
            cp = c + d
            if cp < n:
                m |= 1 << cp
            cm = c - d
            if cm >= 0:
                m |= 1 << cm
            attack[c][d] = m

    def dp_from_first_row_cols(first_cols):
        # After placing row 0, the packed state is just that column in the low nibble.
        states = defaultdict(int)
        for c0 in first_cols:
            states[c0] += 1

        # Fill rows 1..n-1
        for r in range(1, n):
            m_prev = r if r < L else L  # number of previous rows constrained
            nxt = defaultdict(int)

            # localize for speed
            attack_local = attack
            acm = all_cols_mask
            sh = shift
            km = keep_mask
            mask_needed = r + 1 >= L

            for state, cnt in states.items():
                # Build forbidden columns for row r from the previous min(L, r) queens.
                forbid = 0
                s = state
                i = 1
                # Extract columns from low nibbles; distance increases as we shift.
                while i <= m_prev:
                    pc = s & 0xF
                    s >>= sh
                    forbid |= attack_local[pc][i]
                    i += 1

                avail = acm & ~forbid
                while avail:
                    bit = avail & -avail
                    avail -= bit
                    col = bit.bit_length() - 1
                    ns = (state << sh) | col
                    if mask_needed:
                        ns &= km
                    nxt[ns] += cnt

            states = nxt

        return sum(states.values())

    # Vertical reflection symmetry (mirror columns): always valid for this problem.
    # For even n: no fixed points under reflection (no middle column), so total = 2*left_half.
    # For odd n: total = 2*left_half + middle_column_case.
    half = n // 2
    left_count = dp_from_first_row_cols(range(half))
    if n % 2 == 0:
        return 2 * left_count
    else:
        mid_count = dp_from_first_row_cols([half])
        return 2 * left_count + mid_count


def Q(n: int, w: int) -> int:
    """Q(n,w) as defined in the problem."""
    if not (0 <= w <= n - 1):
        raise ValueError("w must satisfy 0 <= w <= n-1")
    L = n - 1 - w
    return _count_by_L(n, L)


def S(n: int) -> int:
    """S(n) = sum_{w=0..n-1} Q(n,w)."""
    total = 0
    for w in range(n):
        total += Q(n, w)
    return total


def _run_asserts_from_statement() -> None:
    # Given examples:
    assert Q(4, 0) == 2
    assert Q(4, 2) == 16
    assert Q(4, 3) == 256
    assert S(4) == 276
    assert S(5) == 3347


def main() -> None:
    _run_asserts_from_statement()
    print(S(14))


if __name__ == "__main__":
    main()
