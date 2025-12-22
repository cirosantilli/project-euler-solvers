from __future__ import annotations

from math import gcd
from typing import Final


def count_between_one_third_and_one_half(limit: int) -> int:
    """
    Count reduced proper fractions n/d with:
      1/3 < n/d < 1/2, 1 <= d <= limit, gcd(n,d)=1
    """
    total = 0
    g = gcd  # local alias for speed

    for d in range(2, limit + 1):
        # strict: n/d > 1/3  => n > d/3 => n >= floor(d/3) + 1
        n_start = d // 3 + 1
        # strict: n/d < 1/2  => n < d/2 => n <= floor((d-1)/2)
        n_end = (d - 1) // 2

        if n_start > n_end:
            continue

        for n in range(n_start, n_end + 1):
            if g(n, d) == 1:
                total += 1

    return total


def main() -> None:
    # Example from the statement: d <= 8 has exactly 3 fractions in (1/3, 1/2)
    assert count_between_one_third_and_one_half(8) == 3

    LIMIT: Final[int] = 12_000
    ans = count_between_one_third_and_one_half(LIMIT)
    print(ans)


if __name__ == "__main__":
    main()
