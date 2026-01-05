from __future__ import annotations

from typing import Dict, List, Tuple


def v_factor(n: int, p: int) -> int:
    cnt = 0
    while n % p == 0:
        n //= p
        cnt += 1
    return cnt


def precompute_counts(m: int) -> Tuple[List[List[int]], List[List[int]]]:
    """Return (count_val, inc_code) for base-3 encoded counts of size m."""
    total = 3**m
    pow3 = [1] * (m + 1)
    for i in range(1, m + 1):
        pow3[i] = pow3[i - 1] * 3
    count_val = [[0] * m for _ in range(total)]
    inc_code = [[0] * m for _ in range(total)]
    for code in range(total):
        tmp = code
        counts = [0] * m
        for i in range(m):
            counts[i] = tmp % 3
            tmp //= 3
        for i in range(m):
            count_val[code][i] = counts[i]
            new = counts[i] + 1
            if new > 2:
                new = 2
            inc_code[code][i] = code + (new - counts[i]) * pow3[i]
    return count_val, inc_code


def count_one_child_coprime(d: int) -> int:
    inv10 = pow(10, -1, d)
    w = [0] * (d + 1)
    w[1] = inv10 % d
    for i in range(2, d + 1):
        w[i] = (w[i - 1] * inv10) % d

    delta_counts: List[List[Tuple[int, int]]] = []
    for i in range(1, d + 1):
        digits = range(1, 10) if i == 1 else range(10)
        counts: Dict[int, int] = {}
        wi = w[i]
        for digit in digits:
            delta = (digit * wi) % d
            counts[delta] = counts.get(delta, 0) + 1
        delta_counts.append(list(counts.items()))

    dp0: Dict[int, int] = {((1 << 0) << 5) | 0: 1}
    dp1: Dict[int, int] = {}
    for i in range(d):
        next0: Dict[int, int] = {}
        next1: Dict[int, int] = {}
        for key, ways in dp0.items():
            mask = key >> 5
            r = key & 31
            for delta, cnt in delta_counts[i]:
                r2 = r + delta
                if r2 >= d:
                    r2 -= d
                bit = 1 << r2
                if mask & bit:
                    key2 = (mask << 5) | r2
                    next1[key2] = next1.get(key2, 0) + ways * cnt
                else:
                    key2 = ((mask | bit) << 5) | r2
                    next0[key2] = next0.get(key2, 0) + ways * cnt
        for key, ways in dp1.items():
            mask = key >> 5
            r = key & 31
            for delta, cnt in delta_counts[i]:
                r2 = r + delta
                if r2 >= d:
                    r2 -= d
                bit = 1 << r2
                if mask & bit:
                    continue
                key2 = ((mask | bit) << 5) | r2
                next1[key2] = next1.get(key2, 0) + ways * cnt
        dp0, dp1 = next0, next1
    return sum(dp1.values())


def count_one_child_with_t(d: int) -> int:
    a = v_factor(d, 2)
    b = v_factor(d, 5)
    t = (2**a) * (5**b)
    m = d // t
    L = max(a, b)

    count_val, inc_code = precompute_counts(m if m > 0 else 1)

    if m > 1:
        inv10 = pow(10, -1, m)
        w = [0] * (d + 1)
        w[1] = inv10 % m
        for i in range(2, d + 1):
            w[i] = (w[i - 1] * inv10) % m
    else:
        w = [0] * (d + 1)

    if L == 1:
        dp = [dict() for _ in range(3)]
        start_code = inc_code[0][0]
        dp[0][(start_code, 0)] = 1
        for pos in range(1, d + 1):
            next_dp = [dict() for _ in range(3)]
            digits = range(1, 10) if pos == 1 else range(10)
            wi = w[pos]
            for div_count in range(3):
                for (counts_code, q), ways in dp[div_count].items():
                    for digit in digits:
                        q_next = (q + digit * wi) % m if m > 1 else 0
                        new_div = 0
                        if digit % t == 0:
                            new_div = count_val[counts_code][q_next]
                        new_total = div_count + new_div
                        if new_total > 2:
                            new_total = 2
                        new_counts_code = inc_code[counts_code][q_next]
                        key = (new_counts_code, q_next)
                        next_dp[new_total][key] = next_dp[new_total].get(key, 0) + ways
            dp = next_dp
        return sum(dp[1].values())

    mod10L = 10**L
    next_tail = [[0] * 10 for _ in range(mod10L)]
    short_mask = [0] * mod10L
    long_ok = [False] * mod10L
    pow10 = [1] * (L + 1)
    for i in range(1, L + 1):
        pow10[i] = pow10[i - 1] * 10
    for tail in range(mod10L):
        long_ok[tail] = tail % t == 0
        mask = 0
        for l in range(1, L):
            if (tail % pow10[l]) % t == 0:
                mask |= 1 << (l - 1)
        short_mask[tail] = mask
        base = (tail * 10) % mod10L
        for digit in range(10):
            next_tail[tail][digit] = (base + digit) % mod10L

    dp = [dict() for _ in range(3)]
    dp[0][(0, (0,), 0)] = 1
    for pos in range(1, d + 1):
        next_dp = [dict() for _ in range(3)]
        digits = range(1, 10) if pos == 1 else range(10)
        wi = w[pos]
        for div_count in range(3):
            for (counts_code, recent, tail), ways in dp[div_count].items():
                current_q = recent[-1]
                max_l = L - 1
                if pos < max_l:
                    max_l = pos
                for digit in digits:
                    q_next = (current_q + digit * wi) % m if m > 1 else 0
                    new_tail = next_tail[tail][digit]
                    mask = short_mask[new_tail]
                    new_div = 0
                    if mask:
                        for l in range(1, max_l + 1):
                            if mask & (1 << (l - 1)):
                                if recent[-l] == q_next:
                                    new_div += 1
                    if pos >= L and long_ok[new_tail]:
                        new_div += count_val[counts_code][q_next]
                    if new_div > 2:
                        new_div = 2
                    new_total = div_count + new_div
                    if new_total > 2:
                        new_total = 2
                    new_recent = recent + (q_next,)
                    new_counts_code = counts_code
                    if len(new_recent) > L - 1:
                        oldest = new_recent[0]
                        new_counts_code = inc_code[new_counts_code][oldest]
                        new_recent = new_recent[1:]
                    key = (new_counts_code, new_recent, new_tail)
                    next_dp[new_total][key] = next_dp[new_total].get(key, 0) + ways
        dp = next_dp
    return sum(dp[1].values())


def count_one_child(d: int) -> int:
    if d == 1:
        return 9
    if d % 2 != 0 and d % 5 != 0:
        return count_one_child_coprime(d)
    return count_one_child_with_t(d)


def solve() -> int:
    total = 0
    for d in range(1, 20):
        total += count_one_child(d)
    return total


if __name__ == "__main__":
    f10 = sum(count_one_child(d) for d in range(1, 2))
    assert f10 == 9
    f10_3 = sum(count_one_child(d) for d in range(1, 4))
    assert f10_3 == 389
    f10_7 = sum(count_one_child(d) for d in range(1, 8))
    assert f10_7 == 277674
    print(solve())
