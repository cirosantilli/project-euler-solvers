from __future__ import annotations

from math import isqrt

MOD = 100_000_000


def g(n: int) -> int:
    return (n * n * n + 5 * n + 6) // 6


def G(n: int) -> int:
    if n < 0:
        return 0
    n2 = n * n
    n3 = n2 * n
    n4 = n2 * n2
    return (n4 + 2 * n3 + 11 * n2 + 34 * n + 24) // 24


def H(n: int) -> int:
    if n < 0:
        return 0
    s1 = n * (n + 1) // 2
    s2 = n * (n + 1) * (2 * n + 1) // 6
    s3 = s1 * s1
    s4 = n * (n + 1) * (2 * n + 1) * (3 * n * n + 3 * n - 1) // 30
    return (s4 + 2 * s3 + 11 * s2 + 34 * s1 + 24 * (n + 1)) // 24


def sum_G(l: int, r: int) -> int:
    if l > r:
        return 0
    return H(r) - H(l - 1)


def compute(N: int) -> int:
    s = isqrt(N)
    total = 0

    # p = 0
    total += 2 * G(N) - 1

    if N >= 1:
        f1 = G(N + 1) + G(N - 2) - 1
        total += 2 * f1

    if N >= 2:
        fn = g(N) + g(N + 1)
        total += 2 * fn

    # Small |p|
    hi = min(s, N - 1)
    if hi >= 2:
        small_sum = 0
        for p in range(2, hi + 1):
            m = N // p
            small_sum += G(m + p) + G(m - p) - 1
        total += 2 * small_sum

    # Large |p| grouped by m = floor(N / p)
    large_sum = 0
    for m in range(1, s + 1):
        l = N // (m + 1) + 1
        r = N // m
        if r <= s:
            continue
        if l <= s:
            l = s + 1
        if l > r:
            continue
        if r == N and N >= l:
            if l <= N - 1:
                large_sum += sum_G(l + m, N - 1 + m) - sum_G(l - m - 1, N - 1 - m - 1)
        else:
            large_sum += sum_G(l + m, r + m) - sum_G(l - m - 1, r - m - 1)
    total += 2 * large_sum

    # Diagonal p = q
    diag = 2 * min(N // 2, isqrt(N)) + 1
    return (total + diag) // 2


def main() -> None:
    assert compute(5) == 344
    assert compute(100) == 26709528

    n = 10**12
    result = compute(n) % MOD
    print(result)


if __name__ == "__main__":
    main()
