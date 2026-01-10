#!/usr/bin/env python3
"""
Project Euler 660 — Pandigital Triangles

We seek integer-sided triangles with a 120° angle, so (a,b,c) satisfy:
    c^2 = a^2 + a*b + b^2
(where c is opposite the 120° angle, hence the largest side).

An n-pandigital triangle uses each base-n digit 0..n-1 exactly once across the
base-n representations of a, b, c.

We solve by:
- choosing digit-lengths (la, lb, lc) with la+lb+lc = n, la <= lb <= lc
- using digit-by-digit backtracking in base n from least significant digit upward
- enforcing the Diophantine condition via carry propagation on coefficients
- using bitmasks to ensure digits are used exactly once
- heavy pruning from triangle inequality: since a < b, c < a+b <= 2b => lc <= lb+1
  and if lc == lb+1 then c's most significant digit must be 1 in base n
"""

from typing import List, Tuple


def to_base_digits(x: int, base: int) -> List[int]:
    """Most-significant-digit first."""
    if x <= 0:
        raise ValueError("x must be positive")
    digs = []
    while x:
        digs.append(x % base)
        x //= base
    return digs[::-1]


def is_n_pandigital_triangle(a: int, b: int, c: int, n: int) -> bool:
    """Check the definition directly (order-insensitive for a,b)."""
    if not (a > 0 and b > 0 and c > 0):
        return False
    # 120-degree condition (c must be the side opposite 120°, i.e., the largest)
    if not (c * c == a * a + a * b + b * b):
        return False

    da = to_base_digits(a, n)
    db = to_base_digits(b, n)
    dc = to_base_digits(c, n)
    all_d = da + db + dc
    if len(all_d) != n:
        return False
    if len(set(all_d)) != n:
        return False
    return set(all_d) == set(range(n))


def build_pair_map(n: int, coeff1_mod: int, coeff2_mod: int) -> List[List[Tuple[int, int, int]]]:
    """
    Map residue r -> list of (d1, d2, pair_mask) with d1!=d2 and
        coeff1_mod*d1 + coeff2_mod*d2 ≡ r (mod n)
    pair_mask has bits for digits used by (d1,d2).
    """
    mp: List[List[Tuple[int, int, int]]] = [[] for _ in range(n)]
    for d1 in range(n):
        for d2 in range(n):
            if d2 == d1:
                continue
            r = (coeff1_mod * d1 + coeff2_mod * d2) % n
            mp[r].append((d1, d2, (1 << d1) | (1 << d2)))
    return mp


def solve_for_base(n: int) -> int:
    """
    Return sum of largest sides c of all n-pandigital triangles.
    """
    all_digits_mask = (1 << n) - 1
    total_c = 0

    # Choose digit lengths la<=lb<=lc, la+lb+lc=n.
    # Key pruning: with a<b, c < a+b <= 2b => lc <= lb+1.
    for la in range(1, n - 1):
        for lb in range(la, n - la):
            lc = n - la - lb
            if lc < lb or lc < 1:
                continue
            if lc > lb + 1:
                continue

            L = lc  # c is the longest (or tied-longest)
            # digit arrays store least-significant digit at index 0
            a = [0] * (2 * L)
            b = [0] * (2 * L)
            c = [0] * (2 * L)

            # base powers for reconstruction
            pow_n = [1]
            for _ in range(1, L + 1):
                pow_n.append(pow_n[-1] * n)

            # If lc == lb+1, then c in [n^lb, 2*n^lb), so c's MSD in base n must be 1.
            c_msd_fixed = 1 if (lc == lb + 1) else None

            def coef_u_full(t: int) -> int:
                """Coefficient at n^t of E = a^2 + a*b + b^2 - c^2 using current digits."""
                s = 0
                for i in range(t + 1):
                    s += a[i] * a[t - i]
                    s += a[i] * b[t - i]
                    s += b[i] * b[t - i]
                    s -= c[i] * c[t - i]
                return s

            def finish(mask: int, carry: int) -> None:
                """After assigning all digits up to L-1, validate remaining coefficients and add solution."""
                nonlocal total_c
                if mask != 0:
                    return

                car = carry
                for t in range(L, 2 * L - 1):  # L .. 2L-2
                    u = coef_u_full(t)
                    v = u + car
                    if v % n != 0:
                        return
                    car = v // n
                if car != 0:
                    return

                aval = sum(a[i] * pow_n[i] for i in range(la))
                bval = sum(b[i] * pow_n[i] for i in range(lb))
                cval = sum(c[i] * pow_n[i] for i in range(lc))

                # Ensure c is the largest side (should be true for a valid 120° triangle)
                if not (cval > aval and cval > bval):
                    return

                total_c += cval

            def dfs(
                pos: int,
                mask: int,
                carry: int,
                ca_mod: int,
                cb_mod: int,
                cc_mod: int,
                ca_int: int,
                cb_int: int,
                cc_int: int,
                map_bc: List[List[Tuple[int, int, int]]],
                map_ac: List[List[Tuple[int, int, int]]],
                map_cc: List[int],
            ) -> None:
                if pos == L:
                    finish(mask, carry)
                    return

                need_a = pos < la
                need_b = pos < lb

                a_forbid0 = need_a and (pos == la - 1)
                b_forbid0 = need_b and (pos == lb - 1)
                c_forbid0 = (pos == lc - 1)

                # Symmetry break when la==lb: compare MS digits (unique digits => enough)
                enforce_a_lt_b_msd = (la == lb and pos == la - 1)

                # If c ties in length with a or b, MS digit comparison enforces c larger
                enforce_c_gt_a_msd = (la == lc and pos == lc - 1)
                enforce_c_gt_b_msd = (lb == lc and pos == lc - 1)

                # Build constant part of u_pos excluding terms involving digit at pos paired with digit at 0
                const = 0
                for i in range(1, pos):
                    j = pos - i
                    const += a[i] * a[j]
                    const += a[i] * b[j]
                    const += b[i] * b[j]
                    const -= c[i] * c[j]

                # We need: (const + carry + ca*da + cb*db + cc*dc) % n == 0
                base_res = (-const - carry) % n

                if need_a and need_b:
                    # Choose da, then choose (db,dc) using residue map
                    md = mask & (~1) if a_forbid0 else mask
                    while md:
                        da_bit = md & -md
                        da = da_bit.bit_length() - 1
                        md -= da_bit
                        mask1 = mask ^ da_bit

                        target = (base_res - (ca_mod * da)) % n
                        for db, dc, pair_mask in map_bc[target]:
                            if (pair_mask & mask1) != pair_mask:
                                continue
                            if b_forbid0 and db == 0:
                                continue
                            if c_forbid0 and dc == 0:
                                continue
                            if c_msd_fixed is not None and pos == lc - 1 and dc != c_msd_fixed:
                                continue
                            if enforce_a_lt_b_msd and not (da < db):
                                continue
                            if enforce_c_gt_a_msd and not (dc > da):
                                continue
                            if enforce_c_gt_b_msd and not (dc > db):
                                continue

                            a[pos], b[pos], c[pos] = da, db, dc
                            v = const + carry + ca_int * da + cb_int * db + cc_int * dc
                            dfs(
                                pos + 1,
                                mask1 ^ pair_mask,
                                v // n,
                                ca_mod, cb_mod, cc_mod,
                                ca_int, cb_int, cc_int,
                                map_bc, map_ac, map_cc
                            )
                    a[pos] = b[pos] = c[pos] = 0

                elif need_a and not need_b:
                    # Choose (da,dc) using residue map
                    for da, dc, pair_mask in map_ac[base_res]:
                        if (pair_mask & mask) != pair_mask:
                            continue
                        if a_forbid0 and da == 0:
                            continue
                        if c_forbid0 and dc == 0:
                            continue
                        if c_msd_fixed is not None and pos == lc - 1 and dc != c_msd_fixed:
                            continue
                        if enforce_c_gt_a_msd and not (dc > da):
                            continue

                        a[pos], b[pos], c[pos] = da, 0, dc
                        v = const + carry + ca_int * da + cc_int * dc
                        dfs(
                            pos + 1,
                            mask ^ pair_mask,
                            v // n,
                            ca_mod, cb_mod, cc_mod,
                            ca_int, cb_int, cc_int,
                            map_bc, map_ac, map_cc
                        )
                    a[pos] = c[pos] = 0

                elif need_b and not need_a:
                    # Choose (db,dc) using residue map
                    for db, dc, pair_mask in map_bc[base_res]:
                        if (pair_mask & mask) != pair_mask:
                            continue
                        if b_forbid0 and db == 0:
                            continue
                        if c_forbid0 and dc == 0:
                            continue
                        if c_msd_fixed is not None and pos == lc - 1 and dc != c_msd_fixed:
                            continue
                        if enforce_c_gt_b_msd and not (dc > db):
                            continue

                        a[pos], b[pos], c[pos] = 0, db, dc
                        v = const + carry + cb_int * db + cc_int * dc
                        dfs(
                            pos + 1,
                            mask ^ pair_mask,
                            v // n,
                            ca_mod, cb_mod, cc_mod,
                            ca_int, cb_int, cc_int,
                            map_bc, map_ac, map_cc
                        )
                    b[pos] = c[pos] = 0

                else:
                    # Only c digit at this position
                    cand = map_cc[base_res] & mask
                    if c_forbid0:
                        cand &= ~1
                    if c_msd_fixed is not None and pos == lc - 1:
                        cand &= (1 << c_msd_fixed)

                    while cand:
                        dc_bit = cand & -cand
                        dc = dc_bit.bit_length() - 1
                        cand -= dc_bit

                        c[pos] = dc
                        v = const + carry + cc_int * dc
                        dfs(
                            pos + 1,
                            mask ^ dc_bit,
                            v // n,
                            ca_mod, cb_mod, cc_mod,
                            ca_int, cb_int, cc_int,
                            map_bc, map_ac, map_cc
                        )
                    c[pos] = 0

            # --- Position 0: choose (a0,b0,c0), set initial carry, and build residue maps ---
            # Note: if a/b/c length == 1, their only digit is also MSD => cannot be 0.
            forbid0_a0 = (la == 1)
            forbid0_b0 = (lb == 1)
            forbid0_c0 = (lc == 1)
            enforce_a_lt_b_msd0 = (la == lb == 1)

            ma = (all_digits_mask & ~1) if forbid0_a0 else all_digits_mask
            while ma:
                da_bit = ma & -ma
                da = da_bit.bit_length() - 1
                ma -= da_bit
                a[0] = da
                mask1 = all_digits_mask ^ da_bit

                mb = (mask1 & ~1) if forbid0_b0 else mask1
                while mb:
                    db_bit = mb & -mb
                    db = db_bit.bit_length() - 1
                    mb -= db_bit
                    if enforce_a_lt_b_msd0 and not (da < db):
                        continue
                    b[0] = db
                    mask2 = mask1 ^ db_bit

                    mc = (mask2 & ~1) if forbid0_c0 else mask2
                    while mc:
                        dc_bit = mc & -mc
                        dc = dc_bit.bit_length() - 1
                        mc -= dc_bit
                        c[0] = dc

                        # u0 = a0^2 + a0*b0 + b0^2 - c0^2
                        u0 = da * da + da * db + db * db - dc * dc
                        if u0 % n != 0:
                            continue
                        carry1 = u0 // n

                        # coefficients for u_pos (pos>0):
                        ca_int = 2 * da + db
                        cb_int = da + 2 * db
                        cc_int = -2 * dc

                        ca_mod = ca_int % n
                        cb_mod = cb_int % n
                        cc_mod = cc_int % n

                        map_bc = build_pair_map(n, cb_mod, cc_mod)
                        map_ac = build_pair_map(n, ca_mod, cc_mod)

                        map_cc = [0] * n
                        for d in range(n):
                            map_cc[(cc_mod * d) % n] |= (1 << d)

                        dfs(
                            1,
                            mask2 ^ dc_bit,
                            carry1,
                            ca_mod, cb_mod, cc_mod,
                            ca_int, cb_int, cc_int,
                            map_bc, map_ac, map_cc
                        )

            a[0] = b[0] = c[0] = 0

    return total_c


def solve() -> int:
    return sum(solve_for_base(n) for n in range(9, 19))


if __name__ == "__main__":
    # Test value from the problem statement:
    # (217, 248, 403) is 9-pandigital with a 120° angle.
    assert 403 * 403 == 217 * 217 + 217 * 248 + 248 * 248
    assert is_n_pandigital_triangle(217, 248, 403, 9)

    print(solve())

