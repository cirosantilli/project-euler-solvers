import math
from typing import Optional, Tuple

Vector = Tuple[int, int]


def parents_of(a: int, b: int) -> Tuple[Vector, Vector]:
    """Return the unique parents u,w with u+w=(a,b) and det(u,w)=1.

    Assumes a>0 and gcd(a,b)=1.
    """
    # Solve a*q - b*p = 1 with 0 <= p < a.
    p = pow(b, -1, a)
    q = (p * b - 1) // a
    u = (p, q)
    w = (a - p, b - q)
    return u, w


def feasible_near_mid(r: int, u: Vector, s: Vector) -> bool:
    """Check if there exists a lattice translation placing the triangle in the circle.

    For near-maximal perimeter, the long side s is close to a diameter, so a valid
    translation is within a small neighborhood of -s/2. We check a 3x3 block there.
    """
    ux, uy = u
    sx, sy = s
    ax0 = -sx / 2.0
    ay0 = -sy / 2.0
    r2 = r * r

    fx = math.floor(ax0)
    fy = math.floor(ay0)
    for dx in (-1, 0, 1):
        ax = fx + dx
        ax2 = ax * ax
        for dy in (-1, 0, 1):
            ay = fy + dy
            maxd = ax2 + ay * ay
            if maxd > r2:
                continue
            tx = ax + ux
            ty = ay + uy
            d1 = tx * tx + ty * ty
            if d1 > r2:
                continue
            tx = ax + sx
            ty = ay + sy
            d2 = tx * tx + ty * ty
            if d2 > r2:
                continue
            return True
    return False


def max_perimeter_triangle(r: int) -> Tuple[float, Vector, Vector, Vector]:
    """Find maximum perimeter empty triangle inside circle radius r.

    Returns (perimeter, u, w, s) where u+w=s and det(u,w)=1.
    """
    R = 2 * r
    R2 = R * R
    best_per = 0.0
    best_u: Optional[Vector] = None
    best_w: Optional[Vector] = None
    best_s: Optional[Vector] = None

    max_attempts = 10

    for x in range(1, R + 1):
        y = math.isqrt(R2 - x * x)
        yy = y
        attempts = 0
        while yy >= 0 and attempts < max_attempts:
            if math.gcd(x, yy) == 1:
                s = (x, yy)
                u, w = parents_of(x, yy)
                if feasible_near_mid(r, u, s):
                    per = math.hypot(u[0], u[1]) + math.hypot(w[0], w[1]) + math.hypot(s[0], s[1])
                    if per > best_per:
                        best_per = per
                        best_u, best_w, best_s = u, w, s
                    break
            yy -= 1
            attempts += 1

    if best_u is None or best_w is None or best_s is None:
        raise RuntimeError("No valid triangle found")

    return best_per, best_u, best_w, best_s


def compute_T(r: int) -> float:
    per, u, w, s = max_perimeter_triangle(r)
    a = math.hypot(u[0], u[1])
    b = math.hypot(w[0], w[1])
    c = math.hypot(s[0], s[1])
    # area is 1/2, so R = abc / (4 * area) = abc / 2
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
