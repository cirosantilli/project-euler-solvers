#!/usr/bin/env python3
"""
Project Euler 262: Mountain Range

We are given a continuous terrain height function h(x,y). A mosquito flies
at a constant elevation f (i.e., in the plane z=f) and can only travel over
points where h(x,y) <= f.

Tasks:
1) Find f_min, the minimum elevation for which a path from A=(200,200) to
   B=(1400,1400) exists inside 0<=x,y<=1600.
2) At that elevation f_min, find the shortest such path length in the plane.

The answer must be rounded to 3 decimal places.

Note: The PE problem statement provides no explicit numerical test values,
so there are no "statement asserts" to add. We include sanity asserts.
"""

import math
import random

# Domain and endpoints
L = 1600.0
A = (200.0, 200.0)
B = (1400.0, 1400.0)


# ---------- Terrain height and gradient (analytic) ----------


def h_and_grad(x: float, y: float):
    """
    Returns (h(x,y), dh/dx, dh/dy).
    The formula matches Project Euler's "programming language friendly" form:
      h=( 5000-0.005*(x*x+y*y+x*y)+12.5*(x+y) ) * exp( -abs(0.000001*(x*x+y*y)-0.0015*(x+y)+0.7) )
    """
    xx = x * x
    yy = y * y
    P = 5000.0 - 0.005 * (xx + yy + x * y) + 12.5 * (x + y)
    Q = 1e-6 * (xx + yy) - 0.0015 * (x + y) + 0.7
    absQ = abs(Q)
    E = math.exp(-absQ)
    h = P * E

    # derivatives
    # P_x = 12.5 - 0.01x - 0.005y
    # P_y = 12.5 - 0.01y - 0.005x
    Px = 12.5 - 0.01 * x - 0.005 * y
    Py = 12.5 - 0.01 * y - 0.005 * x

    # Q_x = 2e-6 x - 0.0015
    # Q_y = 2e-6 y - 0.0015
    Qx = 2e-6 * x - 0.0015
    Qy = 2e-6 * y - 0.0015

    # derivative of exp(-abs(Q)) is exp(-abs(Q)) * (-sign(Q)) * Q'
    sign = 1.0 if Q >= 0.0 else -1.0

    hx = E * (Px - P * sign * Qx)
    hy = E * (Py - P * sign * Qy)
    return h, hx, hy


def h_only(x: float, y: float) -> float:
    return h_and_grad(x, y)[0]


# ---------- Step 1: Compute f_min ----------
#
# For this specific landscape, the minimax "pass" happens at a boundary tangency
# point on x=0 (symmetrically y=0). Therefore:
#    f_min = max_{0<=y<=1600} h(0,y)
#
# We compute it by coarse scan + golden-section refinement.


def golden_section_maximize(f, a, b, iters=200, tol=1e-13):
    """Maximize unimodal f on [a,b] via golden section search."""
    phi = (math.sqrt(5.0) - 1.0) / 2.0
    c = b - phi * (b - a)
    d = a + phi * (b - a)
    fc = f(c)
    fd = f(d)
    for _ in range(iters):
        if b - a < tol:
            break
        if fc < fd:
            a = c
            c = d
            fc = fd
            d = a + phi * (b - a)
            fd = f(d)
        else:
            b = d
            d = c
            fd = fc
            c = b - phi * (b - a)
            fc = f(c)
    xopt = (a + b) / 2.0
    return xopt, f(xopt)


def compute_f_min():
    # Coarse scan on y=0..1600, x=0 boundary
    best_y = 0.0
    best_h = -1e100
    for yi in range(0, 1601):
        v = h_only(0.0, float(yi))
        if v > best_h:
            best_h = v
            best_y = float(yi)

    # refine around the best integer location
    lo = max(0.0, best_y - 5.0)
    hi = min(L, best_y + 5.0)
    yopt, fmin = golden_section_maximize(lambda yy: h_only(0.0, yy), lo, hi)
    return yopt, fmin


# ---------- Step 2: Tangency points to the level set h(x,y)=f_min ----------
#
# We need points P on the contour satisfying:
#   1) h(P) = f_min
#   2) grad h(P) · (O - P) = 0   (line from O to P is tangent to contour)
#
# Solve by Newton in 2 variables, using finite-difference Jacobian.
#


def newton_tangent_point(origin, fmin, x0, y0, max_iter=120):
    ox, oy = origin
    x, y = float(x0), float(y0)

    def F(xx, yy):
        hh, hx, hy = h_and_grad(xx, yy)
        f1 = hh - fmin
        f2 = hx * (ox - xx) + hy * (oy - yy)
        return f1, f2

    for _ in range(max_iter):
        f1, f2 = F(x, y)
        if abs(f1) < 1e-10 and abs(f2) < 1e-8:
            return x, y

        epsx = 1e-6 * max(1.0, abs(x))
        epsy = 1e-6 * max(1.0, abs(y))

        fpx1, fpx2 = F(x + epsx, y)
        fmx1, fmx2 = F(x - epsx, y)
        dF1dx = (fpx1 - fmx1) / (2.0 * epsx)
        dF2dx = (fpx2 - fmx2) / (2.0 * epsx)

        fpy1, fpy2 = F(x, y + epsy)
        fmy1, fmy2 = F(x, y - epsy)
        dF1dy = (fpy1 - fmy1) / (2.0 * epsy)
        dF2dy = (fpy2 - fmy2) / (2.0 * epsy)

        det = dF1dx * dF2dy - dF1dy * dF2dx
        if abs(det) < 1e-18:
            # random tiny jitter to escape near-singularity
            x += (random.random() - 0.5) * 1e-3
            y += (random.random() - 0.5) * 1e-3
            continue

        # Solve J * [dx,dy] = -F
        dx = (-f1 * dF2dy + f2 * dF1dy) / det
        dy = (-dF1dx * f2 + dF2dx * f1) / det

        # Damping/line-search
        base = abs(f1) + abs(f2)
        lam = 1.0
        for _ in range(25):
            xn = x + lam * dx
            yn = y + lam * dy
            if not (0.0 <= xn <= L and 0.0 <= yn <= L):
                lam *= 0.5
                continue
            nf1, nf2 = F(xn, yn)
            if abs(nf1) + abs(nf2) < base:
                x, y = xn, yn
                break
            lam *= 0.5
        else:
            x, y = x + dx, y + dy

    return x, y


def segment_clear(origin, point, fmin, samples=200):
    """Check if the straight segment origin->point stays in allowed region."""
    ox, oy = origin
    px, py = point
    for i in range(1, samples):
        t = i / samples
        x = ox + (px - ox) * t
        y = oy + (py - oy) * t
        if h_only(x, y) > fmin + 1e-6:
            return False
    return True


def find_accessible_tangent_points(origin, fmin, step=10):
    """
    Coarsely scan a grid for seeds near the contour + tangency condition,
    refine with Newton, keep unique solutions, then filter by segment_clear.
    """
    ox, oy = origin
    seeds = []

    for xi in range(0, 1601, step):
        x = float(xi)
        for yi in range(0, 1601, step):
            y = float(yi)
            hh, hx, hy = h_and_grad(x, y)
            if abs(hh - fmin) > 300.0:
                continue
            tang = hx * (ox - x) + hy * (oy - y)
            if abs(tang) > 400.0:
                continue
            score = abs(hh - fmin) + abs(tang) / 10.0
            seeds.append((score, x, y))

    seeds.sort()
    # Take a modest number of best seeds and spread them out
    picked = []
    for score, x, y in seeds[:500]:
        if all((x - px) ** 2 + (y - py) ** 2 > 400.0 for _, px, py in picked):
            picked.append((score, x, y))

    solutions = []
    for _, sx, sy in picked:
        rx, ry = newton_tangent_point(origin, fmin, sx, sy)
        # uniqueness filter
        if all((rx - ux) ** 2 + (ry - uy) ** 2 > 1e-6 for ux, uy in solutions):
            solutions.append((rx, ry))

    # keep only those reachable by a straight segment in free space
    reachable = [(x, y) for (x, y) in solutions if segment_clear(origin, (x, y), fmin)]
    return reachable


# ---------- Step 3: Arc length along the contour between two points ----------
#
# We integrate along the implicit curve h(x,y)=f_min using an arc-length
# parametrization:
#   d/ds (x,y) = T = perpendicular(grad h) / ||grad h||
#
# Use RK4 and periodically "project" back to the level set to prevent drift.


def project_to_level(x, y, fmin):
    """Project (x,y) to the level set h(x,y)=fmin using a few Newton steps."""
    for _ in range(3):
        hh, hx, hy = h_and_grad(x, y)
        F = hh - fmin
        denom = hx * hx + hy * hy
        if denom == 0.0:
            break
        x -= F * hx / denom
        y -= F * hy / denom
    return x, y


def tangent_unit(x, y, fmin, direction):
    """Unit tangent vector to the level set curve at (x,y)."""
    _, hx, hy = h_and_grad(x, y)
    n = math.hypot(hx, hy)
    # Tangent is perpendicular to gradient
    tx = (-hy / n) * direction
    ty = (hx / n) * direction
    return tx, ty


def rk4_step(x, y, fmin, ds, direction):
    """One RK4 step along the contour with step size ds (arc length)."""

    def f(xx, yy):
        return tangent_unit(xx, yy, fmin, direction)

    k1x, k1y = f(x, y)
    k2x, k2y = f(x + 0.5 * ds * k1x, y + 0.5 * ds * k1y)
    k3x, k3y = f(x + 0.5 * ds * k2x, y + 0.5 * ds * k2y)
    k4x, k4y = f(x + ds * k3x, y + ds * k3y)

    xn = x + ds * (k1x + 2 * k2x + 2 * k3x + k4x) / 6.0
    yn = y + ds * (k1y + 2 * k2y + 2 * k3y + k4y) / 6.0
    return project_to_level(xn, yn, fmin)


def walk_to_target(
    start, target, fmin, direction, ds_init=0.1, max_len=20000.0, tol=1e-10
):
    """
    Follow the contour from 'start' toward 'target' in the given direction.
    Uses adaptive step reduction when close to the target.
    Returns arc length if target is reached.
    """
    x, y = project_to_level(start[0], start[1], fmin)
    tx, ty = target
    s = 0.0
    ds = ds_init

    for _ in range(2_000_000):
        d = math.hypot(x - tx, y - ty)
        if d < tol:
            return s, True

        # step shrinks as we approach target
        ds = min(ds, max(1e-10, d * 0.5))
        xn, yn = rk4_step(x, y, fmin, ds, direction)
        dn = math.hypot(xn - tx, yn - ty)

        # if we're close and stepping makes things worse, reduce step and retry
        if d < 1.0 and dn > d:
            ds *= 0.5
            if ds < 1e-12:
                return s, False
            continue

        x, y = xn, yn
        s += ds
        if s > max_len:
            return s, False

    return s, False


# ---------- Solve ----------


def solve() -> str:
    y_hi, fmin = compute_f_min()

    # Sanity: A and B must be below f_min
    assert h_only(A[0], A[1]) <= fmin + 1e-6
    assert h_only(B[0], B[1]) <= fmin + 1e-6

    # Find accessible tangency points on the relevant contour component
    tangA = find_accessible_tangent_points(A, fmin)
    tangB = find_accessible_tangent_points(B, fmin)

    # We expect 2 each (symmetry), but allow robustness
    if not tangA or not tangB:
        raise RuntimeError("Failed to locate tangent points; numerical issue.")

    best = float("inf")

    for p in tangA:
        for q in tangB:
            # arc length along contour: take shorter of the two directions
            arc1, ok1 = walk_to_target(p, q, fmin, direction=1.0)
            arc2, ok2 = walk_to_target(p, q, fmin, direction=-1.0)
            if not (ok1 and ok2):
                continue
            arc = min(arc1, arc2)

            total = (
                math.hypot(p[0] - A[0], p[1] - A[1])
                + arc
                + math.hypot(q[0] - B[0], q[1] - B[1])
            )
            if total < best:
                best = total

    if not math.isfinite(best):
        raise RuntimeError("No valid path length computed.")

    return f"{best:.3f}"


if __name__ == "__main__":
    print(solve())
