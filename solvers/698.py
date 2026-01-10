#!/usr/bin/env python3
"""
Project Euler 698: 123 Numbers

We enumerate "123-numbers" in increasing numeric order. Since all digits are from {1,2,3},
numeric order is equivalent to:
  1) increasing length (number of digits),
  2) lexicographic order within a fixed length.

A length-L number is valid iff for each digit that appears, its total count is itself a 123-number.
"""

from functools import lru_cache

MOD = 123_123_123
TARGET_N = 111_111_111_111_222_333


@lru_cache(None)
def is_123_number(x: int) -> bool:
    """Return True iff x is a 123-number (as an integer)."""
    if x == 1:
        return True
    if x <= 0:
        return False

    s = str(x)
    for ch in s:
        if ch not in "123":
            return False

    c1 = s.count("1")
    c2 = s.count("2")
    c3 = s.count("3")

    if c1 and not is_123_number(c1):
        return False
    if c2 and not is_123_number(c2):
        return False
    if c3 and not is_123_number(c3):
        return False

    return True


def factorials_up_to(n: int) -> list[int]:
    fact = [1] * (n + 1)
    for i in range(1, n + 1):
        fact[i] = fact[i - 1] * i
    return fact


def allowed_counts_up_to(L: int) -> list[int]:
    """All positive integers <= L that are 123-numbers."""
    return [i for i in range(1, L + 1) if is_123_number(i)]


def multinomial_from_fact(fact: list[int], n: int, a: int, b: int, c: int) -> int:
    return fact[n] // (fact[a] * fact[b] * fact[c])


def count_valid_length(L: int, allowed: list[int], fact: list[int]) -> int:
    """
    Count valid length-L strings over {1,2,3}.
    Valid means the total counts (a,b,c) sum to L and each positive count is a 123-number.
    """
    poss = [0] + allowed
    poss_set = set(poss)
    total = 0
    for a in poss:
        for b in poss:
            s = a + b
            if s > L:
                continue
            c = L - s
            if c in poss_set:
                if a == 0 and b == 0 and c == 0:
                    continue
                total += multinomial_from_fact(fact, L, a, b, c)
    return total


def find_length_and_rank(n: int) -> tuple[int, int, list[int], list[int]]:
    """
    Find the length L such that the n-th 123-number has length L.
    Returns (L, k, allowed_counts, fact) where k is the 1-based index within the length-L block.
    """
    if n <= 0:
        raise ValueError("n must be positive")

    fact = [1]  # fact[i] = i!
    allowed: list[int] = []
    cumulative = 0

    for L in range(1, 5000):  # generous safety bound
        fact.append(fact[-1] * L)
        if is_123_number(L):
            allowed.append(L)

        cnt_L = count_valid_length(L, allowed, fact)
        if cumulative + cnt_L >= n:
            k = n - cumulative
            return L, k, allowed, fact
        cumulative += cnt_L

    raise RuntimeError("Failed to find length within search limit.")


def valid_total_triples(L: int, allowed: list[int]) -> list[tuple[int, int, int]]:
    poss = [0] + allowed
    poss_set = set(poss)
    triples: list[tuple[int, int, int]] = []
    for a in poss:
        for b in poss:
            s = a + b
            if s > L:
                continue
            c = L - s
            if c in poss_set:
                if a == 0 and b == 0 and c == 0:
                    continue
                triples.append((a, b, c))
    return triples


def count_completions(
    L: int,
    fact: list[int],
    triples: list[tuple[int, int, int]],
    used1: int,
    used2: int,
    used3: int,
) -> int:
    """
    Given a prefix that used (used1, used2, used3) digits, count how many valid length-L strings
    extend this prefix.
    """
    used = used1 + used2 + used3
    r = L - used
    total = 0
    for a, b, c in triples:
        if used1 <= a and used2 <= b and used3 <= c:
            ra = a - used1
            rb = b - used2
            rc = c - used3
            if ra + rb + rc != r:
                continue
            total += fact[r] // (fact[ra] * fact[rb] * fact[rc])
    return total


def nth_123_string(n: int) -> str:
    """Return the exact decimal string of F(n)."""
    L, k, _, _ = find_length_and_rank(n)

    fact = factorials_up_to(L)
    allowed = allowed_counts_up_to(L)
    triples = valid_total_triples(L, allowed)

    used1 = used2 = used3 = 0
    out_digits: list[str] = []

    for _pos in range(L):
        for digit in (1, 2, 3):
            n1, n2, n3 = used1, used2, used3
            if digit == 1:
                n1 += 1
            elif digit == 2:
                n2 += 1
            else:
                n3 += 1

            cnt = count_completions(L, fact, triples, n1, n2, n3)
            if k > cnt:
                k -= cnt
            else:
                out_digits.append(str(digit))
                used1, used2, used3 = n1, n2, n3
                break
        else:
            raise RuntimeError("Unranking failed (no digit chosen).")

    return "".join(out_digits)


def mod_of_decimal_string(s: str, mod: int) -> int:
    v = 0
    for ch in s:
        v = (v * 10 + (ord(ch) - 48)) % mod
    return v


def _run_examples() -> None:
    # Examples given in the problem statement:
    assert nth_123_string(4) == "11"
    assert nth_123_string(10) == "31"
    assert nth_123_string(40) == "1112"
    assert nth_123_string(1000) == "1223321"
    assert nth_123_string(6000) == "2333333333323"


def main() -> None:
    _run_examples()
    value = nth_123_string(TARGET_N)
    print(mod_of_decimal_string(value, MOD))


if __name__ == "__main__":
    main()
