#!/usr/bin/env python3
"""
Project Euler 691
Long substring with many repetitions

We need the sum of non-zero L(k, S_N) for k >= 1 where:
- a_n is the Thue–Morse sequence (parity of popcount)
- b_n = floor((n+1)/phi) - floor(n/phi)
- c_n = a_n XOR b_n
- S_N is the string c_0..c_{N-1}

Approach:
Build a suffix automaton (SAM) of S_N (binary alphabet). For each SAM state,
compute its occurrence count (endpos size). Then:

L(k, S) = max_{state with occ >= k} maxlen[state]

So we bucket best[occ] = max(maxlen), then take a suffix maximum over k.
Finally sum best[k] while > 0.

No external libraries are used.
"""

from array import array
import math
import sys


def _sum_nonzero_L(n: int, return_best: bool = False):
    """Return (sum_{k>=1, L(k)>0} L(k,S_n), best_array_if_requested).

    best[k] (1<=k<=n) will equal L(k, S_n) after the suffix-maximum pass.
    """
    # Generate b_n using an incremental floor of (n / phi).
    # inv_phi = 1/phi = (sqrt(5)-1)/2
    inv_phi = (math.sqrt(5.0) - 1.0) * 0.5

    # Suffix automaton with fixed binary transitions.
    # State indices: 0 is a dummy sentinel; 1 is the root.
    nxt0 = array('I', [0, 0])
    nxt1 = array('I', [0, 0])
    link = array('I', [0, 0])
    maxlen = array('I', [0, 0])
    occ = array('I', [0, 0])

    last = 1
    size = 2

    # Local bindings for speed
    nxt0_append = nxt0.append
    nxt1_append = nxt1.append
    link_append = link.append
    maxlen_append = maxlen.append
    occ_append = occ.append

    acc = 0.0
    prev_floor = 0

    for i in range(n):
        # b_i = floor((i+1)/phi) - floor(i/phi)
        acc += inv_phi
        cur_floor = int(acc)
        b = cur_floor - prev_floor
        prev_floor = cur_floor

        # a_i is parity of popcount(i)
        ch = (i.bit_count() & 1) ^ b  # c_i = a_i XOR b_i

        cur = size
        size += 1

        nxt0_append(0)
        nxt1_append(0)
        link_append(0)
        maxlen_append(maxlen[last] + 1)
        occ_append(1)

        p = last
        if ch == 0:
            while p and nxt0[p] == 0:
                nxt0[p] = cur
                p = link[p]
            if p == 0:
                link[cur] = 1
            else:
                q = nxt0[p]
                if maxlen[p] + 1 == maxlen[q]:
                    link[cur] = q
                else:
                    clone = size
                    size += 1

                    nxt0_append(nxt0[q])
                    nxt1_append(nxt1[q])
                    link_append(link[q])
                    maxlen_append(maxlen[p] + 1)
                    occ_append(0)

                    while p and nxt0[p] == q:
                        nxt0[p] = clone
                        p = link[p]
                    link[q] = clone
                    link[cur] = clone
        else:
            while p and nxt1[p] == 0:
                nxt1[p] = cur
                p = link[p]
            if p == 0:
                link[cur] = 1
            else:
                q = nxt1[p]
                if maxlen[p] + 1 == maxlen[q]:
                    link[cur] = q
                else:
                    clone = size
                    size += 1

                    nxt0_append(nxt0[q])
                    nxt1_append(nxt1[q])
                    link_append(link[q])
                    maxlen_append(maxlen[p] + 1)
                    occ_append(0)

                    while p and nxt1[p] == q:
                        nxt1[p] = clone
                        p = link[p]
                    link[q] = clone
                    link[cur] = clone

        last = cur

    # Transitions are no longer needed; free memory early.
    del nxt0, nxt1

    # Counting sort states by maxlen to propagate occurrence counts.
    cnt = array('I', [0]) * (n + 1)
    for v in range(1, size):
        cnt[maxlen[v]] += 1
    for L in range(1, n + 1):
        cnt[L] += cnt[L - 1]

    order = array('I', [0]) * (size - 1)  # states 1..size-1
    for v in range(size - 1, 0, -1):
        L = maxlen[v]
        cnt[L] -= 1
        order[cnt[L]] = v

    del cnt

    # Propagate occurrences from longer states to suffix links.
    for idx in range(size - 2, 0, -1):  # skip root at order[0]
        v = order[idx]
        occ[link[v]] += occ[v]

    del order

    # best[k] = maximum maxlen among states with exactly k occurrences
    best = array('I', [0]) * (n + 1)
    for v in range(1, size):
        k = occ[v]
        L = maxlen[v]
        if L > best[k]:
            best[k] = L

    # Turn it into L(k): maximum length among states with occurrences >= k.
    for k in range(n - 1, 0, -1):
        if best[k] < best[k + 1]:
            best[k] = best[k + 1]

    total = 0
    for k in range(1, n + 1):
        v = best[k]
        if v == 0:
            break
        total += v

    if return_best:
        return total, best
    return total, None


def _self_test():
    # Test values provided in the problem statement.
    _, b10 = _sum_nonzero_L(10, return_best=True)
    assert b10[2] == 5
    assert b10[3] == 2

    _, b100 = _sum_nonzero_L(100, return_best=True)
    assert b100[2] == 14
    assert b100[4] == 6

    s1000, b1000 = _sum_nonzero_L(1000, return_best=True)
    assert b1000[2] == 86
    assert b1000[3] == 45
    assert b1000[5] == 31
    assert s1000 == 2460


def main():
    _self_test()

    n = 5_000_000
    ans, _ = _sum_nonzero_L(n, return_best=False)
    sys.stdout.write(str(ans) + "\n")


if __name__ == "__main__":
    main()
