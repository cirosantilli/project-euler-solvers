#!/usr/bin/env python3
"""Project Euler 676: Matching Digit Sums

Let d(i, b) be the digit sum of i written in base b.
Let M(n, b1, b2) be the sum of all i <= n such that d(i, b1) = d(i, b2).

We need:
    sum_{k=3..6} sum_{l=1..k-2} M(10^16, 2^k, 2^l)
    (last 16 digits)

No external libraries are used.
"""

MOD = 10**16
TARGET_N = 10**16


def M_power2_bases(n: int, k: int, l: int) -> int:
    """Return M(n, 2^k, 2^l).

    Key identity for power-of-two bases:
      If i = sum_{p>=0} b_p 2^p with b_p in {0,1}, then
      d(i, 2^m) = sum_{p>=0} b_p * 2^(p mod m).

    Therefore, the condition d(i,2^k) = d(i,2^l) becomes a single integer equation
    on the bits:
        sum b_p * (2^(p mod k) - 2^(p mod l)) = 0.

    We count/sum all numbers <= n with a digit DP over the binary representation of n,
    keeping only the running difference of digit sums as state.

    Returns the exact sum (Python int).
    """
    if n <= 0:
        return 0
    if k <= 0 or l <= 0:
        raise ValueError("k and l must be positive")

    bits = [int(c) for c in bin(n)[2:]]  # MSB -> LSB
    B = len(bits)

    # DP maps: diff -> (count, sum_of_values)
    # tight: prefix equals n so far; loose: prefix already smaller.
    tight = {0: (1, 0)}
    loose = {}

    for idx, lim in enumerate(bits):
        p = B - 1 - idx  # actual bit position counted from LSB
        c = (1 << (p % k)) - (
            1 << (p % l)
        )  # contribution to (d_k - d_l) if this bit is 1
        w = 1 << p  # contribution to the number's value if this bit is 1

        new_tight = {}
        new_loose = {}

        # Extend loose states: next bit can be 0 or 1.
        for diff, (cnt, sm) in loose.items():
            # bit 0
            a, b = new_loose.get(diff, (0, 0))
            new_loose[diff] = (a + cnt, b + sm)

            # bit 1
            d1 = diff + c
            a, b = new_loose.get(d1, (0, 0))
            new_loose[d1] = (a + cnt, b + sm + w * cnt)

        # Extend tight states: next bit is 0..lim.
        for diff, (cnt, sm) in tight.items():
            if lim == 0:
                # only bit 0 keeps us tight
                a, b = new_tight.get(diff, (0, 0))
                new_tight[diff] = (a + cnt, b + sm)
            else:
                # choose 0 -> becomes loose
                a, b = new_loose.get(diff, (0, 0))
                new_loose[diff] = (a + cnt, b + sm)

                # choose 1 -> stays tight
                d1 = diff + c
                a, b = new_tight.get(d1, (0, 0))
                new_tight[d1] = (a + cnt, b + sm + w * cnt)

        tight, loose = new_tight, new_loose

    ans = 0
    if 0 in tight:
        ans += tight[0][1]
    if 0 in loose:
        ans += loose[0][1]
    return ans


def solve() -> int:
    total = 0
    for k in range(3, 7):
        for l in range(1, k - 1):  # 1..k-2 inclusive
            total += M_power2_bases(TARGET_N, k, l)
    return total % MOD


if __name__ == "__main__":
    # Tests from the problem statement.
    assert M_power2_bases(10, 3, 1) == 18
    assert M_power2_bases(100, 3, 1) == 292
    assert M_power2_bases(10**6, 3, 1) == 19173952

    print(f"{solve():016d}")
