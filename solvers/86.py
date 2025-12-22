from __future__ import annotations

from math import isqrt
from typing import Tuple


def count_solutions_up_to(M: int) -> int:
    """
    Count distinct cuboids (a,b,c) with 1<=a<=b<=c<=M such that the shortest
    surface path between opposite corners has integer length.

    For a<=b<=c, the shortest unfolding distance is sqrt((a+b)^2 + c^2).
    """
    total = 0
    for c in range(1, M + 1):
        c2 = c * c
        for s in range(2, 2 * c + 1):  # s = a+b
            d = s * s + c2
            t = isqrt(d)
            if t * t == d:
                # count (a,b) with a<=b, a+b=s, 1<=a<=b<=c
                lo = max(1, s - c)
                hi = s // 2
                if hi >= lo:
                    total += hi - lo + 1
    return total


def least_M_exceeding(target: int) -> int:
    """
    Incrementally extend max side length c = M, maintaining total count.
    """
    total = 0
    c = 0
    while total <= target:
        c += 1
        c2 = c * c
        for s in range(2, 2 * c + 1):
            d = s * s + c2
            t = isqrt(d)
            if t * t == d:
                lo = max(1, s - c)
                hi = s // 2
                if hi >= lo:
                    total += hi - lo + 1
    return c


def main() -> None:
    # Given checks from the problem statement
    assert count_solutions_up_to(99) == 1975
    assert count_solutions_up_to(100) == 2060

    ans = least_M_exceeding(1_000_000)
    print(ans)


if __name__ == "__main__":
    main()
