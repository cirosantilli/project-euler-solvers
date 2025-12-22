from __future__ import annotations

import math
from typing import Tuple


TARGET = 2_000_000


def rectangle_count(m: int, n: int) -> int:
    """Number of axis-aligned sub-rectangles in an m by n grid."""
    return (m * (m + 1) * n * (n + 1)) // 4


def best_grid_area_near(target: int) -> Tuple[int, int, int]:
    """
    Returns (best_m, best_n, best_area) whose rectangle count is closest to target.
    Uses symmetry (m <= n).
    """
    best_diff = 10**30
    best_m = 0
    best_n = 0
    best_area = 0

    # m*(m+1)/2 grows ~ m^2/2. For target=2e6, m around 2000 is plenty.
    for m in range(1, 3000):
        a = m * (m + 1) // 2  # number of ways to choose vertical sides

        # If even with n=1 we are already above target and getting worse, stop.
        if a > target and (a - target) > best_diff:
            break

        # We want b = n(n+1)/2 close to target/a.
        b_target = target / a
        n0 = int((math.sqrt(1.0 + 8.0 * b_target) - 1.0) / 2.0)

        # Check a small neighborhood around n0 to avoid any rounding issues.
        for n in {max(1, n0 + d) for d in range(-3, 4)}:
            if n < m:
                continue  # enforce m <= n (symmetry)

            b = n * (n + 1) // 2
            cnt = a * b
            diff = abs(cnt - target)
            if diff < best_diff:
                best_diff = diff
                best_m, best_n = m, n
                best_area = m * n

    return best_m, best_n, best_area


def main() -> None:
    # Given example from statement: 3 by 2 contains 18 rectangles
    assert rectangle_count(3, 2) == 18

    m, n, area = best_grid_area_near(TARGET)
    print(area)


if __name__ == "__main__":
    main()
