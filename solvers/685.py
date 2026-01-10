#!/usr/bin/env python3
"""
Project Euler 685: Inverse Digit Sum II

Compute S(10000) = sum_{n=1..10000} f(n^3, n^4) (mod 1_000_000_007),
where f(s, m) is the m-th positive integer (in increasing order) whose
decimal digit sum equals s.

No external libraries are used.
"""

MOD = 1_000_000_007
INV9 = pow(9, MOD - 2, MOD)


def comb(n: int, k: int) -> int:
    """Exact binomial C(n,k) for large n but (typically) small k."""
    if k < 0 or k > n:
        return 0
    k = min(k, n - k)
    if k == 0:
        return 1
    res = 1
    # Multiplicative formula avoids factorials.
    for i in range(1, k + 1):
        res = (res * (n - k + i)) // i
    return res


def count_deficit_sequences(length: int, deficit: int) -> int:
    """
    Count sequences (x_1..x_length) with 0<=x_i<=9 and sum x_i = deficit.

    This is the coefficient of z^deficit in (1+z+...+z^9)^length, computed by
    inclusion-exclusion on the upper bound 9.
    """
    if deficit < 0:
        return 0
    if length == 0:
        return 1 if deficit == 0 else 0

    # Inclusion-exclusion:
    # number of nonnegative solutions with x_i<=9:
    # sum_{j>=0} (-1)^j * C(length, j) * C(deficit - 10j + length - 1, deficit - 10j)
    res = 0
    max_j = deficit // 10
    for j in range(max_j + 1):
        d = deficit - 10 * j
        term = comb(length, j) * comb(d + length - 1, d)
        res = res - term if (j & 1) else res + term
    return res


def count_len_with_digit_sum(length: int, digit_sum: int) -> int:
    """
    Count length-digit positive integers (leading digit nonzero) with digit sum = digit_sum.
    Uses the 'deficit' transform: deficit = 9*length - digit_sum.
    """
    deficit = 9 * length - digit_sum
    if deficit < 0:
        return 0

    total = count_deficit_sequences(length, deficit)

    # Leading digit is zero <=> first deficit digit is 9 (since digit=0 => deficit=9).
    if deficit >= 9:
        total -= count_deficit_sequences(length - 1, deficit - 9)

    return total


def find_length_and_rank(digit_sum: int, m: int) -> tuple[int, int]:
    """
    Find the number of digits L such that the m-th number with digit_sum lies among
    L-digit numbers, and return (L, rank_within_L) where rank_within_L is 1-indexed.
    """
    # No number with fewer than ceil(digit_sum/9) digits can reach the required sum.
    L = (digit_sum + 8) // 9
    passed = 0
    while True:
        cnt = count_len_with_digit_sum(L, digit_sum)
        if passed + cnt >= m:
            return L, m - passed
        passed += cnt
        L += 1


def append_repeat_mod(prefix_mod: int, digit: int, count: int) -> int:
    """Append 'digit' repeated 'count' times to a number represented modulo MOD."""
    if count <= 0:
        return prefix_mod
    pow10 = pow(10, count, MOD)
    # value of block "ddd...d" (count digits) is d * (10^count - 1) / 9
    if digit == 0:
        block = 0
    else:
        block = digit * (pow10 - 1) % MOD
        block = block * INV9 % MOD
    return (prefix_mod * pow10 + block) % MOD


def f_mod(digit_sum: int, m: int) -> int:
    """
    Return f(digit_sum, m) modulo MOD.
    f(digit_sum, m) is the m-th positive integer with the given digit sum.
    """
    length, k = find_length_and_rank(digit_sum, m)  # k is rank within this length
    deficit = 9 * length - digit_sum

    # Choose the first (most significant) digit: 1..9
    value_mod = 0
    for dig in range(1, 10):
        used = 9 - dig  # deficit consumed at this digit
        if used > deficit:
            continue
        cnt = count_deficit_sequences(length - 1, deficit - used)
        if k > cnt:
            k -= cnt
        else:
            value_mod = dig % MOD
            length -= 1
            deficit -= used
            break
    else:
        raise RuntimeError("Failed to choose the leading digit")

    # Remaining digits: 0..9, unrank lexicographically using counts.
    while length > 0:
        if deficit == 0:
            # Remaining digits are all 9.
            value_mod = append_repeat_mod(value_mod, 9, length)
            break

        total = count_deficit_sequences(length, deficit)
        tail = count_deficit_sequences(
            length - 1, deficit
        )  # sequences starting with digit 9

        # If k lies in the tail block (leading digit 9), there may be a long run of 9s.
        if tail > 0 and k > total - tail:
            # Convert to "rank from the end" inside this length/deficit block.
            need = total - k + 1  # 1-indexed
            # Find the shortest suffix length t such that count_deficit_sequences(t, deficit) >= need.
            lo = (deficit + 8) // 9  # minimum digits needed to hold this deficit
            hi = length
            while lo < hi:
                mid = (lo + hi) // 2
                if count_deficit_sequences(mid, deficit) >= need:
                    hi = mid
                else:
                    lo = mid + 1
            t = lo
            prefix_9 = length - t
            if prefix_9 > 0:
                value_mod = append_repeat_mod(value_mod, 9, prefix_9)
                # Move k into the suffix block of size count_deficit_sequences(t, deficit)
                k -= total - count_deficit_sequences(t, deficit)
                length = t
                continue

        # Now the next digit is < 9 (or 9 is impossible). Try digits 0..8 in order.
        chosen = False
        for dig in range(0, 9):
            used = 9 - dig
            if used > deficit:
                continue
            cnt = count_deficit_sequences(length - 1, deficit - used)
            if k > cnt:
                k -= cnt
            else:
                value_mod = (value_mod * 10 + dig) % MOD
                length -= 1
                deficit -= used
                chosen = True
                break

        if not chosen:
            # Must be 9.
            value_mod = (value_mod * 10 + 9) % MOD
            length -= 1

    return value_mod


def S(K: int) -> int:
    """Compute S(K) modulo MOD."""
    total = 0
    for n in range(1, K + 1):
        total = (total + f_mod(n * n * n, n * n * n * n)) % MOD
    return total


def _self_test() -> None:
    # Problem statement examples for f(10, m)
    assert f_mod(10, 1) == 19
    assert f_mod(10, 10) == 109
    assert f_mod(10, 100) == 1423

    # Problem statement examples for S(k)
    assert S(3) == 7128
    assert S(10) == 32287064


def main() -> None:
    _self_test()
    print(S(10_000))


if __name__ == "__main__":
    main()
