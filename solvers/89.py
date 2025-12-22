from __future__ import annotations

import os
import sys
from typing import Dict, List, Tuple


ROMAN_VALUE: Dict[str, int] = {
    "I": 1,
    "V": 5,
    "X": 10,
    "L": 50,
    "C": 100,
    "D": 500,
    "M": 1000,
}

# Standard minimal Roman numeral construction (Project Euler 89 rules).
MINIMAL_TABLE: List[Tuple[int, str]] = [
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


def roman_to_int(s: str) -> int:
    """Parse a (valid) Roman numeral into an integer."""
    total = 0
    i = 0
    n = len(s)
    while i < n:
        v = ROMAN_VALUE[s[i]]
        if i + 1 < n:
            v2 = ROMAN_VALUE[s[i + 1]]
            if v < v2:
                total += v2 - v
                i += 2
                continue
        total += v
        i += 1
    return total


def int_to_min_roman(x: int) -> str:
    """Convert an integer to its minimal Roman numeral form."""
    if x <= 0:
        raise ValueError("Roman numerals here are defined only for positive integers.")
    res: List[str] = []
    for val, sym in MINIMAL_TABLE:
        if x == 0:
            break
        k, x = divmod(x, val)
        if k:
            res.append(sym * k)
    return "".join(res)


def load_lines() -> List[str]:
    with open("0089_roman.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]


def total_characters_saved(lines: List[str]) -> int:
    saved = 0
    for s in lines:
        val = roman_to_int(s)
        minimal = int_to_min_roman(val)
        saved += len(s) - len(minimal)
    return saved


def _self_tests() -> None:
    assert roman_to_int("XVI") == 16
    assert int_to_min_roman(16) == "XVI"

    assert roman_to_int("VIIII") == 9
    assert int_to_min_roman(9) == "IX"
    assert len("VIIII") - len("IX") == 3

    assert roman_to_int("IIII") == 4
    assert int_to_min_roman(4) == "IV"
    assert len("IIII") - len("IV") == 2

    assert roman_to_int("MCMXC") == 1990
    assert int_to_min_roman(1990) == "MCMXC"

    assert roman_to_int("MMMMCMXCIX") == 4999
    assert int_to_min_roman(4999) == "MMMMCMXCIX"


def main() -> None:
    _self_tests()
    lines = load_lines()
    ans = total_characters_saved(lines)
    print(ans)


if __name__ == "__main__":
    main()
