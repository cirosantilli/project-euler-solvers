from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
import math


def triangle_numbers(n: int) -> List[int]:
    return [k * (k + 1) // 2 for k in range(1, n + 1)]


def is_triangle(x: int) -> bool:
    # Solve n(n+1)/2 = x  =>  n^2 + n - 2x = 0
    # n = (-1 + sqrt(1 + 8x)) / 2 must be an integer >= 1
    if x <= 0:
        return False
    d = 1 + 8 * x
    s = math.isqrt(d)
    if s * s != d:
        return False
    return (s - 1) % 2 == 0


def word_value(word: str) -> int:
    # Words are uppercase A-Z in the provided file
    return sum((ord(c) - ord("A") + 1) for c in word if "A" <= c <= "Z")


def parse_words_file(text: str) -> List[str]:
    # File format: "WORD1","WORD2",...
    # Split by commas and strip surrounding quotes.
    parts = text.strip().split(",")
    return [p.strip().strip('"') for p in parts if p.strip()]


def find_words_file() -> Path:
    return Path("0042_words.txt")


def count_triangle_words(words: Iterable[str]) -> int:
    return sum(1 for w in words if is_triangle(word_value(w)))


def _asserts() -> None:
    # From statement: first ten triangle numbers
    assert triangle_numbers(10) == [1, 3, 6, 10, 15, 21, 28, 36, 45, 55]
    # From statement: SKY = 55 which is triangular (t_10)
    assert word_value("SKY") == 55
    assert is_triangle(55)


def main() -> None:
    _asserts()
    path = find_words_file()
    text = path.read_text(encoding="utf-8")
    words = parse_words_file(text)
    print(count_triangle_words(words))


if __name__ == "__main__":
    main()
