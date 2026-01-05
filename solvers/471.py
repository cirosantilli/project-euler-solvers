#!/usr/bin/env python3
"""
Project Euler 471 - Triangle Inscribed in Ellipse

No third-party libraries are used.

The program prints G(10^11) in scientific notation rounded to 10 significant digits,
as requested by the problem.
"""
from __future__ import annotations

from decimal import Decimal, getcontext, ROUND_HALF_UP
from fractions import Fraction


# High precision is cheap here (only O(1) big computations), and helps robust rounding.
getcontext().prec = 80
getcontext().rounding = ROUND_HALF_UP

# Euler–Mascheroni constant to ~80 digits (more than enough for our needs).
GAMMA = Decimal(
    "0.57721566490153286060651209008240243104215933593992359880576723488486772677766467"
)

# For small n we compute H_n exactly by summation (used by the built-in asserts).
# For large n we use Euler–Maclaurin, which converges extremely fast.
HARMONIC_EXACT_LIMIT = 200_000


def r_fraction(a: int, b: int) -> Fraction:
    """Exact r(a,b) as a rational number: r = b*(a-2b)/(a-b)."""
    return Fraction(b * (a - 2 * b), a - b)


def brute_G(n: int) -> Fraction:
    """Exact G(n) by direct summation (only feasible for small n; used for asserts)."""
    total = Fraction(0, 1)
    for a in range(3, n + 1):
        for b in range(1, (a - 1) // 2 + 1):
            total += r_fraction(a, b)
    return total


def harmonic_decimal(n: int) -> Decimal:
    """H_n as Decimal: exact for small n; Euler–Maclaurin for large n."""
    if n <= 0:
        return Decimal(0)

    if n <= HARMONIC_EXACT_LIMIT:
        s = Decimal(0)
        dn = Decimal
        for k in range(1, n + 1):
            s += dn(1) / dn(k)
        return s

    N = Decimal(n)
    inv = Decimal(1) / N
    inv2 = inv * inv
    inv4 = inv2 * inv2
    inv6 = inv4 * inv2
    inv8 = inv4 * inv4
    inv10 = inv8 * inv2

    # Euler–Maclaurin:
    # H_n = ln(n) + γ + 1/(2n) - 1/(12n^2) + 1/(120n^4) - 1/(252n^6) + 1/(240n^8) - 1/(132n^10) + ...
    return (
        N.ln()
        + GAMMA
        + inv / 2
        - inv2 / 12
        + inv4 / 120
        - inv6 / 252
        + inv8 / 240
        - inv10 / 132
    )


def _S0_S1_S2(m: int, Hm: Decimal) -> tuple[Decimal, Decimal, Decimal]:
    """
    Helper sums over harmonic numbers:
      S0(m) = sum_{k=1..m} H_k
      S1(m) = sum_{k=1..m} k H_k
      S2(m) = sum_{k=1..m} k^2 H_k
    expressed using only H_m and polynomials.
    """
    D = Decimal
    md = D(m)

    S0 = (md + 1) * Hm - md
    S1 = (D(m * (m + 1)) / 2) * Hm - D(m * (m - 1)) / 4
    S2 = (D(m * (m + 1) * (2 * m + 1)) / 6) * Hm - D(m * (4 * m * m - 3 * m - 1)) / 36
    return S0, S1, S2


def G(n: int) -> Decimal:
    """
    Fast O(1) evaluation of G(n) using closed forms and harmonic numbers.
    """
    if n < 3:
        return Decimal(0)

    # Polynomial part: sum_{a=3..n} m(a+m+1), where m=floor((a-1)/2)
    ne = n // 2
    no = (n - 1) // 2

    def T1(x: int) -> int:
        return x * (x + 1) // 2

    def T2(x: int) -> int:
        return x * (x + 1) * (2 * x + 1) // 6

    P = 3 * (T2(ne) - T1(ne)) + 3 * T2(no) + 2 * T1(no)

    D = Decimal

    # A = sum_{a=3..n} a^2 * H_{a-1}
    mA = n - 1
    HA = harmonic_decimal(mA)
    S0A, S1A, S2A = _S0_S1_S2(mA, HA)
    # shift: sum_{j=2..n-1} (j+1)^2 H_j = (S2+2S1+S0) - 4
    A = S2A + 2 * S1A + S0A - 4

    # B = sum_{a=3..n} a^2 * H_{floor(a/2)}
    # Be careful: a=2 is NOT included, so we subtract its would-be contribution (4*H1 = 4).
    if n % 2 == 1:
        m = no
        Hm = harmonic_decimal(m)
        S0, S1, S2 = _S0_S1_S2(m, Hm)
        B = 8 * S2 + 4 * S1 + S0 - 4
    else:
        m = ne
        Hm = harmonic_decimal(m)
        m1 = m - 1
        Hm1 = harmonic_decimal(m1)
        S0, S1, S2 = _S0_S1_S2(m1, Hm1)
        B = 8 * S2 + 4 * S1 + S0 - 4 + D(4 * m * m) * Hm

    return D(P) - A + B


def format_fixed_sig(x: Decimal, sig: int = 10) -> str:
    """
    Fixed-point formatting rounded to `sig` significant digits (keeps trailing zeros).
    Used for the problem's given values like 19223.60980.
    """
    if x == 0:
        return "0"

    sign = "-" if x < 0 else ""
    x = abs(x)

    int_part = int(x)
    int_digits = len(str(int_part)) if int_part != 0 else 0
    decimals = max(sig - int_digits, 0)

    q = Decimal(1).scaleb(-decimals)  # 10**(-decimals)
    y = x.quantize(q)
    return sign + f"{y:.{decimals}f}"


def format_sci_10(x: Decimal) -> str:
    """
    Scientific notation with 10 significant digits, like: 2.059722222e1
    """
    if x == 0:
        return "0.000000000e0"

    sign = "-" if x < 0 else ""
    x = abs(x)

    exp = x.adjusted()  # floor(log10(x))
    mant = x.scaleb(-exp)  # in [1,10)

    mant = mant.quantize(
        Decimal("1.000000000")
    )  # 9 digits after the dot => 10 significant digits total
    if mant >= 10:
        mant = (mant / 10).quantize(Decimal("1.000000000"))
        exp += 1

    return f"{sign}{mant}e{exp}"


def _run_asserts() -> None:
    # r(a,b) examples
    assert r_fraction(3, 1) == Fraction(1, 2)
    assert r_fraction(6, 2) == Fraction(1, 1)
    assert r_fraction(12, 3) == Fraction(2, 1)

    # G(n) examples (rounded to 10 significant digits in the statement)
    g10 = brute_G(10)
    g10d = Decimal(g10.numerator) / Decimal(g10.denominator)
    assert format_fixed_sig(g10d, 10) == "20.59722222"
    assert format_sci_10(g10d) == "2.059722222e1"

    g100 = brute_G(100)
    g100d = Decimal(g100.numerator) / Decimal(g100.denominator)
    assert format_fixed_sig(g100d, 10) == "19223.60980"


def main() -> None:
    _run_asserts()
    n = 10**11
    ans = G(n)
    print(format_sci_10(ans))


if __name__ == "__main__":
    main()
