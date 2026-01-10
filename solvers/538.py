#!/usr/bin/env python3
"""
Project Euler 538: Maximum Quadrilaterals

We process prefixes U_n of the sequence:
  u_n = 2^{B(3n)} + 3^{B(2n)} + B(n+1)
where B(k) is the popcount of k.

For each prefix U_n, f(U_n) is the perimeter of the maximum-area quadrilateral
that can be formed from 4 distinct elements of the prefix; ties in area are
broken by larger perimeter.

This program computes:
  sum_{n=4..3_000_000} f(U_n)

No external libraries are used.
"""

from bisect import bisect_left, insort


def generate_u_and_uniques(N: int):
    """Return (u_list, sorted_uniques) for n=1..N (u_list is 0-indexed with u_list[n])."""
    # n <= 3_000_000 => 3n < 9_000_000 < 2^24, so popcount <= 24 is sufficient.
    pow3 = [1] * 25
    for k in range(1, 25):
        pow3[k] = pow3[k - 1] * 3

    u = [0] * (N + 1)
    uniq = set()
    for n in range(1, N + 1):
        val = (1 << ((3 * n).bit_count())) + pow3[n.bit_count()] + (n + 1).bit_count()
        u[n] = val
        uniq.add(val)

    return u, sorted(uniq)


def better(prod_new: int, per_new: int, prod_best: int, per_best: int) -> bool:
    """Return True if (prod_new, per_new) is better than (prod_best, per_best)."""
    return prod_new > prod_best or (prod_new == prod_best and per_new > per_best)


def compute_sum_f(N: int, want_f_at=()):
    """
    Compute sum_{n=4..N} f(U_n) and optionally return f(U_k) for k in want_f_at.
    Returns (total_sum, dict_of_f_at).
    """
    u, uniq_vals = generate_u_and_uniques(N)
    idx_of = {v: i for i, v in enumerate(uniq_vals)}

    counts = [0] * len(uniq_vals)  # multiplicities for each distinct value
    active = []  # sorted indices i with counts[i] > 0

    best_prod = -1
    best_per = 0

    want_set = set(want_f_at)
    got = {}

    total = 0

    for n in range(1, N + 1):
        v = u[n]
        idx = idx_of[v]
        c_before = counts[idx]

        if c_before == 0:
            insort(active, idx)
        counts[idx] = c_before + 1

        pos = bisect_left(active, idx)

        # Collect up to 3 predecessors of the *new copy* (we treat the new copy as
        # the last among equal values), and up to 3 successors.
        left = []
        t = 3 if c_before >= 3 else c_before
        for _ in range(t):
            left.append(v)

        q = pos - 1
        while len(left) < 3 and q >= 0:
            idx2 = active[q]
            v2 = uniq_vals[idx2]
            take = counts[idx2]
            need = 3 - len(left)
            if take > need:
                take = need
            for _ in range(take):
                left.append(v2)
            q -= 1

        right = []
        q = pos + 1
        while len(right) < 3 and q < len(active):
            idx2 = active[q]
            v2 = uniq_vals[idx2]
            take = counts[idx2]
            need = 3 - len(right)
            if take > need:
                take = need
            for _ in range(take):
                right.append(v2)
            q += 1

        # Build the local neighborhood in sorted order:
        #    [... up to 3 predecessors ... , new_element , ... up to 3 successors ...]
        around = left[::-1]
        around.append(v)
        around.extend(right)

        p = len(around) - len(right) - 1  # index of the new element in `around`

        # Check up to 4 consecutive quadruples (windows of length 4) containing the new element.
        for start in (p - 3, p - 2, p - 1, p):
            if start < 0 or start + 4 > len(around):
                continue
            a = around[start]
            b = around[start + 1]
            c = around[start + 2]
            d = around[start + 3]

            # Quadrilateral inequality (necessary and sufficient): largest side < sum of the other three
            if d >= a + b + c:
                continue

            P = a + b + c + d
            # Compare areas via 16*A^2 = (P-2a)(P-2b)(P-2c)(P-2d), avoiding sqrt/floats.
            prod = (P - 2 * a) * (P - 2 * b) * (P - 2 * c) * (P - 2 * d)

            if better(prod, P, best_prod, best_per):
                best_prod = prod
                best_per = P

        if n in want_set:
            got[n] = best_per

        if n >= 4:
            total += best_per

    return total, got


def main():
    # --- Problem statement test values ---
    total_150, f_at = compute_sum_f(150, want_f_at=(5, 10, 150))
    assert f_at[5] == 59, f"Expected f(U_5)=59, got {f_at[5]}"
    assert f_at[10] == 118, f"Expected f(U_10)=118, got {f_at[10]}"
    assert f_at[150] == 3223, f"Expected f(U_150)=3223, got {f_at[150]}"
    assert (
        total_150 == 234761
    ), f"Expected sum f(U_n)=234761 for 4<=n<=150, got {total_150}"

    # --- Full answer ---
    ans, _ = compute_sum_f(3_000_000)
    print(ans)


if __name__ == "__main__":
    main()
