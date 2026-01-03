#!/usr/bin/env python3
"""
Project Euler 375 - Minimum of subsequences

Let S0 = 290797
    S_{n+1} = S_n^2 mod 50515093

Let A(i,j) = min(S_i..S_j), and M(N) = sum_{1<=i<=j<=N} A(i,j).

This program prints M(2_000_000_000).
"""

from array import array

MOD = 50515093
SEED = 290797

# The PRNG outputs S1, S2, ... and (for this modulus+seed) repeats with period:
#   S_{n+6308948} = S_n   for all n >= 1
CYCLE_LEN = 6_308_948

# Test values from the problem statement
TEST_M10 = 432_256_955
TEST_M10000 = 3_264_567_774_119


def M_small(n: int) -> int:
    """Compute M(n) directly in O(n) time using a monotone stack (n is small here)."""
    s = SEED
    vals: list[int] = []
    cnts: list[int] = []
    cur_sum = 0
    total = 0

    for _ in range(n):
        s = (s * s) % MOD
        x = s

        cnt = 1
        while vals and vals[-1] >= x:
            v = vals.pop()
            c = cnts.pop()
            cur_sum -= v * c
            cnt += c

        vals.append(x)
        cnts.append(cnt)
        cur_sum += x * cnt
        total += cur_sum

    return total


def build_cycle() -> array:
    """Generate the first full period S1..S_CYCLE_LEN as 32-bit unsigned ints."""
    s = SEED
    cyc = array("I")
    append = cyc.append
    for _ in range(CYCLE_LEN):
        s = (s * s) % MOD
        append(s)

    # Lightweight sanity check: next value repeats the first one.
    s = cyc[-1]
    first = cyc[0]
    s = (s * s) % MOD
    assert s == first, "CYCLE_LEN constant is wrong (period check failed)"
    return cyc


def samples_for_remainder(r: int) -> tuple[int, int, int]:
    """
    Return:
      y1 = M(1*CYCLE_LEN + r)
      y2 = M(2*CYCLE_LEN + r)
      y3 = M(3*CYCLE_LEN + r)

    computed in a single pass over 3 full cycles plus r extra values.
    """
    cycle = build_cycle()

    t1 = CYCLE_LEN + r
    t2 = 2 * CYCLE_LEN + r
    t3 = 3 * CYCLE_LEN + r

    vals: list[int] = []
    cnts: list[int] = []
    cur_sum = 0
    total = 0

    # Collect results at t1,t2,t3 (in that order)
    out = []
    next_t = t1
    i = 0

    # Localize for speed
    vals_append = vals.append
    cnts_append = cnts.append
    vals_pop = vals.pop
    cnts_pop = cnts.pop

    def step(x: int) -> None:
        nonlocal cur_sum, total, i
        i += 1

        cnt = 1
        while vals and vals[-1] >= x:
            v = vals_pop()
            c = cnts_pop()
            cur_sum -= v * c
            cnt += c

        vals_append(x)
        cnts_append(cnt)
        cur_sum += x * cnt
        total += cur_sum

    # Process 3 full cycles
    for _ in range(3):
        for x in cycle:
            step(x)
            if i == next_t:
                out.append(total)
                if next_t == t1:
                    next_t = t2
                elif next_t == t2:
                    next_t = t3
                else:
                    break

    # Then r extra values (prefix of the next cycle)
    for idx in range(r):
        step(cycle[idx])
        if i == next_t:
            out.append(total)
            break

    assert len(out) == 3 and i == t3, "internal sampling logic error"
    return out[0], out[1], out[2]


def M_big(N: int) -> int:
    """
    Compute M(N) using the discovered PRNG period.

    For fixed remainder r, the function f(k) = M(k*CYCLE_LEN + r) is a quadratic polynomial in k.
    We compute f(1), f(2), f(3), fit the quadratic, then evaluate at k = N // CYCLE_LEN.
    """
    k, r = divmod(N, CYCLE_LEN)
    if k == 0:
        return M_small(r)

    y1, y2, y3 = samples_for_remainder(r)

    # Fit f(k) = a*k^2 + b*k + c using k=1,2,3
    # Second difference: y3 - 2*y2 + y1 = 2a
    second = y3 - 2 * y2 + y1
    assert second % 2 == 0
    a = second // 2
    b = (y2 - y1) - 3 * a
    c = y1 - a - b

    return a * k * k + b * k + c


def main() -> None:
    # Asserts required by the prompt: test values from the problem statement
    assert M_small(10) == TEST_M10
    assert M_small(10_000) == TEST_M10000

    answer = M_big(2_000_000_000)
    print(answer)


if __name__ == "__main__":
    main()
