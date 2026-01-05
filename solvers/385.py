#!/usr/bin/env python3
"""
Project Euler 385 - Ellipses Inside Triangles

Compute A(n): the sum of the areas of all triangles with integer vertices
(x_i, y_i) satisfying |x_i|,|y_i| <= n whose maximum-area inscribed ellipse
(Steiner inellipse) has foci at (±sqrt(13), 0).

No external libraries are used.
"""

from __future__ import annotations

from math import gcd


# Seeds (s, t) for Pell-type equations s^2 - 3 t^2 = K that actually occur here.
# These are the "reduced" positive solutions for each K; multiplying by (2+sqrt(3))^k
# generates all positive solutions in that orbit.
_PELL_SEEDS = {
    468: [(24, 6), (30, 12)],
    117: [(12, 3), (15, 6)],
    36: [(6, 0)],
    9: [(3, 0)],
}


def _pell_step(s: int, t: int) -> tuple[int, int]:
    """
    Multiply (s + t*sqrt(3)) by the fundamental unit (2 + sqrt(3)):

        (s', t') = (2s + 3t, s + 2t)

    This preserves s^2 - 3 t^2.
    """
    return 2 * s + 3 * t, s + 2 * t


def _all_directions() -> list[tuple[int, int, int, int]]:
    """
    Enumerate all primitive integer pairs (m, n) that can occur after reduction,
    i.e., those where D = n^2 + 3 m^2 divides 468 and K = 468 / D is one of the
    Pell K values that has solutions.

    Returns list of (m, n, D, K).
    """
    dirs: list[tuple[int, int, int, int]] = []
    # For D | 468 and D = n^2 + 3 m^2, we have |m| <= sqrt(468/3) < 13 and |n| <= sqrt(468) < 22.
    for m in range(-12, 13):
        for n in range(-21, 22):
            if m == 0 and n == 0:
                continue
            if gcd(abs(m), abs(n)) != 1:
                continue
            D = n * n + 3 * m * m
            if D == 0 or 468 % D != 0:
                continue
            K = 468 // D
            if K in _PELL_SEEDS:
                dirs.append((m, n, D, K))
    return dirs


_DIRS = _all_directions()


def A(N: int) -> int:
    """
    Return A(N) as an integer.
    """
    seen: set[tuple[tuple[int, int], tuple[int, int], tuple[int, int]]] = set()
    total_num_over_4 = 0  # accumulate numerator for area in quarters: area = total/4

    for m, n, D, K in _DIRS:
        # Iterate each Pell orbit for this K.
        for s0, t0 in _PELL_SEEDS[K]:
            s, t = s0, t0

            # s and t grow ~ (2+sqrt(3))^k, so this loop is O(log N).
            # Safe stop: the third vertex is (-c, -d) with c = (s*n)/3 and d = t*m.
            # Hence |s| <= 3N/|n| and |t| <= N/|m| (when m != 0). Using 6N is ample.
            while max(s, t) <= 6 * N + 10:
                if s != 0 and t != 0:
                    # Apply sign choices for (s, t). They correspond to symmetries and
                    # are needed to enumerate all integer triangles in the box.
                    for ss in (s, -s):
                        for tt in (t, -t):
                            # Build p=a+bi and q=c+di (see README for derivation):
                            #   a = ss*m
                            #   b = -tt*n
                            #   c = (ss*n)/3  (must be integer)
                            #   d = tt*m
                            if (ss * n) % 3 != 0:
                                continue
                            a = ss * m
                            b = -tt * n
                            c = (ss * n) // 3
                            d = tt * m

                            # Convert to vertices:
                            #   z1 = (p+q)/2, z2 = (q-p)/2, z3 = -q
                            # Parity condition for Gaussian integrality:
                            if ((a + c) & 1) or ((b + d) & 1):
                                continue

                            x1 = (a + c) // 2
                            y1 = (b + d) // 2
                            x2 = (c - a) // 2
                            y2 = (d - b) // 2
                            x3 = -c
                            y3 = -d

                            if (
                                max(
                                    abs(x1), abs(y1), abs(x2), abs(y2), abs(x3), abs(y3)
                                )
                                > N
                            ):
                                continue

                            tri = tuple(sorted(((x1, y1), (x2, y2), (x3, y3))))
                            if tri in seen:
                                continue
                            seen.add(tri)

                            # Area formula:
                            #   area = D*|s*t| / 4
                            # We add the numerator (over 4) as an integer.
                            total_num_over_4 += D * abs(s * t)

                s, t = _pell_step(s, t)

    # The total should be an integer area sum.
    assert total_num_over_4 % 4 == 0
    return total_num_over_4 // 4


def main() -> None:
    # Test values from the problem statement
    assert A(8) == 72
    assert A(10) == 252
    assert A(100) == 34632
    assert A(1000) == 3529008

    print(A(10**9))


if __name__ == "__main__":
    main()
