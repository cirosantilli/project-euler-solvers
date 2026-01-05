from __future__ import annotations

from typing import Dict, List, Tuple


def collatz_length(
    n: int, limit: int, cache_small: List[int], cache_big: Dict[int, int]
) -> int:
    """
    Returns the number of terms in the Collatz chain starting at n and ending at 1 (inclusive).
    Uses memoization in cache_small for values <= limit and cache_big for values > limit.
    """
    m = n
    path: List[int] = []

    while True:
        if m <= limit:
            cm = cache_small[m]
            if cm:
                length = cm
                break
        else:
            cm = cache_big.get(m)
            if cm is not None:
                length = cm
                break

        path.append(m)
        if m & 1:
            m = 3 * m + 1
        else:
            m //= 2

    # Propagate known length back through the path
    for v in reversed(path):
        length += 1
        if v <= limit:
            cache_small[v] = length
        else:
            cache_big[v] = length

    if n <= limit:
        return cache_small[n]
    return cache_big[n]


def longest_collatz_under(limit: int) -> Tuple[int, int]:
    """
    Returns (starting_number, chain_length) for the longest Collatz chain with start < limit.
    """
    cache_small = [0] * (limit + 1)
    cache_small[1] = 1
    cache_big: Dict[int, int] = {}

    best_n = 1
    best_len = 1

    for n in range(1, limit):
        ln = collatz_length(n, limit, cache_small, cache_big)
        if ln > best_len:
            best_len = ln
            best_n = n

    return best_n, best_len


def main() -> None:
    # Problem statement example: 13 produces a chain of 10 terms.
    limit = 1_000_000
    cache_small = [0] * (limit + 1)
    cache_small[1] = 1
    cache_big: Dict[int, int] = {}
    assert collatz_length(1, limit, cache_small, cache_big) == 1
    assert collatz_length(13, limit, cache_small, cache_big) == 10

    ans_n, ans_len = longest_collatz_under(1_000_000)

    print(ans_n)


if __name__ == "__main__":
    main()
