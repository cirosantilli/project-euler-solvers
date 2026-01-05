# solution.py
# Project Euler 224: Almost right-angled triangles II
#
# We count integer-sided triangles (a <= b <= c) satisfying:
#   a^2 + b^2 = c^2 - 1
# with perimeter a + b + c <= 75,000,000.
#
# Key idea: all solutions are generated uniquely from the root (2,2,3) using
# three linear transformations (a Berggren-like tree). We DFS the tree and
# prune by perimeter.

from __future__ import annotations


def solve(limit: int = 75_000_000) -> int:
    # Root solution
    stack = [(2, 2, 3)]
    cnt = 0
    lim = limit

    while stack:
        a, b, c = stack.pop()
        p = a + b + c
        if p > lim:
            continue

        cnt += 1

        # Children via the three transformations:
        # M1 * (a,b,c)
        x = a - 2 * b + 2 * c
        y = 2 * a - b + 2 * c
        z = 2 * a - 2 * b + 3 * c
        if x + y + z <= lim:
            stack.append((x, y, z))

        # M2 * (a,b,c)
        # For a == b, this branch duplicates another path near the root; skip it.
        if a != b:
            x = -a + 2 * b + 2 * c
            y = -2 * a + b + 2 * c
            z = -2 * a + 2 * b + 3 * c
            if x + y + z <= lim:
                stack.append((x, y, z))

        # M3 * (a,b,c)
        x = 2 * a + b + 2 * c
        y = a + 2 * b + 2 * c
        z = 2 * a + 2 * b + 3 * c
        if x + y + z <= lim:
            stack.append((x, y, z))

    return cnt


def _self_test() -> None:
    # Not given in the original Project Euler statement, but useful sanity checks:
    assert solve(21) == 2  # (2,2,3) and (4,8,9)
    assert solve(75_000_000) == 4_137_330


if __name__ == "__main__":
    _self_test()
    print(solve())
