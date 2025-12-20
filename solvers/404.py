from __future__ import annotations

from math import gcd
from typing import Final


def count_triplets(limit: int) -> int:
    # From the derivation, m is bounded by (2*limit)^(1/4).
    m_max: int = int((2 * limit) ** 0.25) + 1
    total = 0

    for m in range(1, m_max + 1):
        m2 = m * m

        # n in (-m/3, 0): ensures p > q and r > q.
        n_start = -(m // 3)
        if m % 3 == 0:
            n_start += 1
        for n in range(n_start, 0):
            if (m & 1) and (n & 1):
                continue
            if (m - 2 * n) % 5 == 0:
                continue
            if gcd(m, -n) != 1:
                continue

            n2 = n * n
            mn = m * n
            p = m2 - n2 - 4 * mn
            r = m2 - n2 + mn
            a0 = p * r
            if a0 <= limit:
                total += limit // a0

        # n in (m/2, m): ensures p > q and r > q.
        for n in range(m // 2 + 1, m):
            if (m & 1) and (n & 1):
                continue
            if (m - 2 * n) % 5 == 0:
                continue
            if gcd(m, n) != 1:
                continue

            n2 = n * n
            mn = m * n
            p = n2 + 4 * mn - m2  # abs(m2 - n2 - 4*mn)
            r = m2 - n2 + mn
            a0 = p * r
            if a0 <= limit:
                total += limit // a0

    return total


def main() -> None:
    assert count_triplets(10**3) == 7
    assert count_triplets(10**4) == 106
    assert count_triplets(10**6) == 11845

    limit: Final[int] = 10**17
    print(count_triplets(limit))


if __name__ == "__main__":
    main()
