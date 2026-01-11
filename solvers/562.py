import math
from typing import Optional, Tuple

Vector = Tuple[int, int]


def parents_of(a: int, b: int) -> Tuple[Vector, Vector]:
    """Return u,w with u+w=(a,b) and det(u,w)=1 (a>0, b>0, gcd(a,b)=1)."""
    p = pow(b, -1, a)
    q = (p * b - 1) // a
    return (p, q), (a - p, b - q)


def feasible_translation(r: int, u: Vector, s: Vector) -> bool:
    """Check whether an integer translation places all vertices in the circle."""
    ux, uy = u
    sx, sy = s
    r2 = r * r
    s2 = sx * sx + sy * sy

    num = 4 * r2 - s2
    if num < 0:
        return False

    span = math.isqrt(num) // 2 + 2
    fx = -sx // 2
    fy = -sy // 2

    for dx in range(-span, span + 1):
        ax = fx + dx
        ax2 = ax * ax
        for dy in range(-span, span + 1):
            ay = fy + dy
            if ax2 + ay * ay > r2:
                continue
            tx = ax + ux
            ty = ay + uy
            if tx * tx + ty * ty > r2:
                continue
            tx = ax + sx
            ty = ay + sy
            if tx * tx + ty * ty > r2:
                continue
            return True
    return False


def max_perimeter_triangle(r: int) -> Tuple[float, Vector, Vector, Vector]:
    """Find the maximum-perimeter empty triangle inside the circle."""
    R = 2 * r
    R2 = R * R
    best_per = -1.0
    best_u: Optional[Vector] = None
    best_w: Optional[Vector] = None
    best_s: Optional[Vector] = None

    y = R
    y2 = y * y
    sqrt = math.sqrt
    hypot = math.hypot
    gcd = math.gcd

    for x in range(1, R + 1):
        x2 = x * x
        while x2 + y2 > R2:
            y -= 1
            y2 = y * y
        if y == 0:
            continue

        if gcd(x, y) != 1:
            continue

        s2 = x2 + y2
        l = sqrt(s2)
        if best_per > 0.0:
            if 2.0 * l + 1.0 <= best_per:
                continue

        u, w = parents_of(x, y)
        per = l + hypot(*u) + hypot(*w)
        if per <= best_per:
            continue
        if not feasible_translation(r, u, (x, y)):
            continue

        best_per = per
        best_u, best_w, best_s = u, w, (x, y)

    if best_u is None or best_w is None or best_s is None:
        raise RuntimeError("No valid triangle found")

    return best_per, best_u, best_w, best_s


def compute_T(r: int) -> float:
    _, u, w, s = max_perimeter_triangle(r)
    a = math.hypot(*u)
    b = math.hypot(*w)
    c = math.hypot(*s)
    R = a * b * c / 2.0
    return R / r


def main() -> None:
    # Provided references
    t10 = compute_T(10)
    t100 = compute_T(100)
    assert abs(t10 - 97.26729) < 1e-5
    assert abs(t100 - 9157.64707) < 1e-4

    result = round(compute_T(10_000_000))
    print(result)


if __name__ == "__main__":
    main()
