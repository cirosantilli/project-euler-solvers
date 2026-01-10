#!/usr/bin/env python3
"""
Project Euler 663: Sums of Subarrays

We maintain an array A_n that receives point updates. After each update, M_n(i) is the
maximum sum over all contiguous subarrays. We need:

S(n, 10_200_000) - S(n, 10_000_000) = sum_{i=10_000_001..10_200_000} M_n(i)

Key idea: we only need M_n(i) for the last 200,000 steps, so we:
1) Apply the first 10,000,000 updates directly to A (no queries).
2) Build a block-based segment tree once from A.
3) For the next 200,000 steps, after each point update:
   - recompute the updated block summary by scanning that block,
   - update the segment tree over blocks,
   - add the root's maximum subarray sum to the answer.

No external libraries are used (only Python standard library).
"""

from array import array


NEG_INF = -(
    10**18
)  # safely below any achievable subarray sum magnitude in this problem


def max_subarray_kadane(arr):
    """Maximum subarray sum for a non-empty array (Kadane's algorithm)."""
    cur = best = arr[0]
    for x in arr[1:]:
        s = cur + x
        cur = x if s < x else s
        best = best if best > cur else cur
    return best


def compute_S_bruteforce(n, l):
    """
    Brute force S(n,l) for small n,l: maintain A explicitly and run Kadane each step.
    Used only for the test values from the problem statement.
    """
    A = [0] * n
    u0, u1, u2 = 0, 0, 1 % n  # t_k mod n in a rolling window for k = 2i-2, 2i-1, 2i

    total = 0
    for _ in range(l):
        idx = u0
        delta = (u1 << 1) - n + 1
        A[idx] += delta
        total += max_subarray_kadane(A)

        # advance tribonacci by two steps (mod n)
        t3 = u0 + u1 + u2
        if t3 >= n:
            t3 -= n
        if t3 >= n:
            t3 -= n
        t4 = u1 + u2 + t3
        if t4 >= n:
            t4 -= n
        if t4 >= n:
            t4 -= n
        u0, u1, u2 = u2, t3, t4

    return total


def block_summary(A, start, end):
    """
    Compute (sum, max_prefix, max_suffix, best_subarray) for A[start:end].
    All values correspond to non-empty subarrays/prefixes/suffixes.
    """
    r = 0
    max_pref = NEG_INF
    min_pref_best = 0  # min prefix sum so far (includes empty prefix)
    best = NEG_INF

    # For max suffix, we need min prefix among positions 0..len-1 (exclude full length)
    min_pref_suff = 0
    last = end - 1

    for k in range(start, end):
        r += A[k]

        if r > max_pref:
            max_pref = r

        cand = r - min_pref_best
        if cand > best:
            best = cand
        if r < min_pref_best:
            min_pref_best = r

        if k != last and r < min_pref_suff:
            min_pref_suff = r

    total = r
    max_suff = total - min_pref_suff
    return total, max_pref, max_suff, best


def build_block_tree(A, n, B):
    """
    Build an iterative segment tree over block summaries.
    Node stores: sum, max_prefix, max_suffix, best_subarray.
    """
    m = (n + B - 1) // B
    size = 1
    while size < m:
        size <<= 1

    total = array("q", [0]) * (2 * size)
    pref = array("q", [NEG_INF]) * (2 * size)
    suff = array("q", [NEG_INF]) * (2 * size)
    best = array("q", [NEG_INF]) * (2 * size)

    # leaves
    for b in range(m):
        s = b * B
        e = min(n, s + B)
        ts, tp, tu, tb = block_summary(A, s, e)
        pos = size + b
        total[pos] = ts
        pref[pos] = tp
        suff[pos] = tu
        best[pos] = tb

    # internal nodes
    for pos in range(size - 1, 0, -1):
        l = pos * 2
        r = l + 1

        ts = total[l] + total[r]
        total[pos] = ts

        v1 = pref[l]
        v2 = total[l] + pref[r]
        pref[pos] = v1 if v1 >= v2 else v2

        v1 = suff[r]
        v2 = total[r] + suff[l]
        suff[pos] = v1 if v1 >= v2 else v2

        v = best[l]
        br = best[r]
        if br > v:
            v = br
        cross = suff[l] + pref[r]
        if cross > v:
            v = cross
        best[pos] = v

    return m, size, total, pref, suff, best


def update_block(tree, A, n, B, b):
    """Recompute a single block's summary and update the segment tree path to the root."""
    m, size, total, pref, suff, best = tree  # noqa: F841 (m kept for clarity)
    s = b * B
    e = min(n, s + B)
    ts, tp, tu, tb = block_summary(A, s, e)

    pos = size + b
    total[pos] = ts
    pref[pos] = tp
    suff[pos] = tu
    best[pos] = tb

    pos //= 2
    while pos:
        l = pos * 2
        r = l + 1

        ts = total[l] + total[r]
        total[pos] = ts

        v1 = pref[l]
        v2 = total[l] + pref[r]
        pref[pos] = v1 if v1 >= v2 else v2

        v1 = suff[r]
        v2 = total[r] + suff[l]
        suff[pos] = v1 if v1 >= v2 else v2

        v = best[l]
        br = best[r]
        if br > v:
            v = br
        cross = suff[l] + pref[r]
        if cross > v:
            v = cross
        best[pos] = v

        pos //= 2


def solve():
    # Asserts for test values from the problem statement
    assert compute_S_bruteforce(5, 6) == 32
    assert compute_S_bruteforce(5, 100) == 2416
    assert compute_S_bruteforce(14, 100) == 3881
    assert compute_S_bruteforce(107, 1000) == 1618572

    n = 10_000_003
    start = 10_000_000
    end = 10_200_000

    # Block size: scanning a block is done only for the final 200k updates.
    B = 256

    A = array("q", [0]) * n

    # tribonacci mod n window for k = 2i-2, 2i-1, 2i
    u0, u1, u2 = 0, 0, 1 % n

    tree = None
    ans = 0

    for i in range(1, end + 1):
        idx = u0
        delta = (u1 << 1) - n + 1
        A[idx] += delta

        if i == start:
            # Build structure once, right after step 'start'
            tree = build_block_tree(A, n, B)
        elif i > start:
            # Maintain structure only for the final segment
            update_block(tree, A, n, B, idx // B)
            ans += tree[5][1]  # root best_subarray is M_n(i)

        # advance tribonacci by two steps (mod n), using fast reduction (sum < 3n)
        t3 = u0 + u1 + u2
        if t3 >= n:
            t3 -= n
        if t3 >= n:
            t3 -= n
        t4 = u1 + u2 + t3
        if t4 >= n:
            t4 -= n
        if t4 >= n:
            t4 -= n
        u0, u1, u2 = u2, t3, t4

    return ans


if __name__ == "__main__":
    print(solve())
