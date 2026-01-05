from math import isqrt, sqrt
from fractions import Fraction


def ag(x):
    """A_G(x) = x(3x+1)/(1-x-x^2). Works with Fraction or float."""
    return x * (3 * x + 1) / (1 - x - x * x)


def x_for_n_float(n: int) -> float:
    """
    Solve A_G(x)=n for x (positive root) as a float.
    (n+3)x^2 + (n+1)x - n = 0
    """
    D = 5 * n * n + 14 * n + 1
    return (-(n + 1) + sqrt(D)) / (2 * (n + 3))


def nuggets(count: int):
    """
    Generate the first `count` golden nuggets n, using a Pell-type recurrence
    via the m-sequence:
        m = [7, 14, 50, 97]
        m_k = 7*m_{k-2} - m_{k-4}
    Then n = (sqrt(5m^2+44)-7)/5
    """
    m = [7, 14, 50, 97]
    while len(m) < count:
        m.append(7 * m[-2] - m[-4])

    ns = []
    for mm in m[:count]:
        X2 = 5 * mm * mm + 44
        X = isqrt(X2)
        if X * X != X2:
            raise RuntimeError("Internal error: expected a perfect square.")
        n = (X - 7) // 5
        ns.append(n)
    return ns


def solve(count: int = 30) -> int:
    return sum(nuggets(count))


# ---- Problem-statement sanity checks ----
# Table of x values for A_G(x)=1..5:
_stmt_table = [
    ((sqrt(5) - 1) / 4, 1),
    (2 / 5, 2),
    ((sqrt(22) - 2) / 6, 3),
    ((sqrt(137) - 5) / 14, 4),
    (1 / 2, 5),
]

for expected_x, n in _stmt_table:
    x = x_for_n_float(n)
    assert abs(x - expected_x) < 1e-12
    assert abs(ag(x) - n) < 1e-10

# Exact checks for the rational ones in the table:
assert ag(Fraction(2, 5)) == 2
assert ag(Fraction(1, 2)) == 5

# From the definition, these are the first two golden nuggets:
assert nuggets(2) == [2, 5]

# Problem statement: the 20th golden nugget is 211345365
assert nuggets(20)[19] == 211_345_365


if __name__ == "__main__":
    print(solve(30))
