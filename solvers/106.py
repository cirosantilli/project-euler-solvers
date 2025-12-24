from __future__ import annotations

from math import comb
from typing import Final


def catalan(k: int) -> int:
    # Catalan(k) = (1/(k+1)) * C(2k, k)
    return comb(2 * k, k) // (k + 1)


def pairs_needing_equality_test(n: int) -> int:
    """
    Count disjoint non-empty subset pairs (B, C) that must be tested for S(B) != S(C),
    assuming the set is strictly increasing and already satisfies:
      |B| > |C|  =>  S(B) > S(C)

    Only equal-size subset pairs can possibly violate rule (1), and among those,
    pairs where one subset is elementwise larger than the other (after sorting)
    are guaranteed to have different sums and don't need testing.
    """
    total = 0
    for k in range(2, n // 2 + 1):
        # Choose which 2k elements are involved at all
        ways_choose_elements = comb(n, 2 * k)

        # For those 2k elements, number of unordered partitions into two k-sets:
        unordered_partitions = comb(2 * k, k) // 2

        # Partitions that are elementwise comparable (hence sums are forced unequal)
        # correspond to Dyck words => Catalan(k)
        comparable = catalan(k)

        total += ways_choose_elements * (unordered_partitions - comparable)
    return total


def main() -> None:
    # Given examples from the statement:
    assert pairs_needing_equality_test(4) == 1
    assert pairs_needing_equality_test(7) == 70

    n: Final[int] = 12
    result = pairs_needing_equality_test(n)
    print(result)


if __name__ == "__main__":
    main()
