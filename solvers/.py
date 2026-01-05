#!/usr/bin/env python3
"""
Project Euler 470 - Super Ramvok

Key idea:
- The die-state evolution (toggling one random face after each game) does NOT
  depend on how the player plays Ramvok. Therefore the globally optimal strategy
  is myopic: maximize the expected profit of the *current* Ramvok game only.
- Super Ramvok expected total profit equals sum over states of:
    (expected number of visits to that state before absorption) * (Ramvok profit in that state)
- Starting from all-visible is symmetric under permutations of faces, so the
  distribution of visited subsets depends only on the number of visible faces k.
  Thus we only need:
    V_k(d) = expected number of visits to weight k (k visible faces),
  and
    A_{d,k,c} = average Ramvok profit over all k-subsets of {1..d}.
- d <= 20, so enumerating all subsets (2^d) is feasible.
"""

import math


# -------------------- Ramvok (single game) --------------------


def ramvok_best_profit(values_sorted, c):
    """
    Expected optimal net profit R for a Ramvok game with prizes 'values_sorted'
    (uniform over these values each turn), and cost per turn 'c' paid up-front
    for the chosen horizon t.

    For fixed t, expected prize f_t obeys:
        f_0 = 0
        f_t = E[max(X, f_{t-1})], X uniform over values

    Net profit is max_{t >= 0} (f_t - c*t).
    If c == 0, player can wait forever -> prize = max(values).
    """
    if not values_sorted:
        return 0.0
    maxv = values_sorted[-1]
    if c == 0:
        return float(maxv)

    k = len(values_sorted)
    # prefix sums for fast tail sums
    pref = [0]
    s = 0
    for v in values_sorted:
        s += v
        pref.append(s)

    # Reasonable upper bound:
    # once c*t > maxv, profit <= 0, and t=0 yields 0, so no need beyond maxv/c
    t_max = int(maxv / c) + 2
    if t_max < 1:
        t_max = 1

    best = 0.0
    prev = 0.0
    p = 0  # number of values < prev (monotone increasing)
    total = pref[-1]

    for t in range(1, t_max + 1):
        # advance p while values[p] < prev
        while p < k and values_sorted[p] < prev:
            p += 1
        # sum of >= prev is total - pref[p]
        sum_ge = total - pref[p]
        prev = (prev * p + sum_ge) / k
        profit = prev - c * t
        if profit > best:
            best = profit

        # If we reached the maximum prize, further f_t stays maxv,
        # and profit decreases linearly, so stop early.
        if abs(prev - maxv) < 1e-15:
            break

    return best


def best_profits_all_integer_c_for_mask(mask, max_c):
    """
    For a subset represented by bitmask 'mask' over values 1..d,
    compute best profit for each integer c in [0..max_c].

    Optimization:
    - values are extracted in increasing order by repeatedly removing lowest set bit.
    - f_t computed in O(k + t) using a moving pointer and cumulative sums.
    - For integer c>=1 and prize <= maxv, horizons t > maxv cannot yield positive profit.
    """
    vals = []
    cum = []
    total = 0

    m = mask
    while m:
        lsb = m & -m
        v = lsb.bit_length()  # value in 1..d
        vals.append(v)
        total += v
        cum.append(total)
        m ^= lsb

    k = len(vals)
    maxv = vals[-1]

    best = [0.0] * (max_c + 1)
    # c=0: wait forever -> always obtain maximum visible value
    best[0] = float(maxv)

    prev = 0.0
    p = 0

    # horizons beyond maxv are never useful for c>=1 (profit <= maxv - t <= 0)
    for t in range(1, maxv + 1):
        while p < k and vals[p] < prev:
            p += 1
        low_sum = cum[p - 1] if p else 0
        sum_ge = total - low_sum
        prev = (prev * p + sum_ge) / k

        # profit(prev,t,c)=prev - c*t > 0 only if c < prev/t
        lim = int(prev / t)
        if lim > max_c:
            lim = max_c
        for c in range(1, lim + 1):
            prof = prev - c * t
            if prof > best[c]:
                best[c] = prof

    return best


# -------------------- Super Ramvok (Markov chain by visible-count) --------------------


def gauss_jordan_inverse(mat):
    """Invert a small dense matrix using Gauss-Jordan (n <= 20 here)."""
    n = len(mat)
    aug = [row[:] + [0.0] * n for row in mat]
    for i in range(n):
        aug[i][n + i] = 1.0

    for col in range(n):
        # choose pivot
        pivot = col
        best = abs(aug[pivot][col])
        for r in range(col + 1, n):
            v = abs(aug[r][col])
            if v > best:
                best = v
                pivot = r
        if best == 0.0:
            raise ValueError("Singular matrix encountered")

        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]

        piv = aug[col][col]
        invp = 1.0 / piv
        rowc = aug[col]
        for j in range(2 * n):
            rowc[j] *= invp

        for r in range(n):
            if r == col:
                continue
            rowr = aug[r]
            f = rowr[col]
            if f == 0.0:
                continue
            for j in range(2 * n):
                rowr[j] -= f * rowc[j]

    return [row[n:] for row in aug]


def visit_counts_by_weight(d):
    """
    V_k(d): expected number of visits to the state "k visible faces" in the
    Ehrenfest toggle chain starting from k=d, with absorption at k=0.

    We build the transient submatrix Q over states 1..d, then N=(I-Q)^{-1}.
    Starting from state d -> row d gives expected visit counts to each transient state.
    """
    n = d
    Q = [[0.0] * n for _ in range(n)]

    for k in range(1, d + 1):
        i = k - 1
        if k == d:
            # from d always go to d-1
            Q[i][d - 2] = 1.0
        else:
            down = k / d
            up = (d - k) / d
            if k > 1:
                Q[i][k - 2] = down
            # k==1 goes to absorbing 0 with prob 1/d (not in Q)
            if k < d:
                Q[i][k] = up

    # A = I - Q
    A = [[0.0] * n for _ in range(n)]
    for i in range(n):
        A[i][i] = 1.0
        rowq = Q[i]
        rowa = A[i]
        for j in range(n):
            rowa[j] -= rowq[j]

    N = gauss_jordan_inverse(A)
    start_row = N[d - 1]  # start at weight d
    V = [0.0] * (d + 1)
    for k in range(1, d + 1):
        V[k] = start_row[k - 1]
    return V


def compute_S_list(d):
    """
    Compute S(d,c) for all integer c in [0..d], returning a list S where S[c]=S(d,c).
    """
    max_c = d
    V = visit_counts_by_weight(d)

    # sum_R[k][c] = sum_{|A|=k} R(A,c)
    sum_R = [[0.0] * (max_c + 1) for _ in range(d + 1)]

    for mask in range(1, 1 << d):
        k = mask.bit_count()
        best = best_profits_all_integer_c_for_mask(mask, max_c)
        row = sum_R[k]
        for c in range(max_c + 1):
            row[c] += best[c]

    S = [0.0] * (max_c + 1)
    for c in range(max_c + 1):
        total = 0.0
        for k in range(1, d + 1):
            avg = sum_R[k][c] / math.comb(d, k)
            total += V[k] * avg
        S[c] = total
    return S


def round_half_up(x):
    """Round to nearest integer (Project Euler style)."""
    return int(x + 0.5)


# -------------------- Main (compute F(20)) --------------------


def solve():
    # Assert samples from the statement
    # R(4,0.2) = 2.65
    r = ramvok_best_profit([1, 2, 3, 4], 0.2)
    assert abs(r - 2.65) < 1e-9, (r, "!= 2.65")

    # S(6,1) = 208.3
    S6 = compute_S_list(6)
    assert abs(S6[1] - 208.3) < 1e-6, (S6[1], "!= 208.3")

    # Compute F(20) = sum_{d=4..20} sum_{c=0..20} S(d,c)
    # But S(d,c)=0 for c>d (prize <= d), so sum c=0..min(20,d).
    F = 0.0
    for d in range(4, 21):
        Sd = compute_S_list(d)
        F += sum(Sd)  # Sd already only 0..d
    return round_half_up(F)


if __name__ == "__main__":
    print(solve())
