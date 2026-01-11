from __future__ import annotations

import math
from typing import Set


def _count_triangles(n: int) -> int:
    # Parameterization via equal sums of squares on doubled variables:
    # X = pr + qs, K = pr - qs, Y = |ps - qr| with X, Y, K even.
    # Then a = (X - Y)/2, b = (X + Y)/2, c = K.
    # Constraints: K > 0, K <= n, X + Y <= 2K.
    seen: Set[int] = set()
    n15 = (3 * n) // 2

    for p in range(1, n + 1):
        r_max = n15 // p
        for r in range(1, r_max + 1):
            pr = p * r
            s_max = pr // 3
            if s_max == 0:
                continue
            for s in range(1, s_max + 1):
                # q*s <= pr/3 and pr - q*s <= n
                if pr > n:
                    q_min = (pr - n + s - 1) // s
                else:
                    q_min = 1
                q_max = pr // (3 * s)
                if q_max < q_min:
                    continue

                # Split by q*r <= p*s
                q_split = (p * s) // r

                # Case 1: q <= q_split, Y = p*s - q*r
                if q_min <= q_split:
                    q1_max = min(q_split, q_max)
                    if r < 3 * s:
                        bound = (p * (r - s)) // (3 * s - r)
                        q1_max = min(q1_max, bound)
                    for q in range(q_min, q1_max + 1):
                        qs = q * s
                        k = pr - qs
                        if k <= 0 or k > n:
                            continue
                        x = pr + qs
                        y = p * s - q * r
                        if x + y > 2 * k or x <= k:
                            continue
                        if (x | y | k) & 1:
                            continue
                        a = (x - y) // 2
                        b = (x + y) // 2
                        if a <= 0 or a > b or b > k:
                            continue
                        key = (a << 40) | (b << 20) | k
                        seen.add(key)

                # Case 2: q >= q_split + 1, Y = q*r - p*s
                q2_min = max(q_min, q_split + 1)
                if q2_min <= q_max:
                    bound = (p * (r + s)) // (r + 3 * s)
                    q2_max = min(q_max, bound)
                    for q in range(q2_min, q2_max + 1):
                        qs = q * s
                        k = pr - qs
                        if k <= 0 or k > n:
                            continue
                        x = pr + qs
                        y = q * r - p * s
                        if x + y > 2 * k or x <= k:
                            continue
                        if (x | y | k) & 1:
                            continue
                        a = (x - y) // 2
                        b = (x + y) // 2
                        if a <= 0 or a > b or b > k:
                            continue
                        key = (a << 40) | (b << 20) | k
                        seen.add(key)

    return len(seen)


def main() -> None:
    # Provided samples
    assert _count_triangles(10) == 3
    assert _count_triangles(50) == 165

    result = _count_triangles(100000)
    print(result)


if __name__ == "__main__":
    main()
