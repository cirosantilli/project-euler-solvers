#!/usr/bin/env python3
"""
Project Euler 472 - Comfortable Distance II

We compute:
    sum_{1 <= N <= 10^12} f(N)  (last 8 digits)

where f(N) is the number of first-seat choices that maximize the final number
of seated people under the problem's greedy "furthest seat" rule + no adjacency.

No external libraries are used.
"""

MOD = 10**8

# ------------------------------------------------------------
# Small brute-force support (only for base range and asserts)
# ------------------------------------------------------------


def A(n: int) -> int:
    """
    A(n) = number of occupants that will end up seated in a free edge segment
    of length n, adjacent to exactly one occupied seat.

    Derived closed form:
        let t = n+1
        p = highest power of two <= t
        A(n) = max(p/2, t - p)  (where t-p = n+1-p = n-(p-1))
    """
    if n <= 0:
        return 0
    t = n + 1
    p = 1 << (t.bit_length() - 1)
    return max(p >> 1, t - p)


def brute_f(N: int) -> int:
    """
    Brute f(N) using the derived independence:
        occupancy(p) = 1 + A(left_len) + A(right_len)
    and f(N) counts how many p maximize occupancy.

    Works fast for small N (used for base table / asserts).
    """
    if N == 1:
        return 1
    if N == 2:
        return 2

    # edge starts (p=1 or p=N) produce: 1 + A(N-2)
    edge = A(N - 2)

    # interior p=2..N-1 corresponds to x from 0..M with M=N-3
    M = N - 3
    best = -1
    cnt = 0
    for x in range(M + 1):
        val = A(x) + A(M - x)
        if val > best:
            best = val
            cnt = 1
        elif val == best:
            cnt += 1

    mx = edge if edge > best else best
    ans = 0
    if edge == mx:
        ans += 2  # p=1 and p=N
    if best == mx:
        ans += cnt  # p=2..N-1
    return ans


BASE = 64
F_BASE = [0] * (BASE + 1)
PREF_BASE = [0] * (BASE + 1)

for n in range(1, BASE + 1):
    F_BASE[n] = brute_f(n)
    PREF_BASE[n] = PREF_BASE[n - 1] + F_BASE[n]


# ------------------------------------------------------------
# Fast individual f(N) for large N (recurrence by leading bits)
# ------------------------------------------------------------


def f_fast(N: int) -> int:
    """
    Compute f(N) for any N using derived binary-block recurrences:

    Let pow=highest power of two <= N, half=pow/2.

    If N is in the '11' block: [pow+half, 2*pow-1] = [3*half, 4*half-1]
        f(N) has an explicit piecewise formula in terms of offset j=N-3*half.

    If N is in the '10' block: [pow, pow+half-1] = [2*half, 3*half-1]
        f(N) is mostly a copy of f(N-half) with a correction on the last quarter.
    """
    if N <= BASE:
        return F_BASE[N]

    pow2 = 1 << (N.bit_length() - 1)
    half = pow2 >> 1
    split = pow2 + half  # start of '11' block

    if N >= split:
        # '11' block with parameter k = log2(half)
        j = N - split  # offset in [0..half-1]
        # k >= 3 for large N; if small, fallback:
        k = half.bit_length() - 1
        if k < 3:
            return brute_f(N)

        m = 1 << (k - 1)  # = half/2
        if j == 0:
            return 4
        if 1 <= j <= m:
            return 2 * j
        if j == m + 1:
            return 3 * m + 3
        # tail: decreasing by 1
        return half + 4 - j

    # '10' block
    u = N - pow2  # in [0..half-1]
    mapped = f_fast(N - half)  # N - half = half + u, smaller bit-length

    # Correction applies only when half=2^k with k>=4 (i.e. N large enough)
    k = half.bit_length() - 1
    if k >= 4:
        u0 = half - (half >> 2) + 1  # 3/4*half + 1
        if u >= u0:
            mapped += half - u
    return mapped


# ------------------------------------------------------------
# Prefix sums Σ f(N) for huge N (recursive splitting)
# ------------------------------------------------------------

SUM_MEMO = {}


def prefix_sum_11_block(half: int, length: int) -> int:
    """
    Sum of f(N) over the first `length` elements of the '11' block:
        N in [3*half, 4*half-1], take N=3*half..3*half+length-1

    half is a power of 2: half=2^k
    Uses the explicit closed-form piecewise sequence.
    """
    if length <= 0:
        return 0
    k = half.bit_length() - 1
    if k < 3:
        # small fallback
        s = 0
        start = 3 * half
        for n in range(start, start + length):
            s += brute_f(n)
        return s

    m = half >> 1  # 2^(k-1)

    # sequence parts:
    # j=0 -> 4
    # j=1..m -> 2j
    # j=m+1 -> 3m+3
    # j=m+2..half-1 -> (half+4-j)

    s = 0
    j = 0

    # part 1
    s += 4
    length -= 1
    if length == 0:
        return s

    # part 2: j=1..min(m, length)
    take = min(m, length)
    # sum_{j=1..take} 2j = take*(take+1)
    s += take * (take + 1)
    length -= take
    j += take
    if length == 0:
        return s

    # part 3: j=m+1 (only if we reached it)
    if j == m:
        s += 3 * m + 3
        length -= 1
        j += 1
        if length == 0:
            return s

    # part 4: descending by 1 starting from value (m+2)
    # at j=m+2, value = half+4-(m+2) = m+2
    # so values form arithmetic sequence: (m+2), (m+1), ...
    a1 = m + 2
    cnt = length
    s += cnt * (2 * a1 - (cnt - 1)) // 2
    return s


def sum_upto(N: int) -> int:
    """
    Return Σ_{1<=n<=N} f(n) mod 1e8 using recursive decomposition by bit blocks.
    """
    if N <= BASE:
        return PREF_BASE[N] % MOD
    if N in SUM_MEMO:
        return SUM_MEMO[N]

    pow2 = 1 << (N.bit_length() - 1)  # highest power of 2 <= N
    if N == pow2 - 1:
        # pure power block endpoint can be memoized naturally
        pass

    half = pow2 >> 1
    split = pow2 + half  # start of '11' block

    # sum below pow2:
    res = sum_upto(pow2 - 1)

    # now sum within [pow2..N]
    if N < split:
        # Only '10' part partially
        u_max = N - pow2  # 0..half-1
        # mapped range in smaller block: [half .. half+u_max]
        mapped_sum = (sum_upto(half + u_max) - sum_upto(half - 1)) % MOD

        # correction triangular partial
        k = half.bit_length() - 1
        if k >= 4:
            u0 = half - (half >> 2) + 1
            if u_max >= u0:
                a = u0
                b = u_max
                cnt = b - a + 1
                # sum_{u=a..b} (half-u)
                # = cnt*half - (a+b)*cnt/2
                corr = cnt * half - (a + b) * cnt // 2
                mapped_sum = (mapped_sum + corr) % MOD

        res = (res + mapped_sum) % MOD
        SUM_MEMO[N] = res
        return res

    # full '10' part
    # mapped full = sum over [half..pow2-1]
    sum_small_block = (sum_upto(pow2 - 1) - sum_upto(half - 1)) % MOD

    # full correction: tail length = half/4 - 1 when k>=4
    k = half.bit_length() - 1
    if k >= 4:
        tail_len = (half >> 2) - 1
        corr_full = tail_len * (tail_len + 1) // 2
        sum10 = (sum_small_block + corr_full) % MOD
    else:
        # small block brute
        sum10 = 0
        for n in range(pow2, split):
            sum10 += brute_f(n)
        sum10 %= MOD

    res = (res + sum10) % MOD

    # partial '11' part
    len11 = N - split + 1
    res = (res + prefix_sum_11_block(half, len11)) % MOD

    SUM_MEMO[N] = res
    return res


# ------------------------------------------------------------
# Main execution + asserts from statement
# ------------------------------------------------------------


def main():
    # Problem statement test asserts:
    assert f_fast(1) == 1
    assert f_fast(15) == 9
    assert f_fast(20) == 6
    assert f_fast(500) == 16

    assert sum_upto(20) % MOD == 83
    assert sum_upto(500) % MOD == 13343

    # Required answer:
    LIMIT = 10**12
    ans = sum_upto(LIMIT) % MOD
    print(str(ans).zfill(8))


if __name__ == "__main__":
    main()
