#!/usr/bin/env python3
"""Project Euler 508: Integers in Base i-1

We need B(L) = sum of f(a+bi) over all integers a,b with |a|<=L, |b|<=L,
where f(z) is the number of 1s in the unique base (i-1) representation using digits {0,1}.

This program computes B(10^15) mod 1_000_000_007 without external libraries.
"""

from __future__ import annotations

from functools import lru_cache

MOD = 1_000_000_007

# When a subproblem (region) has at most this many lattice points, we brute-force it.
BRUTE_LIMIT = 4000


def ceil_div(n: int, d: int) -> int:
    """Ceiling division for integers (d>0)."""
    return -(-n // d)


def f_gauss(a: int, b: int) -> int:
    """Count 1s in the base (i-1) representation of a+bi.

    Uses the standard division algorithm in Z[i] with base (i-1).

    Least digit r is 1 iff a and b have different parity.
    Then (a+bi - r) is divisible by (i-1) and we continue with the quotient.
    """
    cnt = 0
    while a != 0 or b != 0:
        if (a ^ b) & 1:
            a -= 1
            cnt += 1
        # Divide by (i - 1)
        a, b = (b - a) // 2, -(a + b) // 2
    return cnt


def to_base_str(a: int, b: int) -> str:
    """Return the base (i-1) representation (digits 0/1) as a string."""
    if a == 0 and b == 0:
        return "0"
    digits = []
    while a != 0 or b != 0:
        r = (a ^ b) & 1
        digits.append("1" if r else "0")
        if r:
            a -= 1
        a, b = (b - a) // 2, -(a + b) // 2
    return "".join(reversed(digits))


def count_rect(x0: int, x1: int, y0: int, y1: int) -> int:
    """Number of integer lattice points in a rectangle [x0..x1] x [y0..y1]."""
    if x0 > x1 or y0 > y1:
        return 0
    return (x1 - x0 + 1) * (y1 - y0 + 1)


def count_parity(lo: int, hi: int, parity: int) -> int:
    """Count integers in [lo,hi] with given parity (0 even, 1 odd)."""
    if lo > hi:
        return 0
    first = lo if (lo & 1) == parity else lo + 1
    if first > hi:
        return 0
    return (hi - first) // 2 + 1


def count_diamond(u0: int, u1: int, v0: int, v1: int) -> int:
    """Number of Gaussian integers (a,b) whose (u,v)=(a+b,a-b) lies in the box.

    The constraints are:
        u0 <= u <= u1
        v0 <= v <= v1
        u and v must have the same parity (so that a=(u+v)/2 and b=(u-v)/2 are integers).
    """
    if u0 > u1 or v0 > v1:
        return 0
    eu = count_parity(u0, u1, 0)
    ou = (u1 - u0 + 1) - eu
    ev = count_parity(v0, v1, 0)
    ov = (v1 - v0 + 1) - ev
    return eu * ev + ou * ov


def rect_to_diamond_bounds(
    x0: int, x1: int, y0: int, y1: int, r: int
) -> tuple[int, int, int, int]:
    """Preimage of rectangle under z = (i-1)q + r, expressed as a diamond in q-space.

    If q = A + Bi, define u = A+B and v = A-B.

    For z = (i-1)q + r, we have:
        Re(z) = -u + r
        Im(z) = v

    So constraints on Re/Im become constraints on (u,v).
    """
    u0 = -x1 + r
    u1 = -x0 + r
    v0 = y0
    v1 = y1
    return u0, u1, v0, v1


def diamond_to_rect_bounds(
    u0: int, u1: int, v0: int, v1: int, r: int
) -> tuple[int, int, int, int]:
    """Preimage of a diamond (u,v)-box under z=(i-1)q+r, as a rectangle in q-space.

    For q = A + Bi, and z = (i-1)q + r:
        u_z = Re(z)+Im(z) = r - 2B
        v_z = Re(z)-Im(z) = r - 2A

    So bounding u_z and v_z separately gives independent bounds on A and B.
    """
    x0 = ceil_div(r - v1, 2)
    x1 = (r - v0) // 2
    y0 = ceil_div(r - u1, 2)
    y1 = (r - u0) // 2
    return x0, x1, y0, y1


def brute_rect(x0: int, x1: int, y0: int, y1: int) -> int:
    s = 0
    for a in range(x0, x1 + 1):
        for b in range(y0, y1 + 1):
            s += f_gauss(a, b)
    return s % MOD


def brute_diamond(u0: int, u1: int, v0: int, v1: int) -> int:
    s = 0
    for u in range(u0, u1 + 1):
        parity = u & 1
        v_start = v0 if (v0 & 1) == parity else v0 + 1
        for v in range(v_start, v1 + 1, 2):
            a = (u + v) // 2
            b = (u - v) // 2
            s += f_gauss(a, b)
    return s % MOD


@lru_cache(maxsize=None)
def sum_rect(x0: int, x1: int, y0: int, y1: int) -> int:
    """Sum of f over rectangle [x0..x1]x[y0..y1] in (a,b) coordinates."""
    if x0 > x1 or y0 > y1:
        return 0
    n = count_rect(x0, x1, y0, y1)
    if n <= BRUTE_LIMIT:
        return brute_rect(x0, x1, y0, y1)

    # Split by least digit r in {0,1} using z = (i-1)q + r.
    d0 = rect_to_diamond_bounds(x0, x1, y0, y1, 0)
    d1 = rect_to_diamond_bounds(x0, x1, y0, y1, 1)

    res = (sum_diamond(*d0) + sum_diamond(*d1)) % MOD
    # Add 1 for each element with r=1.
    res = (res + count_diamond(*d1)) % MOD
    return res


@lru_cache(maxsize=None)
def sum_diamond(u0: int, u1: int, v0: int, v1: int) -> int:
    """Sum of f over a 'diamond' region described by u=a+b and v=a-b bounds."""
    if u0 > u1 or v0 > v1:
        return 0
    n = count_diamond(u0, u1, v0, v1)
    if n <= BRUTE_LIMIT:
        return brute_diamond(u0, u1, v0, v1)

    r0 = diamond_to_rect_bounds(u0, u1, v0, v1, 0)
    r1 = diamond_to_rect_bounds(u0, u1, v0, v1, 1)

    res = (sum_rect(*r0) + sum_rect(*r1)) % MOD
    # Add 1 for each element with r=1.
    res = (res + count_rect(*r1)) % MOD
    return res


def B(L: int) -> int:
    """Compute B(L) mod MOD."""
    sum_rect.cache_clear()
    sum_diamond.cache_clear()
    return sum_rect(-L, L, -L, L) % MOD


def _run_asserts() -> None:
    # Base (i-1) representation examples
    assert to_base_str(11, 24) == "111010110001101"
    assert to_base_str(24, -11) == "110010110011"
    assert to_base_str(8, 0) == "111000000"
    assert to_base_str(-5, 0) == "11001101"
    assert to_base_str(0, 0) == "0"

    # f examples
    assert f_gauss(11, 24) == 9
    assert f_gauss(24, -11) == 7

    # B example
    assert B(500) == 10795060


def main() -> None:
    _run_asserts()
    print(B(10**15))


if __name__ == "__main__":
    main()
