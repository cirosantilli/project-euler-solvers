#!/usr/bin/env python3
"""
Project Euler 314: The Mouse on the Moon

Maximize enclosed Area / wall Length inside a 500x500 grid of integer posts.

Approach:
- Use symmetry: solve on a 250x250 reduced domain (one corner), ratio is unchanged.
- Use Dinkelbach's method for fractional optimization:
    maximize A/P  <=> iteratively solve maximize (A - r*P) for r
- For fixed r, solve maximize (A - r*P) via DP with a 1D "upper envelope" speed-up.

Performance:
- Pure Python is usually slow for this DP. If numba is available, we JIT compile the DP.
"""

from __future__ import annotations

import math

try:
    import numpy as np
except ImportError:  # extremely unlikely in most Euler solver environments
    np = None

try:
    from numba import njit

    HAS_NUMBA = True
except Exception:
    HAS_NUMBA = False
    njit = None


def square_ratio() -> float:
    """Statement check: 2000m wall around entire 250000 m^2 square => ratio 125."""
    return 250000.0 / 2000.0


def triangle_cut_ratio() -> float:
    """
    Statement example:
    cut off four corner triangles with sides 75, 75, 75*sqrt(2).
    Area = 250000 - 4*(75*75/2) = 238750
    Perimeter = 4*(500-2*75) + 4*sqrt(75^2+75^2) = 1400 + 300*sqrt(2)
    Ratio ≈ 130.87
    """
    area = 250000.0 - 4.0 * (75.0 * 75.0 / 2.0)
    peri = 4.0 * (500.0 - 2.0 * 75.0) + 4.0 * math.hypot(75.0, 75.0)
    return area / peri


def _build_dist(n: int):
    """dist[dx,dy] = sqrt(dx^2+dy^2) for dx,dy in [0..n]."""
    dist = np.empty((n + 1, n + 1), dtype=np.float64)
    for dx in range(n + 1):
        for dy in range(n + 1):
            dist[dx, dy] = math.hypot(dx, dy)
    return dist


def _solve_with_numba() -> float:
    if np is None:
        raise RuntimeError("numpy is required for the numba-accelerated solver.")

    n = 250
    dist = _build_dist(n)

    NEG = -1.0e300
    NEG_HALF = NEG / 2.0

    @njit(cache=True)
    def intersect(a: int, Sa: float, b: int, Sb: float, dx: int, r: float) -> int:
        """
        Smallest integer j >= b where f_b(j) >= f_a(j), else n+1.
        f_y(j) = S_y - r * sqrt(dx^2 + (j-y)^2)
        """
        k = b - a
        dS = Sb - Sa
        if dS >= 0.0:
            return b

        # If b never overtakes a:
        if dS + r * k <= 0.0:
            return n + 1

        # Solve crossing in reals, then round up + fix-up.
        C = (Sa - Sb) / r  # positive
        A = k * k - C * C  # > 0
        u = (-k + C * math.sqrt(1.0 + (4.0 * dx * dx) / A)) * 0.5
        j0 = int(b + u)
        if j0 < b:
            j0 = b

        # Fix-up for rounding error:
        while j0 <= n:
            fb = Sb - r * dist[dx, j0 - b]
            fa = Sa - r * dist[dx, j0 - a]
            if fb >= fa - 1e-13:
                break
            j0 += 1

        if j0 > n:
            return n + 1
        return j0

    @njit(cache=True)
    def solve_for_ratio(r: float) -> tuple[float, float]:
        """
        Returns (area, perimeter) for the shape that maximizes (A - r*P).
        """
        # DP score grid and parent pointers to reconstruct best path.
        dp = np.empty((n + 1, n + 1), dtype=np.float64)
        parx = np.empty((n + 1, n + 1), dtype=np.int16)
        pary = np.empty((n + 1, n + 1), dtype=np.int16)

        for i in range(n + 1):
            for j in range(n + 1):
                dp[i, j] = NEG
                parx[i, j] = -1
                pary[i, j] = -1

        # Initialization: allow initial vertical segment on x=0 of length y
        for y in range(n + 1):
            dp[0, y] = -r * y

        sites = np.empty(n + 1, dtype=np.int16)
        starts = np.empty(n + 1, dtype=np.int16)
        vals = np.empty(n + 1, dtype=np.float64)

        best = np.empty(n + 1, dtype=np.float64)
        best_px = np.empty(n + 1, dtype=np.int16)
        best_py = np.empty(n + 1, dtype=np.int16)

        for i in range(1, n + 1):
            for j in range(n + 1):
                best[j] = NEG
                best_px[j] = -1
                best_py[j] = -1

            for x in range(i):
                dx = i - x
                halfdx = 0.5 * dx

                # Build envelope over y
                m = 0
                for y in range(n + 1):
                    v = dp[x, y]
                    if v <= NEG_HALF:
                        continue
                    Sy = v + halfdx * y

                    if m == 0:
                        sites[0] = y
                        vals[0] = Sy
                        starts[0] = y
                        m = 1
                        continue

                    while m > 0:
                        y_last = int(sites[m - 1])
                        S_last = vals[m - 1]
                        j0 = intersect(y_last, S_last, y, Sy, dx, r)
                        if j0 <= starts[m - 1]:
                            m -= 1
                            if m == 0:
                                break
                        else:
                            break

                    if m == 0:
                        sites[0] = y
                        vals[0] = Sy
                        starts[0] = y
                        m = 1
                    else:
                        sites[m] = y
                        vals[m] = Sy
                        starts[m] = j0
                        m += 1

                # Query envelope for all j
                idx = 0
                for j in range(n + 1):
                    while idx + 1 < m and j >= starts[idx + 1]:
                        idx += 1
                    yb = int(sites[idx])
                    if yb > j:
                        continue
                    score = vals[idx] - r * dist[dx, j - yb] + halfdx * j
                    if score > best[j]:
                        best[j] = score
                        best_px[j] = x
                        best_py[j] = yb

            # Commit row i
            for j in range(n + 1):
                dp[i, j] = best[j]
                parx[i, j] = best_px[j]
                pary[i, j] = best_py[j]

        # Reconstruct path from (n,n) back to x=0
        path_x = np.empty(n + 2, dtype=np.int16)
        path_y = np.empty(n + 2, dtype=np.int16)
        k = 0
        cx = n
        cy = n
        while cx != 0:
            path_x[k] = cx
            path_y[k] = cy
            px = int(parx[cx, cy])
            py = int(pary[cx, cy])
            cx = px
            cy = py
            k += 1
        path_x[k] = 0
        path_y[k] = cy
        k += 1

        # Reverse in-place
        for t in range(k // 2):
            tx = path_x[t]
            ty = path_y[t]
            path_x[t] = path_x[k - 1 - t]
            path_y[t] = path_y[k - 1 - t]
            path_x[k - 1 - t] = tx
            path_y[k - 1 - t] = ty

        # Compute area and perimeter from path
        y0 = float(path_y[0])
        area = 0.0
        peri = y0  # initial vertical segment from (0,0) to (0,y0)

        for t in range(k - 1):
            x1 = int(path_x[t])
            y1 = int(path_y[t])
            x2 = int(path_x[t + 1])
            y2 = int(path_y[t + 1])
            dx = x2 - x1
            dy = y2 - y1
            if dy < 0:
                dy = -dy
            area += (y1 + y2) * dx * 0.5
            peri += dist[dx, dy]

        return area, peri

    # Dinkelbach iteration: converges very fast here (typically ~3-6 iterations)
    r = triangle_cut_ratio()
    for _ in range(12):
        area, peri = solve_for_ratio(r)
        new_r = area / peri
        if abs(new_r - r) < 5e-13:
            r = new_r
            break
        r = new_r

    return r


def compute_answer() -> float:
    # Asserts for statement-provided values
    assert abs(square_ratio() - 125.0) < 1e-12
    assert round(triangle_cut_ratio(), 2) == 130.87

    if HAS_NUMBA:
        return _solve_with_numba()

    # Pure-Python fallback (correct but usually slow).
    # If your environment doesn’t have numba, consider installing it for speed.
    from array import array

    n = 250
    dist = [[0.0] * (n + 1) for _ in range(n + 1)]
    for dx in range(n + 1):
        row = dist[dx]
        for dy in range(n + 1):
            row[dy] = math.hypot(dx, dy)

    NEG_INF = -1e300
    NEG_HALF = NEG_INF / 2.0
    rn1 = range(n + 1)

    def intersect(a, Sa, b, Sb, dx, r):
        k = b - a
        dS = Sb - Sa
        if dS >= 0.0:
            return b
        if dS + r * k <= 0.0:
            return n + 1
        C = (Sa - Sb) / r
        A = k * k - C * C
        u = (-k + C * math.sqrt(1.0 + 4.0 * dx * dx / A)) * 0.5
        j0 = int(b + u)
        if j0 < b:
            j0 = b
        dist_dx = dist[dx]
        while j0 <= n:
            fb = Sb - r * dist_dx[j0 - b]
            fa = Sa - r * dist_dx[j0 - a]
            if fb >= fa - 1e-13:
                break
            j0 += 1
        return j0 if j0 <= n else n + 1

    def solve_for_ratio(ratio):
        dp = [array("d", [NEG_INF] * (n + 1)) for _ in range(n + 1)]
        parx = [array("h", [-1] * (n + 1)) for _ in range(n + 1)]
        pary = [array("h", [-1] * (n + 1)) for _ in range(n + 1)]

        for y in rn1:
            dp[0][y] = -ratio * y

        for i in range(1, n + 1):
            best = [NEG_INF] * (n + 1)
            best_px = array("h", [-1] * (n + 1))
            best_py = array("h", [-1] * (n + 1))

            for x in range(i):
                dx = i - x
                halfdx = 0.5 * dx
                prev = dp[x]
                dist_dx = dist[dx]

                sites = []
                vals = []
                starts = []

                for y in rn1:
                    v = prev[y]
                    if v <= NEG_HALF:
                        continue
                    Sy = v + halfdx * y
                    if not sites:
                        sites.append(y)
                        vals.append(Sy)
                        starts.append(y)
                        continue

                    while sites:
                        y_last = sites[-1]
                        S_last = vals[-1]
                        j0 = intersect(y_last, S_last, y, Sy, dx, ratio)
                        if j0 <= starts[-1]:
                            sites.pop()
                            vals.pop()
                            starts.pop()
                            if not sites:
                                break
                        else:
                            break

                    if not sites:
                        sites.append(y)
                        vals.append(Sy)
                        starts.append(y)
                    else:
                        sites.append(y)
                        vals.append(Sy)
                        starts.append(j0)

                idx = 0
                L = len(sites)
                for j in rn1:
                    while idx + 1 < L and j >= starts[idx + 1]:
                        idx += 1
                    yb = sites[idx]
                    if yb > j:
                        continue
                    score = vals[idx] - ratio * dist_dx[j - yb] + halfdx * j
                    if score > best[j]:
                        best[j] = score
                        best_px[j] = x
                        best_py[j] = yb

            dp[i] = array("d", best)
            parx[i] = best_px
            pary[i] = best_py

        # reconstruct
        path = []
        cx, cy = n, n
        while cx != 0:
            path.append((cx, cy))
            px = int(parx[cx][cy])
            py = int(pary[cx][cy])
            cx, cy = px, py
        path.append((0, cy))
        path.reverse()

        y0 = path[0][1]
        area = 0.0
        peri = float(y0)
        for (x1, y1), (x2, y2) in zip(path, path[1:]):
            dx = x2 - x1
            dy = y2 - y1
            if dy < 0:
                dy = -dy
            area += (y1 + y2) * dx * 0.5
            peri += math.hypot(dx, dy)
        return area, peri

    r = triangle_cut_ratio()
    for _ in range(12):
        area, peri = solve_for_ratio(r)
        new_r = area / peri
        if abs(new_r - r) < 5e-13:
            r = new_r
            break
        r = new_r

    return r


def main() -> None:
    ans = compute_answer()
    print(f"{ans:.8f}")


if __name__ == "__main__":
    main()
