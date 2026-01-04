from __future__ import annotations

from typing import List, Tuple


LIMIT = 1_000_000_000


def triangle_area_isosceles(a: int, b: int) -> int:
    """
    Isosceles triangle with equal sides a,a and base b.
    Area = b/4 * sqrt(4a^2 - b^2). Assumes it is integral.
    """
    d = 4 * a * a - b * b
    k = int(d**0.5)
    assert k * k == d
    assert (b * k) % 4 == 0
    return (b * k) // 4


def generate_almost_equilateral_perimeters(limit: int) -> List[int]:
    """
    Generates perimeters of almost equilateral triangles (a,a,a±1)
    with integral sides and integral area, perimeter <= limit.
    Uses solutions to x^2 - 3y^2 = 4.
    """
    # First non-degenerate solution to x^2 - 3y^2 = 4 that yields a valid triangle:
    # (x,y) = (14,8) -> a=5, b=6, perimeter=16
    x, y = 14, 8

    perimeters: List[int] = []
    while True:
        if x % 3 == 2:
            # x = 3a - 1  => a = (x+1)/3, triangle (a,a,a+1), perimeter = 3a+1
            a = (x + 1) // 3
            p = 3 * a + 1
        else:
            # x = 3a + 1 => a = (x-1)/3, triangle (a,a,a-1), perimeter = 3a-1
            a = (x - 1) // 3
            p = 3 * a - 1

        if p > limit:
            break
        perimeters.append(p)

        # Next Pell-type solution via multiplication by (2 + sqrt(3)):
        # (x + y√3) <- (x + y√3)(2 + √3)
        x, y = 2 * x + 3 * y, x + 2 * y

    return perimeters


def main() -> None:
    # Small correctness checks from the statement
    assert triangle_area_isosceles(5, 6) == 12  # 5-5-6 has area 12

    # Check first few perimeters
    assert generate_almost_equilateral_perimeters(1000) == [16, 50, 196, 722]

    perimeters = generate_almost_equilateral_perimeters(LIMIT)
    ans = sum(perimeters)

    assert ans == 518_408_346

    print(ans)


if __name__ == "__main__":
    main()
