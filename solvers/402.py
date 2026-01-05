from __future__ import annotations

from typing import Dict, List, Tuple

MOD = 1_000_000_000
DIVS = [1, 2, 3, 4, 6, 8, 12, 24]


def precompute_solutions() -> Dict[int, List[Tuple[int, int, int]]]:
    sols: Dict[int, List[Tuple[int, int, int]]] = {}
    for m in DIVS:
        arr: List[Tuple[int, int, int]] = []
        for a in range(m):
            for b in range(m):
                for c in range(m):
                    p1 = (1 + a + b + c) % m
                    p2 = (16 + 8 * a + 4 * b + 2 * c) % m
                    p3 = (81 + 27 * a + 9 * b + 3 * c) % m
                    p4 = (256 + 64 * a + 16 * b + 4 * c) % m
                    if p1 == 0 and p2 == 0 and p3 == 0 and p4 == 0:
                        arr.append((a, b, c))
        sols[m] = arr
    return sols


def compute_S(n: int, sols: Dict[int, List[Tuple[int, int, int]]]) -> int:
    if n <= 0:
        return 0
    A: Dict[int, int] = {}
    for m in DIVS:
        q, rem = divmod(n, m)
        counts = [q] * m
        for r in range(1, rem + 1):
            counts[r] += 1
        total = 0
        for a, b, c in sols[m]:
            total += counts[a] * counts[b] * counts[c]
        A[m] = total

    B: Dict[int, int] = {}
    for m in sorted(DIVS, reverse=True):
        total = A[m]
        for k in DIVS:
            if k > m and k % m == 0:
                total -= B[k]
        B[m] = total

    return sum(m * B[m] for m in DIVS)


def build_coeffs(
    sols: Dict[int, List[Tuple[int, int, int]]]
) -> List[Tuple[int, int, int, int]]:
    coeffs: List[Tuple[int, int, int, int]] = []
    for r in range(24):
        vals = [compute_S(r + 24 * t, sols) for t in range(4)]
        y0, y1, y2, y3 = vals
        d0 = y0
        d1 = y1 - y0
        d2 = y2 - 2 * y1 + y0
        d3 = y3 - 3 * y2 + 3 * y1 - y0
        coeffs.append((d0, d1, d2, d3))
    return coeffs


def mat_mul(a: List[List[int]], b: List[List[int]], mod: int) -> List[List[int]]:
    size = len(a)
    res = [[0] * size for _ in range(size)]
    for i in range(size):
        row = a[i]
        for k in range(size):
            aik = row[k]
            if aik == 0:
                continue
            brow = b[k]
            for j in range(size):
                res[i][j] = (res[i][j] + aik * brow[j]) % mod
    return res


def mat_vec_mul(a: List[List[int]], v: List[int], mod: int) -> List[int]:
    size = len(a)
    res = [0] * size
    for i in range(size):
        total = 0
        row = a[i]
        for j in range(size):
            total = (total + row[j] * v[j]) % mod
        res[i] = total
    return res


def build_mono_matrix(a: int, b: int, c: int, d: int, mod: int) -> List[List[int]]:
    m = [[0] * 10 for _ in range(10)]
    m[0][0] = 1
    m[1][1] = a
    m[1][2] = b
    m[2][1] = c
    m[2][2] = d

    m[3][3] = (a * a) % mod
    m[3][4] = (2 * a * b) % mod
    m[3][5] = (b * b) % mod

    m[4][3] = (a * c) % mod
    m[4][4] = (a * d + b * c) % mod
    m[4][5] = (b * d) % mod

    m[5][3] = (c * c) % mod
    m[5][4] = (2 * c * d) % mod
    m[5][5] = (d * d) % mod

    m[6][6] = (a * a * a) % mod
    m[6][7] = (3 * a * a * b) % mod
    m[6][8] = (3 * a * b * b) % mod
    m[6][9] = (b * b * b) % mod

    m[7][6] = (a * a * c) % mod
    m[7][7] = (a * a * d + 2 * a * b * c) % mod
    m[7][8] = (2 * a * b * d + b * b * c) % mod
    m[7][9] = (b * b * d) % mod

    m[8][6] = (a * c * c) % mod
    m[8][7] = (2 * a * c * d + b * c * c) % mod
    m[8][8] = (a * d * d + 2 * b * c * d) % mod
    m[8][9] = (b * d * d) % mod

    m[9][6] = (c * c * c) % mod
    m[9][7] = (3 * c * c * d) % mod
    m[9][8] = (3 * c * d * d) % mod
    m[9][9] = (d * d * d) % mod
    return m


def build_aug_matrix(mono: List[List[int]]) -> List[List[int]]:
    size = 14
    aug = [[0] * size for _ in range(size)]
    for i in range(10):
        for j in range(10):
            aug[i][j] = mono[i][j]

    # sum0' = sum0 + 1
    aug[10][0] = 1
    aug[10][10] = 1

    # sum1' = sum1 + y'
    for j in range(10):
        aug[11][j] = mono[2][j]
    aug[11][11] = 1

    # sum2' = sum2 + y'^2
    for j in range(10):
        aug[12][j] = mono[5][j]
    aug[12][12] = 1

    # sum3' = sum3 + y'^3
    for j in range(10):
        aug[13][j] = mono[9][j]
    aug[13][13] = 1

    return aug


def precompute_powers(
    matrix: List[List[int]], max_bits: int, mod: int
) -> List[List[List[int]]]:
    powers = [matrix]
    for _ in range(1, max_bits):
        powers.append(mat_mul(powers[-1], powers[-1], mod))
    return powers


def subseq_sums(
    k0: int,
    n_terms: int,
    fib_big: List[int],
    powers: List[List[List[int]]],
    mod: int,
) -> Tuple[int, int, int, int]:
    if n_terms <= 0:
        return (0, 0, 0, 0)

    x = fib_big[k0 + 1]
    y = fib_big[k0]

    v = [0] * 14
    v[0] = 1
    v[1] = x
    v[2] = y
    v[3] = (x * x) % mod
    v[4] = (x * y) % mod
    v[5] = (y * y) % mod
    v[6] = (v[3] * x) % mod
    v[7] = (v[3] * y) % mod
    v[8] = (v[5] * x) % mod
    v[9] = (v[5] * y) % mod

    # sums include t=0
    v[10] = 1
    v[11] = y
    v[12] = v[5]
    v[13] = v[9]

    steps = n_terms - 1
    bit = 0
    while steps:
        if steps & 1:
            v = mat_vec_mul(powers[bit], v, mod)
        steps >>= 1
        bit += 1

    return v[10], v[11], v[12], v[13]


def sum_S_fib(k_max: int, sols: Dict[int, List[Tuple[int, int, int]]]) -> int:
    if k_max < 2:
        return 0

    coeffs = build_coeffs(sols)

    # Use a modulus large enough to make division by 24^3 and by 2/6 safe via truncation.
    mod_big = 24**3 * 6 * MOD

    # Fibonacci numbers modulo mod_big for small indices.
    fib_big = [0, 1]
    for _ in range(2, 50):
        fib_big.append((fib_big[-1] + fib_big[-2]) % mod_big)

    a = fib_big[25] % mod_big
    b = fib_big[24] % mod_big
    c = fib_big[24] % mod_big
    d = fib_big[23] % mod_big

    mono = build_mono_matrix(a, b, c, d, mod_big)
    aug = build_aug_matrix(mono)

    max_bits = (k_max // 24 + 2).bit_length()
    powers = precompute_powers(aug, max_bits, mod_big)

    fib_mod24 = [0, 1]
    for _ in range(2, 24):
        fib_mod24.append((fib_mod24[-1] + fib_mod24[-2]) % 24)

    mod6 = 6 * MOD
    mod1 = 24 * mod6
    mod2 = 24 * 24 * mod6
    mod3 = 24 * 24 * 24 * mod6

    total = 0
    for s in range(24):
        k0 = s if s >= 2 else s + 24
        if k0 > k_max:
            continue
        n_terms = 1 + (k_max - k0) // 24
        sum0, sum1, sum2, sum3 = subseq_sums(k0, n_terms, fib_big, powers, mod_big)

        r = fib_mod24[s]

        num1 = (sum1 % mod1 - r * (n_terms % mod1)) % mod1
        sum_t = (num1 // 24) % mod6

        sum1_m2 = sum1 % mod2
        num2 = (sum2 % mod2 - 2 * r * sum1_m2 + (r * r) * (n_terms % mod2)) % mod2
        sum_t2 = (num2 // (24 * 24)) % mod6

        sum1_m3 = sum1 % mod3
        sum2_m3 = sum2 % mod3
        num3 = (
            sum3 % mod3
            - 3 * r * sum2_m3
            + 3 * r * r * sum1_m3
            - (r**3) * (n_terms % mod3)
        ) % mod3
        sum_t3 = (num3 // (24 * 24 * 24)) % mod6

        diff2 = (sum_t2 - sum_t) % (2 * MOD)
        sum_c2 = (diff2 // 2) % MOD

        diff3 = (sum_t3 - 3 * sum_t2 + 2 * sum_t) % (6 * MOD)
        sum_c3 = (diff3 // 6) % MOD

        d0, d1, d2, d3 = coeffs[r]
        total = (
            total
            + (d0 % MOD) * (n_terms % MOD)
            + (d1 % MOD) * (sum_t % MOD)
            + (d2 % MOD) * sum_c2
            + (d3 % MOD) * sum_c3
        ) % MOD

    return total


def main() -> None:
    sols = precompute_solutions()
    assert compute_S(10, sols) == 1972
    assert compute_S(10000, sols) == 2024258331114

    k_max = 1234567890123
    ans = sum_S_fib(k_max, sols)
    print(f"{ans:09d}")


if __name__ == "__main__":
    main()
