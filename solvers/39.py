from __future__ import annotations

from math import gcd
from typing import List


def max_solutions_perimeter(limit: int) -> int:
    """
    Counts right-triangle integer solutions (a,b,c) for each perimeter p<=limit
    using Euclid's formula for Pythagorean triples.
    Returns p that maximizes the number of solutions.
    """
    counts: List[int] = [0] * (limit + 1)

    m = 2
    # Smallest n is 1, so smallest perimeter for given m is 2*m*(m+1).
    while 2 * m * (m + 1) <= limit:
        for n in range(1, m):
            # Primitive triple conditions: coprime and opposite parity
            if ((m - n) & 1) == 0:
                continue
            if gcd(m, n) != 1:
                continue

            p0 = 2 * m * (m + n)  # perimeter of primitive triple
            if p0 > limit:
                continue

            # Count all multiples of this primitive triple within the limit
            for k in range(1, limit // p0 + 1):
                counts[k * p0] += 1

        m += 1

    best_p = 0
    best_count = -1
    for p in range(1, limit + 1):
        if counts[p] > best_count:
            best_count = counts[p]
            best_p = p
    return best_p


def main() -> None:
    limit = 1000
    answer = max_solutions_perimeter(limit)

    # Test from statement: p=120 has exactly 3 solutions.
    # Our counting counts distinct (a,b,c) solutions ignoring order of legs, matching the statement.
    # If the logic is correct, counts[120] should be 3; we validate via recomputation.
    # (We re-run to access the internal counts deterministically for the assert.)
    def count_for(limit_inner: int, p_target: int) -> int:
        counts = [0] * (limit_inner + 1)
        m = 2
        while 2 * m * (m + 1) <= limit_inner:
            for n in range(1, m):
                if ((m - n) & 1) == 0:
                    continue
                if gcd(m, n) != 1:
                    continue
                p0 = 2 * m * (m + n)
                if p0 > limit_inner:
                    continue
                for k in range(1, limit_inner // p0 + 1):
                    counts[k * p0] += 1
            m += 1
        return counts[p_target]

    assert count_for(1000, 120) == 3

    print(answer)


if __name__ == "__main__":
    main()
