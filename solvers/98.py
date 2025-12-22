from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple


def pattern_signature(s: str) -> Tuple[int, ...]:
    """Encode equality structure, e.g. NOON -> (0,1,1,0), CARE -> (0,1,2,3)."""
    mp: Dict[str, int] = {}
    out: List[int] = []
    nxt = 0
    for ch in s:
        if ch not in mp:
            mp[ch] = nxt
            nxt += 1
        out.append(mp[ch])
    return tuple(out)


def read_words() -> List[str]:
    candidates = [
        Path("0098_words.txt"),
        Path("words.txt"),
        Path("resources/documents/0098_words.txt"),
    ]
    for p in candidates:
        if p.exists():
            content = p.read_text(encoding="utf-8").strip()
            # File is comma-separated with quoted words: "CARE","RACE",...
            return [w.strip().strip('"') for w in content.split(",") if w.strip()]
    raise FileNotFoundError(
        "Could not find the words file. Tried: " + ", ".join(str(p) for p in candidates)
    )


@dataclass
class SquaresByLength:
    by_pattern: Dict[Tuple[int, ...], List[str]]
    as_set: Set[str]


def squares_with_length(L: int) -> SquaresByLength:
    lo = 10 ** (L - 1)
    hi = 10**L - 1
    n0 = isqrt(lo - 1) + 1
    n1 = isqrt(hi)

    by_pat: Dict[Tuple[int, ...], List[str]] = {}
    st: Set[str] = set()
    for n in range(n0, n1 + 1):
        sq = n * n
        s = str(sq)
        st.add(s)
        pat = pattern_signature(s)
        by_pat.setdefault(pat, []).append(s)

    return SquaresByLength(by_pattern=by_pat, as_set=st)


def solve(words: List[str]) -> int:
    # Group by anagram class
    groups: Dict[str, List[str]] = {}
    for w in words:
        groups.setdefault("".join(sorted(w)), []).append(w)

    anagram_groups = [g for g in groups.values() if len(g) >= 2]
    if not anagram_groups:
        return 0

    lengths_needed = sorted({len(w) for g in anagram_groups for w in g})

    squares_cache: Dict[int, SquaresByLength] = {L: squares_with_length(L) for L in lengths_needed}

    # Cache word patterns
    word_pat: Dict[str, Tuple[int, ...]] = {}
    for g in anagram_groups:
        for w in g:
            word_pat[w] = pattern_signature(w)

    best = 0

    for g in anagram_groups:
        L = len(g[0])
        sqinfo = squares_cache[L]

        for i, w1 in enumerate(g):
            p1 = word_pat[w1]
            candidates = sqinfo.by_pattern.get(p1, [])
            if not candidates:
                continue

            others = [w for w in g if w != w1]
            for sq_str in candidates:
                # Build bijection w1 letters <-> digits
                char_to_digit: Dict[str, str] = {}
                digit_to_char: Dict[str, str] = {}
                ok = True
                for ch, d in zip(w1, sq_str):
                    if ch in char_to_digit and char_to_digit[ch] != d:
                        ok = False
                        break
                    if d in digit_to_char and digit_to_char[d] != ch:
                        ok = False
                        break
                    char_to_digit[ch] = d
                    digit_to_char[d] = ch
                if not ok:
                    continue

                sq1 = int(sq_str)
                for w2 in others:
                    # Leading zero not allowed
                    if char_to_digit[w2[0]] == "0":
                        continue
                    num2 = "".join(char_to_digit[ch] for ch in w2)
                    if num2 in sqinfo.as_set:
                        sq2 = int(num2)
                        if sq1 > best:
                            best = sq1
                        if sq2 > best:
                            best = sq2

    return best


def main() -> None:
    words = read_words()
    ans = solve(words)
    print(ans)


if __name__ == "__main__":
    main()
