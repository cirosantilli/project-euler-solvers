from __future__ import annotations

from typing import List


def partitions_upto(n: int) -> List[int]:
    """
    Exact partition numbers p(0..n) using Euler's pentagonal recurrence.
    Suitable for small n (uses Python big integers).
    """
    p: List[int] = [0] * (n + 1)
    p[0] = 1
    for i in range(1, n + 1):
        total = 0
        k = 1
        while True:
            g1 = k * (3 * k - 1) // 2
            if g1 > i:
                break
            sign = 1 if (k % 2 == 1) else -1
            total += sign * p[i - g1]

            g2 = k * (3 * k + 1) // 2
            if g2 <= i:
                total += sign * p[i - g2]
            k += 1
        p[i] = total
    return p


def least_n_partition_divisible(mod: int) -> int:
    """
    Returns the least n such that p(n) % mod == 0.
    Computes p(n) modulo mod via pentagonal recurrence.
    """
    p: List[int] = [1]  # p[0] = 1 (mod mod)
    n = 1
    while True:
        total = 0
        k = 1
        while True:
            g1 = k * (3 * k - 1) // 2
            if g1 > n:
                break
            sign = 1 if (k % 2 == 1) else -1
            total += sign * p[n - g1]

            g2 = k * (3 * k + 1) // 2
            if g2 <= n:
                total += sign * p[n - g2]
            k += 1

        total %= mod
        p.append(total)
        if total == 0:
            return n
        n += 1


def main() -> None:
    # Small sanity checks from known partition values.
    small = partitions_upto(10)
    assert small[0] == 1
    assert small[5] == 7
    assert small[10] == 42

    ans = least_n_partition_divisible(1_000_000)
    print(ans)


if __name__ == "__main__":
    main()
