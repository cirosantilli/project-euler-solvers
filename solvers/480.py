#!/usr/bin/env python3
"""
Project Euler 480 - The Last Question

We consider all words (length 1..15) that can be formed from the multiset of letters in:
"thereisasyetinsufficientdataforameaningfulanswer"
sorted in standard lexicographic order (dictionary order), and 1-indexed.

This program implements:
- P(w): lexicographic rank (position) of word w
- W(p): word at position p (lexicographic unranking)

No external libraries are used.
"""

from functools import lru_cache
from collections import Counter


PHRASE = "thereisasyetinsufficientdataforameaningfulanswer"
MAX_LEN = 15


# ---- Precompute base multiset and combinatorics ----

_counter = Counter(PHRASE)
LETTERS = tuple(sorted(_counter.keys()))
BASE_COUNTS = tuple(_counter[ch] for ch in LETTERS)
INDEX = {ch: i for i, ch in enumerate(LETTERS)}

# factorials and binomial coefficients up to MAX_LEN
FACT = [1] * (MAX_LEN + 1)
for i in range(1, MAX_LEN + 1):
    FACT[i] = FACT[i - 1] * i

# nCk table (small: up to 15)
COMB = [[0] * (MAX_LEN + 1) for _ in range(MAX_LEN + 1)]
for n in range(MAX_LEN + 1):
    for k in range(n + 1):
        COMB[n][k] = FACT[n] // (FACT[k] * FACT[n - k])


@lru_cache(maxsize=None)
def count_suffix(counts, k):
    """
    Count the number of distinct sequences (including empty) of length 0..k
    that can be formed from the remaining multiset 'counts'.

    Let dp[L] be the number of distinct sequences of length L.

    We build dp by processing letter-types one by one. When adding t copies of a
    new letter to an existing arrangement of length l, the number of distinct
    interleavings is C(l+t, t). Thus:
        new[l+t] += dp[l] * C(l+t, t)

    This works because dp[l] already accounts for indistinguishability among
    previously processed letters.
    """
    if k < 0:
        return 0
    dp = [0] * (k + 1)
    dp[0] = 1
    for c in counts:
        new = dp[:]  # t=0 case
        for l in range(k + 1):
            v = dp[l]
            if not v:
                continue
            mt = min(c, k - l)
            for t in range(1, mt + 1):
                new[l + t] += v * COMB[l + t][t]
        dp = new
    return sum(dp)  # lengths 0..k


def P(word: str) -> int:
    """Return the 1-indexed lexicographic position of 'word'."""
    counts = list(BASE_COUNTS)
    rank_less = 0
    prefix_len = 0

    for i, ch in enumerate(word):
        if ch not in INDEX:
            raise ValueError(f"Letter {ch!r} not in source phrase.")
        # count words that share the current prefix but use a smaller next letter
        for j, ltr in enumerate(LETTERS):
            if ltr >= ch:
                break
            if counts[j] == 0:
                continue
            counts[j] -= 1
            rank_less += count_suffix(tuple(counts), MAX_LEN - (prefix_len + 1))
            counts[j] += 1

        idx = INDEX[ch]
        if counts[idx] == 0:
            raise ValueError(f"Word {word!r} uses too many {ch!r} letters.")
        counts[idx] -= 1
        prefix_len += 1

        # any proper prefix is lexicographically before the full word
        if i < len(word) - 1:
            rank_less += 1

    return rank_less + 1


def W(p: int) -> str:
    """Return the word in 1-indexed position 'p'."""
    if p <= 0:
        raise ValueError("Position must be positive (1-indexed).")

    counts = list(BASE_COUNTS)
    prefix = ""

    while True:
        if prefix:
            # the word equal to the current prefix comes first
            if p == 1:
                return prefix
            p -= 1

        # extend by choosing the next letter
        for j, ltr in enumerate(LETTERS):
            if counts[j] == 0:
                continue
            counts[j] -= 1
            cnt = count_suffix(tuple(counts), MAX_LEN - (len(prefix) + 1))
            if p > cnt:
                p -= cnt
                counts[j] += 1
                continue
            prefix += ltr
            break
        else:
            raise ValueError("Position out of range.")

        if len(prefix) > MAX_LEN:
            raise ValueError("Exceeded maximum word length.")


def main() -> None:
    # ---- Problem statement examples (tests) ----
    assert W(10) == "aaaaaacdee"
    assert P("aaaaaacdee") == 10
    assert W(115246685191495243) == "euler"
    assert P("euler") == 115246685191495243
    assert W(525069350231428029) == "ywuuttttssssrrr"
    assert P("ywuuttttssssrrr") == 525069350231428029

    # ---- Required computation ----
    target = (
        P("legionary")
        + P("calorimeters")
        - P("annihilate")
        + P("orchestrated")
        - P("fluttering")
    )
    print(W(target))


if __name__ == "__main__":
    main()
