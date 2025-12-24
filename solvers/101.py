from __future__ import annotations

from fractions import Fraction
from typing import List, Sequence, Tuple


def lagrange_interpolate_value(xs: Sequence[int], ys: Sequence[int], x: int) -> int:
    """
    Evaluate the unique degree <= len(xs)-1 polynomial passing through (xs[i], ys[i])
    at point x, using Lagrange interpolation. All values here are small; Fraction is fine.
    """
    k = len(xs)
    total = Fraction(0, 1)
    for i in range(k):
        term = Fraction(ys[i], 1)
        xi = xs[i]
        for j in range(k):
            if j == i:
                continue
            xj = xs[j]
            term *= Fraction(x - xj, xi - xj)
        total += term

    # For integer xs and integer ys originating from a polynomial, this is an integer.
    assert total.denominator == 1
    return total.numerator


def sum_fits_for_sequence(values_starting_at_1: Sequence[int], max_k: int) -> int:
    """
    Given u_1, u_2, ..., compute sum of FITs for k=1..max_k, where OP(k,n)
    is the best (degree k-1) polynomial fitting first k terms.
    """
    xs_all = list(range(1, len(values_starting_at_1) + 1))
    s = 0
    for k in range(1, max_k + 1):
        xs = xs_all[:k]
        ys = list(values_starting_at_1[:k])
        n_fit = k + 1
        op_val = lagrange_interpolate_value(xs, ys, n_fit)
        true_val = values_starting_at_1[n_fit - 1]
        if op_val != true_val:
            s += op_val
    return s


def cubic_terms(count: int) -> List[int]:
    return [n**3 for n in range(1, count + 1)]


def tenth_degree_u(n: int) -> int:
    # u_n = sum_{i=0..10} (-1)^i * n^i
    total = 0
    sign = 1
    p = 1
    for _i in range(11):
        total += sign * p
        sign *= -1
        p *= n
    return total


def main() -> None:
    # Sanity check using the cubic example from the statement: FIT sum should be 74.
    cube_vals = cubic_terms(6)  # enough to cover k=1..4 and their FIT checks
    assert sum_fits_for_sequence(cube_vals, max_k=3) == 74

    # Now solve the stated problem (degree 10 polynomial).
    vals = [tenth_degree_u(n) for n in range(1, 12)]  # need up to u_11 for k=10 FIT
    result = sum_fits_for_sequence(vals, max_k=10)

    print(result)


if __name__ == "__main__":
    main()
