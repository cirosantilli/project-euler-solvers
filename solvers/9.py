from __future__ import annotations

from typing import Tuple


def special_pythagorean_product(total: int) -> int:
    """
    Find abc for the unique Pythagorean triplet (a<b<c, a^2+b^2=c^2) with a+b+c=total.
    Uses Euclid's formula: a=k(m^2-n^2), b=k(2mn), c=k(m^2+n^2).
    Then total = 2*k*m*(m+n).
    """
    # m must satisfy 2*m*(m+1) <= total (since n>=1, k>=1)
    m = 2
    while 2 * m * (m + 1) <= total:
        for n in range(1, m):
            s = 2 * m * (m + n)
            if total % s != 0:
                continue
            k = total // s
            a = k * (m * m - n * n)
            b = k * (2 * m * n)
            c = k * (m * m + n * n)

            a, b, c = sorted((a, b, c))
            if a > 0 and a * a + b * b == c * c and a + b + c == total:
                return a * b * c
        m += 1

    raise ValueError(f"No Pythagorean triplet sums to {total}")


def _self_test() -> None:
    # Example in the statement: 3,4,5 is a Pythagorean triplet (sum=12, product=60)
    assert special_pythagorean_product(12) == 60


def main() -> None:
    _self_test()
    print(special_pythagorean_product(1000))


if __name__ == "__main__":
    main()
