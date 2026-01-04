from __future__ import annotations

from typing import Optional, Tuple


TARGET_MASK = 0
for d in range(1, 10):
    TARGET_MASK |= 1 << d


def concatenated_product(x: int) -> Tuple[str, int]:
    """
    Returns (concatenated_string, n) for the smallest n such that the concatenation
    of x*1, x*2, ... x*n has length >= 9.
    """
    parts = []
    n = 0
    total_len = 0
    while total_len < 9:
        n += 1
        s = str(x * n)
        parts.append(s)
        total_len += len(s)
    return "".join(parts), n


def is_1_to_9_pandigital(s: str) -> bool:
    if len(s) != 9:
        return False
    mask = 0
    for ch in s:
        d = ord(ch) - 48
        if d == 0:
            return False
        bit = 1 << d
        if mask & bit:
            return False
        mask |= bit
    return mask == TARGET_MASK


def solve() -> int:
    best = 0
    # x cannot exceed 9999; for x >= 10000, x*1 already has 5 digits and
    # concatenating with x*2 gives at least 10 digits.
    for x in range(1, 10000):
        s, n = concatenated_product(x)
        if n > 1 and is_1_to_9_pandigital(s):
            val = int(s)
            if val > best:
                best = val
    return best


def _concat_fixed(x: int, n: int) -> str:
    return "".join(str(x * k) for k in range(1, n + 1))


def main() -> None:
    # Examples from the statement
    assert _concat_fixed(192, 3) == "192384576"
    assert is_1_to_9_pandigital("192384576")
    assert _concat_fixed(9, 5) == "918273645"
    assert is_1_to_9_pandigital("918273645")

    ans = solve()
    print(ans)


if __name__ == "__main__":
    main()
