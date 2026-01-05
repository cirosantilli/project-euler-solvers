from typing import Callable, Tuple


def build_omega_odd(limit: int) -> bytearray:
    n_odd = limit // 2 + 1
    omega = bytearray(n_odd)
    om = omega
    lim = limit
    for p in range(3, lim + 1, 2):
        if om[p >> 1] == 0:
            step = p << 1
            for m in range(p, lim + 1, step):
                om[m >> 1] += 1
    return omega


def build_block_prefix(
    limit: int, omega: bytearray, block_size: int
) -> Tuple[list[int], list[int]]:
    num_blocks = limit // block_size + 1
    even = [0] * (num_blocks + 1)
    odd = [0] * (num_blocks + 1)
    om = omega
    B = block_size
    even_arr = even
    odd_arr = odd

    for s in range(2, limit + 1, 2):
        oddpart = s // (s & -s)
        even_arr[s // B + 1] += 1 << om[oddpart >> 1]

    for s in range(3, limit + 1, 2):
        om_s = om[s >> 1]
        if om_s:
            odd_arr[s // B + 1] += 1 << (om_s - 1)

    for i in range(1, len(even_arr)):
        even_arr[i] += even_arr[i - 1]
        odd_arr[i] += odd_arr[i - 1]

    return even, odd


def make_sum_funcs(
    limit: int,
    omega: bytearray,
    even_prefix: list[int],
    odd_prefix: list[int],
    block_size: int,
) -> Tuple[Callable[[int, int], int], Callable[[int, int], int]]:
    B = block_size
    om = omega
    even_pref = even_prefix
    odd_pref = odd_prefix

    def sum_even_range(L: int, R: int) -> int:
        if L & 1:
            L += 1
        res = 0
        s = L
        while s <= R:
            oddpart = s // (s & -s)
            res += 1 << om[oddpart >> 1]
            s += 2
        return res

    def sum_odd_range(L: int, R: int) -> int:
        if L % 2 == 0:
            L += 1
        res = 0
        s = L
        while s <= R:
            om_s = om[s >> 1]
            if om_s:
                res += 1 << (om_s - 1)
            s += 2
        return res

    def sum_even(L: int, R: int) -> int:
        if L > R:
            return 0
        if L & 1:
            L += 1
        if L > R:
            return 0
        bL = L // B
        bR = R // B
        if bL == bR:
            return sum_even_range(L, R)
        res = even_pref[bR] - even_pref[bL + 1]
        res += sum_even_range(L, (bL + 1) * B - 1)
        res += sum_even_range(bR * B, R)
        return res

    def sum_odd(L: int, R: int) -> int:
        if L > R:
            return 0
        if L % 2 == 0:
            L += 1
        if L > R:
            return 0
        bL = L // B
        bR = R // B
        if bL == bR:
            return sum_odd_range(L, R)
        res = odd_pref[bR] - odd_pref[bL + 1]
        res += sum_odd_range(L, (bL + 1) * B - 1)
        res += sum_odd_range(bR * B, R)
        return res

    return sum_even, sum_odd


def compute_F(
    R: int,
    X: int,
    sum_even: Callable[[int, int], int],
    sum_odd: Callable[[int, int], int],
) -> int:
    M = min(R, X)
    res = 0
    s = 1
    while s <= M:
        T = R // s
        D = X // s
        end = min(M, R // T, X // D)

        t_even = T // 2
        t_odd = (T + 1) // 2
        odd_count = (D + 1) // 2
        even_count = D // 2
        per_a = 4 * (odd_count * t_odd + even_count * t_even)
        per_b = 4 * T * D

        res += per_a * sum_even(s, end)
        res += per_b * sum_odd(s, end)
        s = end + 1

    res += 2 * R * X
    return res


def main() -> None:
    r1, x1 = 10**8, 10**9
    r2, x2 = 10**9, 10**8
    limit = min(r1, x1, r2, x2)

    block_size = 1 << 10
    omega = build_omega_odd(limit)
    even_prefix, odd_prefix = build_block_prefix(limit, omega, block_size)
    sum_even, sum_odd = make_sum_funcs(
        limit, omega, even_prefix, odd_prefix, block_size
    )

    assert compute_F(1, 5, sum_even, sum_odd) == 10
    assert compute_F(2, 10, sum_even, sum_odd) == 52
    assert compute_F(10, 100, sum_even, sum_odd) == 3384

    result = compute_F(r1, x1, sum_even, sum_odd) + compute_F(r2, x2, sum_even, sum_odd)
    print(result)


if __name__ == "__main__":
    main()
