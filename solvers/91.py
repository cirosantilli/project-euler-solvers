from __future__ import annotations

from math import gcd


def count_right_triangles(n: int) -> int:
    """
    Count right triangles OPQ with O=(0,0), P and Q integer points in [0,n]x[0,n],
    P != Q, P,Q != O.
    """
    total = n * n  # right angle at the origin: (x,0) with (0,y), x,y in 1..n

    for x in range(n + 1):
        for y in range(n + 1):
            if x == 0 and y == 0:
                continue

            # Right angle at P=(x,y): OP ⟂ PQ
            if x == 0 or y == 0:
                # OP is axis-aligned => PQ must be perpendicular axis-aligned line through P.
                # Within the square there are exactly n choices for the other point Q.
                total += n
            else:
                g = gcd(x, y)
                dx = y // g
                dy = x // g

                # Move along (-dx, +dy)
                k1 = min(x // dx, (n - y) // dy)
                # Move along (+dx, -dy)
                k2 = min((n - x) // dx, y // dy)

                total += k1 + k2

    return total


def main() -> None:
    # Example from the statement: for n=2 there are 14 right triangles
    assert count_right_triangles(2) == 14

    ans = count_right_triangles(50)
    print(ans)


if __name__ == "__main__":
    main()
