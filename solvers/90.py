from __future__ import annotations

from itertools import combinations
from typing import List, Tuple


SQUARE_PAIRS: List[Tuple[int, int]] = [
    (0, 1),  # 01
    (0, 4),  # 04
    (0, 9),  # 09
    (1, 6),  # 16
    (2, 5),  # 25
    (3, 6),  # 36
    (4, 9),  # 49
    (6, 4),  # 64
    (8, 1),  # 81
]


def expand_6_9(mask: int) -> int:
    """If a cube has 6 or 9, treat it as having both (since they can be rotated)."""
    has6 = (mask >> 6) & 1
    has9 = (mask >> 9) & 1
    if has6 or has9:
        mask |= (1 << 6) | (1 << 9)
    return mask


def can_display_all_squares(mask_a: int, mask_b: int) -> bool:
    for x, y in SQUARE_PAIRS:
        bx = 1 << x
        by = 1 << y
        if not ((mask_a & bx and mask_b & by) or (mask_a & by and mask_b & bx)):
            return False
    return True


def solve() -> int:
    masks: List[int] = []
    for comb in combinations(range(10), 6):
        m = 0
        for d in comb:
            m |= 1 << d
        masks.append(m)

    expanded: List[int] = [expand_6_9(m) for m in masks]

    count = 0
    n = len(masks)
    for i in range(n):
        for j in range(i, n):  # unordered pairs, allow i == j
            if can_display_all_squares(expanded[i], expanded[j]):
                count += 1
    return count


if __name__ == "__main__":
    ans = solve()
    print(ans)
