#!/usr/bin/env python3
"""
Project Euler 488 - Unbalanced Nim

We compute the last 9 digits of F(10^18).

No external libraries are used.
"""

MOD = 10**9


def _dp_count_sum(A: int, B: int, C: int):
    """
    Digit-DP over bits.

    Returns (count, sum_total) over all triples (a,b,c) such that:
      0 <= a <= A
      0 <= b <= B
      c = a XOR b
      0 <= c <= C

    sum_total is sum over all such triples of (a + b + c).
    """
    if A < 0 or B < 0 or C < 0:
        return 0, 0

    maxbits = max(A, B, C).bit_length()
    if maxbits == 0:
        maxbits = 1

    # State: (ta, tb, tc) where t?=1 means still tight to the corresponding upper bound.
    # Encode as ta*4 + tb*2 + tc in [0..7].
    counts = [0] * 8
    sumA = [0] * 8
    sumB = [0] * 8
    sumC = [0] * 8
    counts[7] = 1  # (1,1,1)

    for p in range(maxbits - 1, -1, -1):
        bitA = (A >> p) & 1
        bitB = (B >> p) & 1
        bitC = (C >> p) & 1
        val = 1 << p

        ncounts = [0] * 8
        nsumA = [0] * 8
        nsumB = [0] * 8
        nsumC = [0] * 8

        for state in range(8):
            cnt = counts[state]
            if cnt == 0:
                continue
            sa = sumA[state]
            sb = sumB[state]
            sc = sumC[state]

            ta = (state >> 2) & 1
            tb = (state >> 1) & 1
            tc = state & 1

            for abit in (0, 1):
                if ta and abit > bitA:
                    continue
                nta = 1 if (ta and abit == bitA) else 0

                for bbit in (0, 1):
                    if tb and bbit > bitB:
                        continue
                    ntb = 1 if (tb and bbit == bitB) else 0

                    cbit = abit ^ bbit
                    if tc and cbit > bitC:
                        continue
                    ntc = 1 if (tc and cbit == bitC) else 0

                    nstate = (nta << 2) | (ntb << 1) | ntc

                    ncounts[nstate] += cnt
                    nsumA[nstate] += sa + cnt * abit * val
                    nsumB[nstate] += sb + cnt * bbit * val
                    nsumC[nstate] += sc + cnt * cbit * val

        counts, sumA, sumB, sumC = ncounts, nsumA, nsumB, nsumC

    total_count = sum(counts)
    total_sum = sum(sumA) + sum(sumB) + sum(sumC)
    return total_count, total_sum


_dp_cache = {}


def dp_count_sum(A: int, B: int, C: int):
    """Cached wrapper around _dp_count_sum()."""
    key = (A, B, C)
    out = _dp_cache.get(key)
    if out is None:
        out = _dp_count_sum(A, B, C)
        _dp_cache[key] = out
    return out


def F(N: int) -> int:
    """
    F(N) as defined in the problem statement:
      sum of (a+b+c) over losing positions with 0 < a < b < c < N.

    Key fact for 3-heap "no equal heaps" Nim:
      a position (a,b,c) is losing iff (a+1) XOR (b+1) XOR (c+1) == 0.
    """
    L = N  # after the +1 shift, the max value becomes N

    # Count ordered triples (x,y,z) with 2<=x,y,z<=L and x XOR y XOR z = 0.
    # Because z = x XOR y, this is equivalent to ordered pairs (x,y) with
    # 2<=x<=L, 2<=y<=L, and 2<=x XOR y<=L.
    #
    # We'll compute ordered solutions in [0..L] and then exclude values <=1
    # via inclusion-exclusion on the sets {x<=1}, {y<=1}, {z<=1}.
    ordered_count = 0
    ordered_sum_xyz = 0  # sum over ordered triples of (x+y+z)

    for mask in range(8):
        A = 1 if (mask & 1) else L  # x upper bound
        B = 1 if (mask & 2) else L  # y upper bound
        C = 1 if (mask & 4) else L  # z upper bound
        cnt, sm = dp_count_sum(A, B, C)
        if (mask.bit_count() & 1) == 0:
            ordered_count += cnt
            ordered_sum_xyz += sm
        else:
            ordered_count -= cnt
            ordered_sum_xyz -= sm

    # Every unordered triple {x,y,z} of distinct values corresponds to 6 ordered triples.
    # In our range (>=2), distinctness is automatic for XOR-zero triples.
    #
    # Original heaps are (a,b,c) = (x-1,y-1,z-1), so (a+b+c) = (x+y+z) - 3.
    return (ordered_sum_xyz - 3 * ordered_count) // 6


def solve() -> str:
    # Tests from the problem statement:
    assert F(8) == 42
    assert F(128) == 496062

    ans = F(10**18) % MOD
    return f"{ans:09d}"


if __name__ == "__main__":
    print(solve())
