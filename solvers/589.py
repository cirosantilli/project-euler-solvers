#!/usr/bin/env python3
"""
Project Euler 589 - Poohsticks Marathon
Hybrid solver (iterative + direct linear solve fallback), no external libraries.

We model the game as an event-driven stochastic process.
A stick "laps" the other when it emerges while already 1 journey ahead,
making the difference in completed journeys reach ±2.

We reduce the state space by averaging over the post-emergence reset times,
turning the original 2D time state into a 1D expected-value function C1[d]
depending only on the current time difference between sticks.
This yields a linear system of size <= (m+5) <= 105 which we solve directly.
"""

from math import isfinite


# ---------------------------
# Small helper math routines
# ---------------------------


def arith_sum(a: int, b: int) -> float:
    """Sum of integers from a to b inclusive (0 if a>b)."""
    if a > b:
        return 0.0
    n = b - a + 1
    return (a + b) * n / 2.0


def expected_min_consecutive(low: int, high: int) -> float:
    """
    Expected min of two iid discrete uniform variables on [low..high].
    """
    L = high - low + 1
    denom = L * L
    total = 0.0
    for i in range(L):
        v = low + i
        # P(min=v) = (2L - 2i - 1) / L^2
        w = (2 * L - 2 * i - 1) / denom
        total += v * w
    return total


# -----------------------------------------
# Gaussian elimination for dense float system
# -----------------------------------------


def gauss_solve(A, b):
    """
    Solve A x = b via Gauss-Jordan elimination with partial pivoting.
    A is modified in-place. Returns solution vector x.
    """
    n = len(A)

    # augment
    for i in range(n):
        A[i].append(b[i])

    for col in range(n):
        # pivot
        piv = col
        best = abs(A[col][col])
        for r in range(col + 1, n):
            v = abs(A[r][col])
            if v > best:
                best = v
                piv = r
        if best < 1e-18:
            raise RuntimeError("Singular/ill-conditioned system")

        if piv != col:
            A[col], A[piv] = A[piv], A[col]

        # normalize pivot row
        row = A[col]
        inv = 1.0 / row[col]
        for j in range(col, n + 1):
            row[j] *= inv

        # eliminate others
        for r in range(n):
            if r == col:
                continue
            factor = A[r][col]
            if factor == 0.0:
                continue
            rr = A[r]
            for j in range(col, n + 1):
                rr[j] -= factor * row[j]

    return [A[i][n] for i in range(n)]


# -------------------------------------------------
# Direct solver: build linear system for C1[1..M]
# -------------------------------------------------


def compute_C1_direct(n: int, m: int):
    """
    Computes:
      C1[d] = average expected remaining time when:
             - stick A has journey advantage +1 (d=+1 state),
             - stick A's new travel time is uniform in [n+5..m+5],
             - stick B will emerge in exactly d seconds.

    Returns (C1, B0) where:
      B0 = average expected remaining time after simultaneous emergence
          (difference 0 and both reset).
    """
    L = m - n + 1
    A_low = n + 5
    A_high = m + 5
    M = A_high

    EminA = expected_min_consecutive(A_low, A_high)
    k = L / (L - 1.0)
    invL = 1.0 / L

    # B0 = B0_const + sum b0_coeff[d] * C1[d]
    B0_const = k * EminA
    b0_coeff = [0.0] * (M + 1)
    # only d<=L-1 matter in B0
    for d in range(1, min(L, M + 1)):
        if d <= L - 1:
            b0_coeff[d] = k * (2.0 / (L * L)) * (L - d)

    # Build C0[y] = q0[y] + sum_j p0[y][j]*C1[j]
    q0 = [0.0] * (M + 1)
    p0 = [[0.0] * (M + 1) for _ in range(M + 1)]

    for y in range(1, M + 1):
        # a<y part (stick A emerges first)
        lt_low = A_low
        lt_high = min(A_high, y - 1)
        sum_lt_a = arith_sum(lt_low, lt_high)

        if lt_low <= lt_high:
            j_lo = y - lt_high
            j_hi = y - lt_low
            for j in range(j_lo, j_hi + 1):
                if 1 <= j <= M:
                    p0[y][j] += invL

        # a>y part (stick B emerges first)
        gt_low = max(A_low, y + 1)
        gt_high = A_high
        count_gt = max(0, gt_high - gt_low + 1)
        base_gt = count_gt * y

        if gt_low <= gt_high:
            j_lo = gt_low - y
            j_hi = gt_high - y
            for j in range(j_lo, j_hi + 1):
                if 1 <= j <= M:
                    p0[y][j] += invL

        eq = A_low <= y <= A_high
        # constant contribution
        q = (sum_lt_a + base_gt + (y if eq else 0.0)) * invL
        if eq:
            q += B0_const * invL
            # plus linear b0_coeff term
            for d in range(1, min(L, M + 1)):
                if d <= L - 1:
                    p0[y][d] += b0_coeff[d] * invL

        q0[y] = q

    # prefix sums for fast range sums
    pref_q = [0.0] * (M + 1)
    s = 0.0
    for y in range(1, M + 1):
        s += q0[y]
        pref_q[y] = s

    pref_p = [[0.0] * (M + 1) for _ in range(M + 1)]
    for j in range(1, M + 1):
        s = 0.0
        col = pref_p[j]
        for y in range(1, M + 1):
            s += p0[y][j]
            col[y] = s

    # Build B1 = constB1 + sum_j b1[j]*C1[j]
    w = [0.0] * (M + 1)  # weights (L-d)
    for d in range(1, min(L, M + 1)):
        if d <= L - 1:
            w[d] = L - d

    sum_w_q = 0.0
    for d in range(1, min(L, M + 1)):
        if d <= L - 1:
            sum_w_q += w[d] * q0[d]

    constB1 = k * EminA + k * (1.0 / (L * L)) * sum_w_q

    b1 = [0.0] * (M + 1)
    for j in range(1, M + 1):
        ss = 0.0
        for d in range(1, min(L, M + 1)):
            if d <= L - 1:
                ss += w[d] * p0[d][j]
        b1[j] = k * (1.0 / (L * L)) * ss

    # Build linear system for C1[1..M]
    A_mat = [[0.0] * M for _ in range(M)]
    b_vec = [0.0] * M

    for t in range(1, M + 1):
        lt_low = A_low
        lt_high = min(A_high, t - 1)
        sum_lt_a = arith_sum(lt_low, lt_high)

        gt_low = max(A_low, t + 1)
        gt_high = A_high
        count_gt = max(0, gt_high - gt_low + 1)
        base_gt = count_gt * t

        eq = A_low <= t <= A_high

        const1 = (sum_lt_a + base_gt + (t if eq else 0.0)) * invL

        # Sum_gt_C0: y = a - t for a in [gt_low..A_high]
        if gt_low <= gt_high:
            y_lo = gt_low - t
            y_hi = gt_high - t
            Qgt = pref_q[y_hi] - (pref_q[y_lo - 1] if y_lo > 1 else 0.0)

            # subtract (1/L)*Pgt from matrix
            for j in range(1, M + 1):
                Pgt = pref_p[j][y_hi] - (pref_p[j][y_lo - 1] if y_lo > 1 else 0.0)
                A_mat[t - 1][j - 1] -= invL * Pgt
        else:
            Qgt = 0.0

        rhs = const1 + invL * Qgt + (invL * constB1 if eq else 0.0)
        b_vec[t - 1] = rhs

        # +1 on diagonal
        A_mat[t - 1][t - 1] += 1.0

        # subtract eq*(1/L)*b1[j] from every column if eq
        if eq:
            for j in range(1, M + 1):
                A_mat[t - 1][j - 1] -= invL * b1[j]

    sol = gauss_solve([row[:] for row in A_mat], b_vec[:])

    C1 = [0.0] * (M + 1)
    for j in range(1, M + 1):
        C1[j] = sol[j - 1]

    # compute B0 from C1
    ss = 0.0
    for d in range(1, L):
        ss += (L - d) * 2.0 * C1[d]
    B0 = k * (EminA + ss / (L * L))

    return C1, B0


# -------------------------------------------------
# Optional iterative solver (fast for wide ranges)
# -------------------------------------------------


def compute_C1_iterative(n: int, m: int, max_iter=2000, tol=1e-12):
    """
    Fixed-point relaxation solver for large L (typically fast).
    Falls back to RuntimeError if no convergence.
    """
    L = m - n + 1
    A_low = n + 5
    A_high = m + 5
    M = A_high

    EminA = expected_min_consecutive(A_low, A_high)
    k = L / (L - 1.0)

    def compute_B0(C1):
        ss = 0.0
        for d in range(1, L):
            ss += (L - d) * 2.0 * C1[d]
        return k * (EminA + ss / (L * L))

    def compute_B1(C0):
        ss = 0.0
        for d in range(1, L):
            ss += (L - d) * C0[d]
        return k * (EminA + ss / (L * L))

    def prefix(arr):
        p = [0.0] * (M + 1)
        s = 0.0
        for i in range(1, M + 1):
            s += arr[i]
            p[i] = s
        return p

    invL = 1.0 / L
    meanA = (A_low + A_high) / 2.0

    C1 = [0.0] * (M + 1)
    C0 = [0.0] * (M + 1)
    for x in range(1, M + 1):
        C1[x] = meanA + min(meanA, x)
        C0[x] = meanA + x

    # relaxation factor: safe moderate over-relaxation
    w = 1.15

    for _ in range(max_iter):
        # C0 from C1
        pref1 = prefix(C1)
        B0 = compute_B0(C1)
        newC0 = [0.0] * (M + 1)
        for x in range(1, M + 1):
            lt_low = A_low
            lt_high = min(A_high, x - 1)
            sum_lt_a = arith_sum(lt_low, lt_high)
            sum_lt_C = 0.0
            if lt_low <= lt_high:
                y_lo = x - lt_high
                y_hi = x - lt_low
                sum_lt_C = pref1[y_hi] - (pref1[y_lo - 1] if y_lo > 1 else 0.0)

            gt_low = max(A_low, x + 1)
            gt_high = A_high
            count_gt = max(0, gt_high - gt_low + 1)
            base_gt = count_gt * x
            sum_gt_C = 0.0
            if gt_low <= gt_high:
                y_lo = gt_low - x
                y_hi = gt_high - x
                sum_gt_C = pref1[y_hi] - (pref1[y_lo - 1] if y_lo > 1 else 0.0)

            eq = A_low <= x <= A_high
            total = sum_lt_a + sum_lt_C + base_gt + sum_gt_C + (x + B0 if eq else 0.0)
            newC0[x] = total * invL

        for x in range(1, M + 1):
            C0[x] = C0[x] + w * (newC0[x] - C0[x])

        # C1 from C0
        pref0 = prefix(C0)
        B1 = compute_B1(C0)
        newC1 = [0.0] * (M + 1)
        for x in range(1, M + 1):
            lt_low = A_low
            lt_high = min(A_high, x - 1)
            sum_lt_a = arith_sum(lt_low, lt_high)

            gt_low = max(A_low, x + 1)
            gt_high = A_high
            count_gt = max(0, gt_high - gt_low + 1)
            base_gt = count_gt * x
            sum_gt_C = 0.0
            if gt_low <= gt_high:
                y_lo = gt_low - x
                y_hi = gt_high - x
                sum_gt_C = pref0[y_hi] - (pref0[y_lo - 1] if y_lo > 1 else 0.0)

            eq = A_low <= x <= A_high
            total = sum_lt_a + base_gt + sum_gt_C + (x + B1 if eq else 0.0)
            newC1[x] = total * invL

        err = 0.0
        for x in range(1, M + 1):
            v = C1[x] + w * (newC1[x] - C1[x])
            if not isfinite(v):
                raise RuntimeError("Diverged")
            err = max(err, abs(v - C1[x]))
            C1[x] = v

        if err < tol:
            B0 = compute_B0(C1)
            return C1, B0

    raise RuntimeError("No convergence")


# ----------------------------
# Expected game time E(m,n)
# ----------------------------


def expected_game(m: int, n: int) -> float:
    """
    Expected duration (seconds) for the given (m,n).
    Uses hybrid solver:
      - Try iterative for wide ranges (typically fast)
      - Fall back to direct Gaussian elimination
    """
    L = m - n + 1
    # heuristic: iteration works well when L is wide
    if L >= 25:
        try:
            C1, B0 = compute_C1_iterative(n, m)
        except Exception:
            C1, B0 = compute_C1_direct(n, m)
    else:
        C1, B0 = compute_C1_direct(n, m)

    Emin0 = expected_min_consecutive(n, m)

    # Expected value of C1(|U-V|) for U,V uniform [n..m]
    s = B0 * (1.0 / L)  # diff=0
    denom = L * L
    for d in range(1, L):
        prob = 2.0 * (L - d) / denom
        s += prob * C1[d]

    return Emin0 + s


def S(k: int) -> float:
    """S(k) = sum_{m=2..k} sum_{n=1..m-1} E(m,n)."""
    total = 0.0
    for m in range(2, k + 1):
        for n in range(1, m):
            total += expected_game(m, n)
    return total


# ----------------------------
# Main + required asserts
# ----------------------------


def main():
    # tests from problem statement
    e = expected_game(60, 30)
    assert round(e + 1e-9, 2) == 1036.15, e

    s5 = S(5)
    assert round(s5 + 1e-9, 2) == 7722.82, s5

    ans = S(100)
    print(f"{ans:.2f}")


if __name__ == "__main__":
    main()
