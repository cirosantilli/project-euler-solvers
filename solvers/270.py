"""Project Euler 270 - Cutting Squares.

Print C(30) mod 10^8.

The two example values from the statement are asserted:
C(1) = 2 and C(2) = 30.
"""

from __future__ import annotations

MOD_DEFAULT = 10**8


def boundary_points(N: int):
    """Return the 4N border lattice points of an N x N square in cyclic order."""
    pts = []
    # bottom: (0,0) -> (N,0)
    for x in range(0, N + 1):
        pts.append((x, 0))
    # right: (N,1) -> (N,N)
    for y in range(1, N + 1):
        pts.append((N, y))
    # top: (N-1,N) -> (0,N)
    for x in range(N - 1, -1, -1):
        pts.append((x, N))
    # left: (0,N-1) -> (0,1)
    for y in range(N - 1, 0, -1):
        pts.append((0, y))

    assert len(pts) == 4 * N
    return pts


def side_mask(pt: tuple[int, int], N: int) -> int:
    """4-bit side mask: bottom=1, right=2, top=4, left=8. Corners have 2 bits."""
    x, y = pt
    mask = 0
    if y == 0:
        mask |= 1
    if x == N:
        mask |= 2
    if y == N:
        mask |= 4
    if x == 0:
        mask |= 8
    return mask


def compute_C(N: int, mod: int = MOD_DEFAULT) -> int:
    """Return C(N) modulo mod."""
    pts = boundary_points(N)
    n = len(pts)
    masks = [side_mask(p, N) for p in pts]

    # Only 8 distinct masks occur on an axis-aligned square boundary.
    # Map them to 0..7 for compact bitset state.
    type_map = {
        1: 0,  # B
        2: 1,  # R
        4: 2,  # T
        8: 3,  # L
        3: 4,  # B|R
        6: 5,  # R|T
        12: 6,  # T|L
        9: 7,  # L|B
    }
    types = [type_map[m] for m in masks]

    masks_by_type = [0] * 8
    for m, t in type_map.items():
        masks_by_type[t] = m

    # compat[t] is an 8-bit mask of types that share at least one side with type t.
    compat = [0] * 8
    for t in range(8):
        mt = masks_by_type[t]
        bit = 0
        for u in range(8):
            if mt & masks_by_type[u]:
                bit |= 1 << u
        compat[t] = bit

    ALL_TYPES = (1 << 8) - 1

    # allowed[p][q] is True iff (p,q) can be a cut chord (p<q and q>=p+2).
    allowed = [[False] * n for _ in range(n)]
    for p in range(n):
        for q in range(p + 2, n):
            if masks[p] & masks[q]:
                continue  # share a side -> not on different sides
            allowed[p][q] = True

    # dp[i][j] = number of maximal dissections of the subpolygon i..j (inclusive)
    # with base edge (i,j) on the boundary of that subpolygon.
    dp = [[0] * n for _ in range(n)]
    for i in range(n - 1):
        dp[i][i + 1] = 1  # no area

    for length in range(2, n):
        for i in range(0, n - length):
            j = i + length
            memo: dict[tuple[int, int], int] = {}

            def f(p: int, R: int) -> int:
                """Sum of weighted face-boundary paths from p to j, given constraint R."""
                key = (p, R)
                if key in memo:
                    return memo[key]

                total = 0
                for q in range(p + 1, j + 1):
                    if p == i and q == j:
                        continue  # need at least one intermediate vertex => a real face

                    # Irreducibility constraint: q must intersect all fixed vertices (encoded by R).
                    if ((R >> types[q]) & 1) == 0:
                        continue

                    # Edge (p,q) is either a boundary edge (q=p+1) or an allowed cut chord.
                    if q != p + 1 and not allowed[p][q]:
                        continue

                    # Internal vertices (not the first after i, not j) are non-adjacent to i,
                    # hence must share a side with i.
                    if p != i and q != j and (masks[q] & masks[i]) == 0:
                        continue

                    # If we don't finish at j, then p becomes non-adjacent to j and must share a side with j
                    # (except p==i, because i is adjacent to j).
                    if q != j and p != i and (masks[p] & masks[j]) == 0:
                        continue

                    w = dp[p][q]
                    if w == 0:
                        continue

                    if q == j:
                        total += w
                    else:
                        Rn = R if p == i else (R & compat[types[p]])
                        total += w * f(q, Rn)

                memo[key] = total % mod
                return memo[key]

            dp[i][j] = f(i, ALL_TYPES) % mod

    return dp[0][n - 1] % mod


def main() -> None:
    assert compute_C(1, MOD_DEFAULT) == 2
    assert compute_C(2, MOD_DEFAULT) == 30
    print(compute_C(30, MOD_DEFAULT))


if __name__ == "__main__":
    main()
