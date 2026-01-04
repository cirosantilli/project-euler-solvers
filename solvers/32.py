from __future__ import annotations

from typing import Tuple, Set


FULL_MASK = (1 << 9) - 1  # digits 1..9 all present


def digit_mask(n: int) -> Tuple[int, int]:
    """
    Returns (mask, length) where mask has bit (d-1) set if digit d occurs.
    If n contains 0 or repeated digits, returns (-1, 0).
    """
    mask = 0
    length = 0
    while n > 0:
        d = n % 10
        if d == 0:
            return -1, 0
        bit = 1 << (d - 1)
        if mask & bit:
            return -1, 0
        mask |= bit
        length += 1
        n //= 10
    return mask, length


def solve() -> int:
    products: Set[int] = set()

    # Case 1: 1-digit * 4-digit = 4-digit
    for a in range(1, 10):
        ma, la = digit_mask(a)
        if ma < 0:
            continue

        # b is 4-digit; product must be 4-digit => 1000 <= a*b <= 9999
        b_min = (1000 + a - 1) // a
        b_max = 9999 // a
        if b_min < 1000:
            b_min = 1000
        if b_max > 9999:
            b_max = 9999

        for b in range(b_min, b_max + 1):
            mb, lb = digit_mask(b)
            if mb < 0 or (ma & mb):
                continue

            p = a * b
            if p < 1000 or p > 9999:
                continue
            mp, lp = digit_mask(p)
            if mp < 0 or ((ma | mb) & mp):
                continue

            if la + lb + lp == 9 and (ma | mb | mp) == FULL_MASK:
                products.add(p)

    # Case 2: 2-digit * 3-digit = 4-digit
    for a in range(10, 100):
        ma, la = digit_mask(a)
        if ma < 0:
            continue

        # b is 3-digit; product must be 4-digit => 1000 <= a*b <= 9999
        b_min = (1000 + a - 1) // a
        b_max = 9999 // a
        if b_min < 100:
            b_min = 100
        if b_max > 999:
            b_max = 999

        for b in range(b_min, b_max + 1):
            mb, lb = digit_mask(b)
            if mb < 0 or (ma & mb):
                continue

            p = a * b
            if p < 1000 or p > 9999:
                continue
            mp, lp = digit_mask(p)
            if mp < 0 or ((ma | mb) & mp):
                continue

            if la + lb + lp == 9 and (ma | mb | mp) == FULL_MASK:
                products.add(p)

    return sum(products)


if __name__ == "__main__":
    print(solve())
