from __future__ import annotations

from math import gcd
from typing import List, Tuple


def find_curious_fractions() -> List[Tuple[int, int]]:
    """
    Find all non-trivial 2-digit digit-cancelling fractions n/d < 1.
    Non-trivial: exclude cases where both numerator and denominator end with 0.
    Also ignore cancelling digit '0' (as in the problem statement's "trivial" examples).
    """
    res: List[Tuple[int, int]] = []
    for n in range(10, 100):
        for d in range(n + 1, 100):
            if n % 10 == 0 and d % 10 == 0:
                continue  # trivial example like 30/50

            ns, ds = str(n), str(d)

            # try cancelling any common non-zero digit
            for c in "123456789":
                if c in ns and c in ds:
                    n_rem = ns.replace(c, "", 1)
                    d_rem = ds.replace(c, "", 1)
                    if len(n_rem) != 1 or len(d_rem) != 1:
                        continue
                    if d_rem == "0":
                        continue
                    n2, d2 = int(n_rem), int(d_rem)

                    # compare fractions exactly: n/d == n2/d2
                    if n * d2 == d * n2:
                        res.append((n, d))
                        break  # avoid duplicates for the same (n,d)
    return res


def reduced_product_denominator(fracs: List[Tuple[int, int]]) -> int:
    num_prod = 1
    den_prod = 1
    for n, d in fracs:
        num_prod *= n
        den_prod *= d
    g = gcd(num_prod, den_prod)
    num_prod //= g
    den_prod //= g
    return den_prod


def main() -> None:
    fracs = find_curious_fractions()

    # Tests based on known examples from the problem statement / known result
    assert len(fracs) == 4
    assert set(fracs) == {(16, 64), (19, 95), (26, 65), (49, 98)}

    ans = reduced_product_denominator(fracs)

    print(ans)


if __name__ == "__main__":
    main()
