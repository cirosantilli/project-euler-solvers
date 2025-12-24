from __future__ import annotations

from typing import List, Tuple


Point = Tuple[int, int]
Triangle = Tuple[Point, Point, Point]


def cross(ax: int, ay: int, bx: int, by: int) -> int:
    """2D cross product (ax,ay) x (bx,by)."""
    return ax * by - ay * bx


def contains_origin_strict(tri: Triangle) -> bool:
    """
    Return True iff the origin (0,0) lies strictly inside the triangle.
    Uses same-side-of-edges test via cross products.
    """
    (x1, y1), (x2, y2), (x3, y3) = tri

    # s1 = cross(B-A, O-A) where O=(0,0), so O-A = (-x1, -y1)
    s1 = cross(x2 - x1, y2 - y1, -x1, -y1)
    s2 = cross(x3 - x2, y3 - y2, -x2, -y2)
    s3 = cross(x1 - x3, y1 - y3, -x3, -y3)

    # Strictly inside => all same sign and none zero
    if s1 == 0 or s2 == 0 or s3 == 0:
        return False
    return (s1 > 0 and s2 > 0 and s3 > 0) or (s1 < 0 and s2 < 0 and s3 < 0)


def parse_triangles(path: str) -> List[Triangle]:
    tris: List[Triangle] = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            nums = [int(x) for x in line.split(",")]
            if len(nums) != 6:
                raise ValueError(f"Bad line (expected 6 ints): {line!r}")
            x1, y1, x2, y2, x3, y3 = nums
            tris.append(((x1, y1), (x2, y2), (x3, y3)))
    return tris


def solve(path: str) -> int:
    tris = parse_triangles(path)
    return sum(1 for t in tris if contains_origin_strict(t))


def main() -> None:
    # Provided examples in the problem statement
    abc: Triangle = ((-340, 495), (-153, -910), (835, -947))
    xyz: Triangle = ((-175, 41), (-421, -714), (574, -645))
    assert contains_origin_strict(abc) is True
    assert contains_origin_strict(xyz) is False

    # File name per instruction: use the basename from the statement's link.
    # (Fallback to 'triangles.txt' if needed.)
    path_candidates = ["0102_triangles.txt", "triangles.txt"]
    last_err: Exception | None = None
    for p in path_candidates:
        try:
            ans = solve(p)
            print(ans)
            return
        except OSError as e:
            last_err = e

    raise SystemExit(f"Could not open triangles input file. Last error: {last_err}")


if __name__ == "__main__":
    main()
