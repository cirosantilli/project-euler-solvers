#!/usr/bin/env python3
"""
Project Euler 444 - The Roundtable Lottery

Key results:
- Optimal play leaves (in expectation) E(p) = H_p, the p-th harmonic number.
- The k-fold summatory function satisfies:
    S_k(N) = C(N+k, k) * (H_{N+k} - H_k)

We compute S_20(10^14) and print it in scientific notation rounded to 10 significant digits.
No external libraries are used (only Python standard library).
"""

from __future__ import annotations

import sys
import math
from decimal import Decimal, getcontext, ROUND_HALF_UP
from typing import Final


# High-precision Euler–Mascheroni constant (more than enough for 10 significant digits output)
EULER_GAMMA: Final[Decimal] = Decimal(
    "0.5772156649015328606065120900824024310421593359399235988057672348848677"
)


def harmonic_small(n: int) -> Decimal:
    """Exact (within Decimal arithmetic) harmonic number by direct summation; good for small n."""
    s = Decimal(0)
    for i in range(1, n + 1):
        s += Decimal(1) / Decimal(i)
    return +s


def harmonic_large(n: int) -> Decimal:
    """
    Harmonic number via Euler–Maclaurin expansion:
      H_n = ln(n) + gamma + 1/(2n) - 1/(12n^2) + 1/(120n^4) - 1/(252n^6) + 1/(240n^8) - 5/(660n^10) + ...
    For n ~ 1e14 this is extremely accurate (far beyond what we need).
    """
    nd = Decimal(n)
    inv = Decimal(1) / nd
    inv2 = inv * inv

    h = nd.ln() + EULER_GAMMA
    h += inv / 2
    h -= inv2 / Decimal(12)

    inv4 = inv2 * inv2
    h += inv4 / Decimal(120)

    inv6 = inv4 * inv2
    h -= inv6 / Decimal(252)

    inv8 = inv4 * inv4
    h += inv8 / Decimal(240)

    inv10 = inv8 * inv2
    h -= (inv10 * Decimal(5)) / Decimal(660)

    return +h


def harmonic(n: int) -> Decimal:
    # Only a few small harmonic numbers are needed exactly (k<=20 and test n<=111).
    # Large n uses Euler–Maclaurin.
    return harmonic_small(n) if n <= 200_000 else harmonic_large(n)


def S_k(N: int, k: int) -> Decimal:
    """
    Compute S_k(N) for Euler 444:
      S_k(N) = C(N+k, k) * (H_{N+k} - H_k)
    """
    if N < 0 or k < 0:
        raise ValueError("N and k must be non-negative")
    coeff = Decimal(math.comb(N + k, k))
    return coeff * (harmonic(N + k) - harmonic(k))


def round_sig(x: Decimal, sig: int) -> Decimal:
    """Round to a given number of significant digits (half-up)."""
    if x.is_zero():
        return x
    exp = abs(x).adjusted()
    quant = Decimal(1).scaleb(exp - sig + 1)
    return x.quantize(quant, rounding=ROUND_HALF_UP)


def format_sci(x: Decimal, sig: int = 10) -> str:
    """
    Format Decimal x into scientific notation with exactly `sig` significant digits,
    using a lowercase 'e', e.g. 5.983679014e5 for sig=10.
    """
    if x.is_zero():
        return "0e0"

    sign = "-" if x < 0 else ""
    x = abs(x)

    exp = x.adjusted()
    mant = x.scaleb(-exp)  # in [1, 10)
    quant = Decimal(1).scaleb(-(sig - 1))
    mant = mant.quantize(quant, rounding=ROUND_HALF_UP)

    if mant == Decimal(10):
        mant = Decimal(1).quantize(quant, rounding=ROUND_HALF_UP)
        exp += 1

    mant_str = f"{mant:f}"
    if "." not in mant_str:
        mant_str += "." + "0" * (sig - 1)
    else:
        frac_len = len(mant_str.split(".")[1])
        if frac_len < sig - 1:
            mant_str += "0" * (sig - 1 - frac_len)

    return f"{sign}{mant_str}e{exp}"


def _run_asserts() -> None:
    # Problem statement examples:
    # E(111) = 5.2912 (rounded to 5 significant digits)
    assert round_sig(harmonic(111), 5) == Decimal("5.2912")

    # S_3(100) = 5.983679014e5 (scientific notation, 10 significant digits)
    assert format_sci(S_k(100, 3), 10) == "5.983679014e5"


def main() -> None:
    # Enough precision for reliable 10-significant-digit rounding even after huge binomial scaling.
    getcontext().prec = 80

    _run_asserts()

    # Default is the Project Euler target.
    N = 10**14
    k = 20

    # Optional CLI: `python main.py [N] [k]`
    if len(sys.argv) >= 2:
        N = int(sys.argv[1])
    if len(sys.argv) >= 3:
        k = int(sys.argv[2])

    ans = S_k(N, k)
    print(format_sci(ans, 10))


if __name__ == "__main__":
    main()
