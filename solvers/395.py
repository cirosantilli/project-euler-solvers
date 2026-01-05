#!/usr/bin/env python3
"""
Project Euler 395: Pythagorean Tree
Find the area of the smallest axis-aligned rectangle (parallel to the initial square)
that contains the entire infinite 3-4-5 Pythagorean tree, rounded to 10 decimals.

No external libraries are used (standard library only).
"""

from __future__ import annotations

import math
import heapq
from typing import List, Tuple

Vec = Tuple[float, float]
Node = Tuple[
    Vec, Vec, Vec, float
]  # (origin p, base vector u, outward vector v, side length s)


# ----------------------------
# Basic 2D vector operations
# ----------------------------


def add(a: Vec, b: Vec) -> Vec:
    return (a[0] + b[0], a[1] + b[1])


def sub(a: Vec, b: Vec) -> Vec:
    return (a[0] - b[0], a[1] - b[1])


def mul(a: Vec, k: float) -> Vec:
    return (a[0] * k, a[1] * k)


def cross(a: Vec, b: Vec) -> float:
    return a[0] * b[1] - a[1] * b[0]


def dot(a: Vec, b: Vec) -> float:
    return a[0] * b[0] + a[1] * b[1]


def norm(a: Vec) -> float:
    return math.hypot(a[0], a[1])


def rotate_ccw(a: Vec) -> Vec:
    """Rotate vector 90 degrees counter-clockwise."""
    return (-a[1], a[0])


def square_corners(p: Vec, u: Vec, v: Vec) -> List[Vec]:
    """Return the four corners of the square with origin p and side vectors u and v."""
    return [p, add(p, u), add(add(p, u), v), add(p, v)]


def center(p: Vec, u: Vec, v: Vec) -> Vec:
    """Center of the square."""
    return (p[0] + 0.5 * (u[0] + v[0]), p[1] + 0.5 * (u[1] + v[1]))


# ----------------------------
# Geometry of the 3-4-5 step
# ----------------------------
# In the parent square's local frame:
# - base vector is u, outward vector is v (same length)
# - the triangle is attached to the top side (opposite base)
# - hypotenuse length = s
# - legs have lengths 4/5*s and 3/5*s
#
# With our chosen chirality ("smaller leg on the right"), the right-angle vertex is:
#   C = A + (16/25) u + (12/25) v
# where A is the top-left corner of the square.

K_U = 16.0 / 25.0
K_V = 12.0 / 25.0


def make_child(P: Vec, Q: Vec, R: Vec) -> Node:
    """
    Create a child square whose base is segment P-Q, and which lies on the side of P-Q
    opposite the point R (which is on/inside the parent triangle).

    We choose the direction of the base vector u so that the square interior lies to the
    left of u (v = rotate_ccw(u)). That makes the construction chirality consistent.
    """
    u = sub(Q, P)
    # If R is to the left of directed segment P->Q, then the square would land on the same side.
    # Flip direction to ensure the square lies on the opposite side from R.
    if cross(u, sub(R, P)) > 0.0:
        P, Q = Q, P
        u = (-u[0], -u[1])
    v = rotate_ccw(u)
    s = norm(u)
    return (P, u, v, s)


def children(node: Node) -> Tuple[Node, Node]:
    """
    Return the two child squares produced from this square.
    """
    p, u, v, _s = node

    # Top edge endpoints
    A = add(p, v)  # top-left
    B = add(add(p, u), v)  # top-right

    # Right-angle vertex C of the 3-4-5 triangle
    C = add(A, add(mul(u, K_U), mul(v, K_V)))

    # Left child is attached to leg A-C (length 4/5 of parent)
    left = make_child(A, C, B)

    # Right child is attached to leg B-C (length 3/5 of parent)
    right = make_child(B, C, A)

    return left, right


# ----------------------------
# Pruning bound: disk radius
# ----------------------------
# We use a safe Euclidean radius bound R such that the entire unit tree (rooted at a unit square)
# lies within a disk of radius R around the root square's center.
#
# In the unit construction, the centers of the two child squares lie at distances:
#   d_left  = sqrt(13/10)
#   d_right = sqrt(29)/5
# from the parent center.
#
# If the whole tree fits in radius R around the parent center, then the left child subtree fits in:
#   d_left + (4/5) R
# and the right child subtree fits in:
#   d_right + (3/5) R
#
# Therefore R satisfies:
#   R >= sqrt(2)/2
#   R >= d_left  + (4/5) R
#   R >= d_right + (3/5) R
# Solving yields:
#   R = 5 * d_left = 5 * sqrt(13/10)

RADIUS_UNIT_TREE = 5.0 * math.sqrt(13.0 / 10.0)


def compute_bounding_box(eps: float = 1e-12) -> Tuple[float, float, float, float]:
    """
    Compute (xmin, xmax, ymin, ymax) for the infinite Pythagorean tree.

    Uses branch-and-bound:
    - Each node's entire subtree is contained in a disk centered at the square center
      with radius = (square side length) * RADIUS_UNIT_TREE.
    - If that disk is fully inside the current global bounding box (with a small epsilon),
      the node cannot affect the final bounds and can be skipped.
    """
    root: Node = ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0), 1.0)

    # Sanity checks derived from the "3-4-5 ratio" in the statement.
    # (No explicit numeric test values are provided in the problem statement.)
    A = (0.0, 1.0)
    B = (1.0, 1.0)
    C = (K_U, 1.0 + K_V)
    AB = norm(sub(B, A))
    AC = norm(sub(C, A))
    BC = norm(sub(C, B))
    assert abs(AB - 1.0) < 1e-15
    assert abs(AC - 4.0 / 5.0) < 1e-15
    assert abs(BC - 3.0 / 5.0) < 1e-15
    assert abs(dot(sub(C, A), sub(C, B))) < 1e-15  # right angle at C

    # Initialize global bounds with the root square.
    xs, ys = zip(*square_corners(root[0], root[1], root[2]))
    xmin, xmax = min(xs), max(xs)
    ymin, ymax = min(ys), max(ys)

    # Max-heap by side length (process bigger squares first).
    pq: List[Tuple[float, Node]] = []
    for ch in children(root):
        heapq.heappush(pq, (-ch[3], ch))

    while pq:
        _neg_s, node = heapq.heappop(pq)
        p, u, v, s = node

        cx, cy = center(p, u, v)
        rad = s * RADIUS_UNIT_TREE

        # If this subtree can't improve any bound, skip it.
        if (
            cx + rad <= xmax + eps
            and cx - rad >= xmin - eps
            and cy + rad <= ymax + eps
            and cy - rad >= ymin - eps
        ):
            continue

        # Update global bounds with this square's corners.
        for x, y in square_corners(p, u, v):
            if x < xmin:
                xmin = x
            elif x > xmax:
                xmax = x
            if y < ymin:
                ymin = y
            elif y > ymax:
                ymax = y

        # Expand.
        for ch in children(node):
            heapq.heappush(pq, (-ch[3], ch))

    return xmin, xmax, ymin, ymax


def solve() -> str:
    xmin, xmax, ymin, ymax = compute_bounding_box(eps=1e-12)
    area = (xmax - xmin) * (ymax - ymin)
    return f"{area:.10f}"


if __name__ == "__main__":
    print(solve())
