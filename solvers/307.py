"""Project Euler 307: Chip Defects

k defects are independently and uniformly assigned to n chips.
We want:
    p(k, n) = P(there exists a chip with at least 3 defects).

Compute the complement:
    q(k, n) = P(all chips have at most 2 defects)
Then p = 1 - q.

Counting for the complement (occupancy with max 2):
Let a be the number of chips with exactly 2 defects, b the number with exactly 1 defect.
Then 2a + b = k.

Choose which chips get 2 defects and which get 1 defect:
    C(n, a) * C(n-a, b)
Assign k *labelled* defects to these chips with the required multiplicities:
    k! / (2!)^a

So the probability contribution for a fixed a is
    T(a) = C(n, a) * C(n-a, k-2a) * k! / 2^a / n^k.

Direct evaluation overflows, so we compute terms by recurrence.
Starting from a=0:
    T(0) = nPk / n^k = \prod_{i=0}^{k-1} (1 - i/n)
and
    T(a+1) / T(a) = b(b-1) / (2 (a+1) (n-k+a+1)),  where b = k-2a.

Summing T(a) for a=0..floor(k/2) gives q(k,n).

The target instance is k=20000, n=1000000; using doubles is sufficient for 10 decimals.
"""

from __future__ import annotations

import math
from typing import List


def prob_any_chip_ge_3(k: int, n: int) -> float:
    """Return p(k,n) = P(exists chip with >=3 defects) for k defects, n chips."""
    if k < 0 or n <= 0:
        raise ValueError("k must be >= 0 and n must be > 0")
    if k < 3:
        return 0.0

    # T(0) = prod_{i=0}^{k-1} (1 - i/n)
    inv_n = 1.0 / n
    log_t0 = 0.0
    for i in range(k):
        log_t0 += math.log1p(-i * inv_n)
    t = math.exp(log_t0)

    terms: List[float] = [t]

    a = 0
    # Produce T(1), T(2), ... via the ratio.
    while True:
        b = k - 2 * a
        if b < 2:
            break
        ratio = (b * (b - 1)) / (2.0 * (a + 1) * (n - k + a + 1))
        t *= ratio
        terms.append(t)
        a += 1

    q = math.fsum(terms)  # robust summation
    return 1.0 - q


def _tests() -> None:
    # Given example from the problem statement:
    # p(3,7) ≈ 0.0204081633
    p37 = prob_any_chip_ge_3(3, 7)
    assert abs(p37 - (1.0 / 49.0)) < 1e-15
    assert format(p37, ".10f") == "0.0204081633"


def main() -> None:
    _tests()

    k = 20_000
    n = 1_000_000
    ans = prob_any_chip_ge_3(k, n)
    print(format(ans, ".10f"))


if __name__ == "__main__":
    main()
