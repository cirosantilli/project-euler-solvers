#!/usr/bin/env python3
"""
Project Euler 568: Reciprocal Games II

We use the identity:
    D(n) = J_B(n) - J_A(n) = H_n / 2^n
where H_n = 1 + 1/2 + ... + 1/n is the nth harmonic number.

The required output is the 7 most significant digits of D(123456789) after
removing leading zeros, i.e. the first 7 digits of the scientific-notation
mantissa of D(n).
"""

from __future__ import annotations

import math
from fractions import Fraction
from decimal import Decimal, getcontext, ROUND_HALF_UP, ROUND_FLOOR


# Euler–Mascheroni constant to high precision (more than enough for this problem)
_EULER_GAMMA = Decimal(
    "0.5772156649015328606065120900824024310421593359399235988057672348848677"
)


def _ja_exact(n: int) -> Fraction:
    """Exact J_A(n) as a rational number (only feasible for small n)."""
    two_n = 1 << n
    s = Fraction(0, 1)
    for k in range(1, n + 1):
        s += Fraction(math.comb(n, k), k * two_n)
    return s


def _jb_exact(n: int) -> Fraction:
    """Exact J_B(n) as a rational number (only feasible for small n)."""
    s = Fraction(0, 1)
    for k in range(1, n + 1):
        s += Fraction(1, k * math.comb(n, k))
    return s


def _harmonic_exact(n: int) -> Fraction:
    """Exact harmonic number H_n as Fraction (small n only)."""
    s = Fraction(0, 1)
    for k in range(1, n + 1):
        s += Fraction(1, k)
    return s


def _decimal_rounded(fr: Fraction, places: int) -> str:
    """Round an exact Fraction to a fixed number of decimal places (string)."""
    # extra guard precision for exact division before quantize
    ctx = getcontext()
    old_prec = ctx.prec
    ctx.prec = max(50, places + 30)
    try:
        d = Decimal(fr.numerator) / Decimal(fr.denominator)
        q = Decimal(1).scaleb(-places)  # 10**(-places)
        return str(d.quantize(q, rounding=ROUND_HALF_UP))
    finally:
        ctx.prec = old_prec


def _leading_sig_digits_fraction(x: Fraction, sig: int) -> int:
    """
    First `sig` significant digits of a positive Fraction in base 10
    after stripping leading zeros (exact arithmetic).

    This is only used for small test cases.
    """
    assert x > 0
    p, q = x.numerator, x.denominator
    # Find smallest t such that p*10^t >= q (so x*10^t >= 1).
    t = 0
    pow10 = 1
    while p * pow10 < q:
        pow10 *= 10
        t += 1
    # mantissa = x * 10^t in [1, 10). digits = floor(mantissa * 10^(sig-1))
    return (p * pow10 * (10 ** (sig - 1))) // q


def _harmonic_asymptotic(n: int) -> Decimal:
    """
    High-accuracy harmonic number approximation via Euler–Maclaurin:
        H_n = ln(n) + γ + 1/(2n) - 1/(12n^2) + 1/(120n^4)
              - 1/(252n^6) + 1/(240n^8) - 1/(132n^10) + ...
    For n = 123456789, the shown terms are far beyond what we need.
    """
    dn = Decimal(n)
    inv = Decimal(1) / dn
    inv2 = inv * inv
    inv4 = inv2 * inv2
    inv6 = inv4 * inv2
    inv8 = inv4 * inv4
    inv10 = inv8 * inv2

    H = dn.ln() + _EULER_GAMMA
    H += inv / 2
    H -= inv2 / 12
    H += inv4 / 120
    H -= inv6 / 252
    H += inv8 / 240
    H -= inv10 / 132
    return +H  # apply context rounding


def solve(n: int = 123456789, sig: int = 7) -> int:
    """
    Return the first `sig` significant digits of D(n) = H_n / 2^n.
    """
    # Need high precision because we multiply log10(2) by n (~1e8)
    getcontext().prec = 120

    H = _harmonic_asymptotic(n)

    log10_2 = Decimal(2).log10()
    L = H.log10() - Decimal(n) * log10_2  # log10(D(n))

    e = int(L.to_integral_value(rounding=ROUND_FLOOR))
    frac = L - Decimal(e)  # in [0, 1)

    ln10 = Decimal(10).ln()
    mantissa = (frac * ln10).exp()  # 10**frac, in [1, 10)

    scale = Decimal(10) ** (sig - 1)
    # Add a tiny epsilon to guard against rare downward rounding artifacts.
    eps = Decimal(1).scaleb(-(sig + 20))
    digits = int(((mantissa + eps) * scale).to_integral_value(rounding=ROUND_FLOOR))

    # If rounding pushed us over the boundary (extremely unlikely), renormalize.
    if digits >= 10**sig:
        digits //= 10
    return digits


def _run_asserts() -> None:
    # Test values from the problem statement (n = 6)
    ja6 = _ja_exact(6)
    jb6 = _jb_exact(6)
    d6 = jb6 - ja6

    assert _decimal_rounded(ja6, 8) == "0.39505208"
    assert _decimal_rounded(jb6, 8) == "0.43333333"
    assert d6 == Fraction(49, 1280)  # exactly 0.03828125
    assert _leading_sig_digits_fraction(d6, 7) == 3828125

    # Core identity check on a few small n: D(n) * 2^n = H_n
    for n in range(1, 15):
        d = _jb_exact(n) - _ja_exact(n)
        assert d * (1 << n) == _harmonic_exact(n)


def main() -> None:
    _run_asserts()
    print(solve())


if __name__ == "__main__":
    main()
