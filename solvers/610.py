#!/usr/bin/env python3
"""Project Euler 610: Roman Numerals II

We repeatedly sample symbols from {I, V, X, L, C, D, M, #} with
P(#)=0.02 and each letter probability 0.14. We build a string left to
right, but only *accept* a letter if the resulting string is a valid
Roman numeral in *minimal* form (Project Euler's rules). Invalid letters
are skipped. We stop when # first appears (not written).

This program computes the expected value of the final numeral and prints
it rounded to 8 decimal places.

No external libraries are used.
"""

from __future__ import annotations

from fractions import Fraction
from typing import Dict, List, Tuple


# --- Roman numeral helpers -------------------------------------------------

_ROMAN_MINIMAL_TABLE: List[Tuple[int, str]] = [
    (1000, "M"),
    (900, "CM"),
    (500, "D"),
    (400, "CD"),
    (100, "C"),
    (90, "XC"),
    (50, "L"),
    (40, "XL"),
    (10, "X"),
    (9, "IX"),
    (5, "V"),
    (4, "IV"),
    (1, "I"),
]


def to_min_roman(n: int) -> str:
    """Convert n>=0 to its minimal Roman numeral representation.

    Project Euler's rules allow an unlimited number of 'M'.
    For n==0 we return the empty string.
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0:
        return ""
    out: List[str] = []
    for value, token in _ROMAN_MINIMAL_TABLE:
        while n >= value:
            out.append(token)
            n -= value
    return "".join(out)


def _parse_group(
    s: str, idx: int, one: str, five: str, ten: str, base: int
) -> Tuple[int, int]:
    """Parse one Roman 'digit' group (e.g. ones, tens, hundreds).

    This matches the Project Euler 'valid' rules (not necessarily minimal):
    - allows 0..9 repetitions of the 'one' symbol when no 'five' is used
    - allows 'five' followed by 0..4 repetitions of the 'one' symbol
    - allows subtractive pairs one+five (4) and one+ten (9)

    Returns (group_value, new_idx)."""

    if idx >= len(s):
        return 0, idx

    # 9 * base
    if s.startswith(one + ten, idx):
        return 9 * base, idx + 2
    # 4 * base
    if s.startswith(one + five, idx):
        return 4 * base, idx + 2

    val = 0
    if s.startswith(five, idx):
        val += 5 * base
        idx += 1
        # after a 'five' we may add up to 4 ones (otherwise we'd reach the next 'ten')
        count = 0
        while idx < len(s) and s[idx] == one:
            count += 1
            if count > 4:
                raise ValueError("invalid: too many repetitions after five")
            idx += 1
        val += count * base
        return val, idx

    # no 'five': up to 9 ones
    count = 0
    while idx < len(s) and s[idx] == one:
        count += 1
        if count > 9:
            raise ValueError("invalid: too many repetitions")
        idx += 1
    val += count * base
    return val, idx


def parse_valid_roman(s: str) -> int:
    """Parse a *valid* Roman numeral under Project Euler's rules.

    This accepts many non-minimal forms (e.g. XXXXIX) but rejects invalid
    subtractive pairs (e.g. IL).

    The empty string is treated as 0.
    """
    if not s:
        return 0

    # thousands: M*
    idx = 0
    while idx < len(s) and s[idx] == "M":
        idx += 1
    thousands = 1000 * idx

    # hundreds, tens, ones
    hundreds, idx = _parse_group(s, idx, one="C", five="D", ten="M", base=100)
    tens, idx = _parse_group(s, idx, one="X", five="L", ten="C", base=10)
    ones, idx = _parse_group(s, idx, one="I", five="V", ten="X", base=1)

    if idx != len(s):
        raise ValueError("invalid: trailing characters")

    return thousands + hundreds + tens + ones


def is_valid_roman(s: str) -> bool:
    try:
        parse_valid_roman(s)
        return True
    except ValueError:
        return False


def is_minimal_roman(s: str) -> bool:
    """Check if s is valid and minimal under Project Euler rules."""
    try:
        v = parse_valid_roman(s)
    except ValueError:
        return False
    return to_min_roman(v) == s


# --- Expected value computation --------------------------------------------

LETTERS = "IVXLCDM"  # seven letters (each with probability 0.14)
P_STOP = Fraction(1, 50)  # 0.02
P_LETTER = Fraction(7, 50)  # 0.14


def _round_fraction(fr: Fraction, digits: int) -> str:
    """Round a positive Fraction to `digits` decimal places (half-up)."""
    if fr < 0:
        raise ValueError("expected non-negative fraction")
    scale = 10**digits
    scaled_num = fr.numerator * scale
    q, r = divmod(scaled_num, fr.denominator)
    # half-up rounding
    if 2 * r >= fr.denominator:
        q += 1
    int_part, frac_part = divmod(q, scale)
    return f"{int_part}.{frac_part:0{digits}d}"


def expected_value() -> Fraction:
    """Return the exact expected value as a Fraction."""

    # Precompute all minimal Roman numerals for 1..999.
    roman_to_val: Dict[str, int] = {}
    romans: List[str] = []
    for n in range(1, 1000):
        r = to_min_roman(n)
        roman_to_val[r] = n
        romans.append(r)

    roman_set = set(romans)

    # Sort by length descending. From any numeral, a valid append always increases length,
    # so this yields a dependency order.
    romans.sort(key=len, reverse=True)

    # E[r] = expected final numeric value (0..999) starting from remainder numeral r.
    E: Dict[str, Fraction] = {}

    for r in romans:
        v = roman_to_val[r]

        extensions = [r + ch for ch in LETTERS if (r + ch) in roman_set]
        denom = P_STOP + P_LETTER * len(extensions)
        numer = P_STOP * v
        for ext in extensions:
            numer += P_LETTER * E[ext]

        E[r] = numer / denom

    # Infinite leading-M segment.
    # Let b = E_total when we currently have written nothing but M's (possibly none).
    # b satisfies:
    #   b = p*M_step + p*sum(E[first_letter]) + p*b
    # where M_step contributes 1000 when we append an M.
    sum_initial = E["I"] + E["V"] + E["X"] + E["L"] + E["C"] + E["D"]
    b = (P_LETTER * (1000 + sum_initial)) / (1 - P_LETTER)
    return b


def solve() -> str:
    ans = expected_value()
    return _round_fraction(ans, 8)


def _run_tests() -> None:
    # Test values/examples mentioned in the problem statement.
    assert to_min_roman(49) == "XLIX"
    assert is_valid_roman("XLIX") and is_minimal_roman("XLIX")
    assert not is_valid_roman("IL")
    assert parse_valid_roman("XXXXIX") == 49
    assert is_valid_roman("XXXXIX") and not is_minimal_roman("XXXXIX")


if __name__ == "__main__":
    _run_tests()
    print(solve())
