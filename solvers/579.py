#!/usr/bin/env python3
"""
Project Euler 579: Lattice Points in Lattice Cubes

We count all lattice cubes whose vertices lie in the box [0..n]^3 and sum the
number of lattice points in each cube.

Key ideas implemented:
- Parametrise lattice cube orientations using integer quaternions (Euler–Rodrigues).
- For each cube orientation (edge vectors u,v,w), number of translations in box is:
      (n - span_x + 1)(n - span_y + 1)(n - span_z + 1)
  where span_x = |u_x|+|v_x|+|w_x| etc.
- Lattice point count in cube (including boundary) for side length m and column gcds g1,g2,g3:
      m^3 + (m+1)(g1+g2+g3) + 1
- Enumerate "primary" primitive quaternions for odd norms, which gives one representative per
  right-unit orbit for odd norms (standard quaternion arithmetic result).
- Deduplicate orientations defensively (hash of canonicalised |u|,|v|,|w|).

The required output is S(5000) mod 1e9.
"""

from math import gcd, isqrt

MOD = 10**9


# ---------- power sums up to k=6 (Faulhaber closed forms) ----------
def power_sums_upto_6(n: int):
    """Return list S[k] = sum_{t=1..n} t^k for k=0..6."""
    if n <= 0:
        return [0] * 7
    nn = n
    n1 = nn + 1
    s0 = nn
    s1 = nn * n1 // 2
    s2 = nn * n1 * (2 * nn + 1) // 6
    s3 = s1 * s1
    s4 = nn * n1 * (2 * nn + 1) * (3 * nn * nn + 3 * nn - 1) // 30
    s5 = nn * nn * n1 * n1 * (2 * nn * nn + 2 * nn - 1) // 12
    # sum t^6 = n(n+1)(2n+1)(3n^4+6n^3-3n+1)/42
    s6 = nn * n1 * (2 * nn + 1) * (3 * nn**4 + 6 * nn**3 - 3 * nn + 1) // 42
    return [s0, s1, s2, s3, s4, s5, s6]


# ---------- quaternion -> orthogonal integer matrix ----------
def cube_matrix_from_quaternion(a: int, b: int, c: int, d: int):
    """
    Euler–Rodrigues construction:
    For quaternion q = a + bi + cj + dk, norm m = a^2+b^2+c^2+d^2.
    The 3x3 matrix has columns u,v,w that are pairwise orthogonal
    and each has squared length m^2 (so cube side length is m).
    """
    aa = a * a
    bb = b * b
    cc = c * c
    dd = d * d

    u0 = aa + bb - cc - dd
    u1 = 2 * (b * c - a * d)
    u2 = 2 * (b * d + a * c)

    v0 = 2 * (b * c + a * d)
    v1 = aa - bb + cc - dd
    v2 = 2 * (c * d - a * b)

    w0 = 2 * (b * d - a * c)
    w1 = 2 * (c * d + a * b)
    w2 = aa - bb - cc + dd

    return (u0, u1, u2), (v0, v1, v2), (w0, w1, w2)


def global_gcd_9(u, v, w):
    g = 0
    for x in u:
        g = gcd(g, abs(x))
    for x in v:
        g = gcd(g, abs(x))
    for x in w:
        g = gcd(g, abs(x))
    return g


def col_gcd(vec):
    return gcd(gcd(abs(vec[0]), abs(vec[1])), abs(vec[2]))


# ---------- canonical orientation key (defensive dedupe) ----------
def canonical_orientation_key(u, v, w):
    """
    Canonicalise an orientation by:
    - take abs of all entries (sign doesn't affect placement spans or gcds)
    - sort columns lexicographically
    This is enough to avoid accidental duplicates in enumeration.
    """
    cols = [
        (abs(u[0]), abs(u[1]), abs(u[2])),
        (abs(v[0]), abs(v[1]), abs(v[2])),
        (abs(w[0]), abs(w[1]), abs(w[2])),
    ]
    cols.sort()
    return tuple(cols[0] + cols[1] + cols[2])


# ---------- enumerate primary primitive quaternions (odd norms) ----------
def generate_primary_odd_quaternions(max_norm: int):
    """
    Generate all primary primitive integer quaternions (a,b,c,d) with odd norm <= max_norm.

    For odd norm:
      - if norm ≡ 1 (mod 4), quaternion has exactly one odd coordinate.
      - if norm ≡ 3 (mod 4), quaternion has exactly one even coordinate.
    Primary condition for S1-type (real part parity differs from others) is:
      - norm ≡ 1 (mod 4): a odd, b,c,d even
      - norm ≡ 3 (mod 4): a even, b,c,d odd
    Plus primary selector: a+b+c+d ≡ 1 (mod 4)
    Plus primitive: gcd(a,b,c,d)=1
    """
    limit = isqrt(max_norm)

    # Precompute relevant ordered pairs by parity classes.
    ab1 = []  # a odd, b even
    cd1 = []  # c even, d even
    ab3 = []  # a even, b odd
    cd3 = []  # c odd, d odd

    for x in range(-limit, limit + 1):
        x2 = x * x
        for y in range(-limit, limit + 1):
            s = x2 + y * y
            if s > max_norm:
                continue
            xo = x & 1
            yo = y & 1
            if xo == 1 and yo == 0:
                ab1.append((x, y, s))
            if xo == 0 and yo == 1:
                ab3.append((x, y, s))
            if xo == 0 and yo == 0:
                cd1.append((x, y, s))
            if xo == 1 and yo == 1:
                cd3.append((x, y, s))

    ab1.sort(key=lambda t: t[2])
    ab3.sort(key=lambda t: t[2])
    cd1.sort(key=lambda t: t[2])
    cd3.sort(key=lambda t: t[2])

    # Case norm ≡ 1 (mod 4)
    for a, b, s in ab1:
        for c, d, t in cd1:
            m = s + t
            if m > max_norm:
                break
            if ((a + b + c + d) & 3) != 1:
                continue
            if gcd(gcd(a, b), gcd(c, d)) != 1:
                continue
            yield a, b, c, d, m

    # Case norm ≡ 3 (mod 4)
    for a, b, s in ab3:
        for c, d, t in cd3:
            m = s + t
            if m > max_norm:
                break
            if ((a + b + c + d) & 3) != 1:
                continue
            if gcd(gcd(a, b), gcd(c, d)) != 1:
                continue
            yield a, b, c, d, m


# ---------- main solver for given n ----------
def compute_C_S(n: int):
    """
    Compute C(n) and S(n) exactly (big integers).
    """
    seen = set()  # defensive dedupe of orientations

    C_total = 0
    S_total = 0

    N1 = n + 1

    for a, b, c, d, m in generate_primary_odd_quaternions(n):
        # Build orientation
        u, v, w = cube_matrix_from_quaternion(a, b, c, d)

        # Reduce by global gcd (some quaternions produce scaled matrices)
        g = global_gcd_9(u, v, w)
        if g != 1:
            u = (u[0] // g, u[1] // g, u[2] // g)
            v = (v[0] // g, v[1] // g, v[2] // g)
            w = (w[0] // g, w[1] // g, w[2] // g)
            m0 = m // g
        else:
            m0 = m

        # Side length must be <= n to fit anything
        if m0 > n:
            continue

        # Canonical key to avoid duplicates
        key = canonical_orientation_key(u, v, w)
        if key in seen:
            continue
        seen.add(key)

        sx = abs(u[0]) + abs(v[0]) + abs(w[0])
        sy = abs(u[1]) + abs(v[1]) + abs(w[1])
        sz = abs(u[2]) + abs(v[2]) + abs(w[2])

        max_span = sx
        if sy > max_span:
            max_span = sy
        if sz > max_span:
            max_span = sz

        if max_span > n:
            continue

        # Column gcds (for lattice point formula)
        gsum = col_gcd(u) + col_gcd(v) + col_gcd(w)

        # Scaling factor t can be applied: edges -> t*edges
        # Valid t: t*max_span <= n
        T = n // max_span
        if T <= 0:
            continue

        # placements(t) = (N1 - sx*t)(N1 - sy*t)(N1 - sz*t)
        ssum = sx + sy + sz
        spair = sx * sy + sx * sz + sy * sz
        strip = sx * sy * sz

        c0 = N1 * N1 * N1
        c1 = - (N1 * N1 * ssum)
        c2 = N1 * spair
        c3 = - strip

        # points(t) = (m0^3)*t^3 + (gsum*m0)*t^2 + gsum*t + 1
        m0_2 = m0 * m0
        m0_3 = m0_2 * m0
        p0 = 1
        p1 = gsum
        p2 = gsum * m0
        p3 = m0_3

        # Convolution to degree 6
        # coeff[k] for t^k
        coeff0 = c0 * p0
        coeff1 = c0 * p1 + c1 * p0
        coeff2 = c0 * p2 + c1 * p1 + c2 * p0
        coeff3 = c0 * p3 + c1 * p2 + c2 * p1 + c3 * p0
        coeff4 = c1 * p3 + c2 * p2 + c3 * p1
        coeff5 = c2 * p3 + c3 * p2
        coeff6 = c3 * p3

        S = power_sums_upto_6(T)
        # sum t^0 is T, we treat as S0 already
        sumC = c0 * S[0] + c1 * S[1] + c2 * S[2] + c3 * S[3]
        sumS = (
            coeff0 * S[0] +
            coeff1 * S[1] +
            coeff2 * S[2] +
            coeff3 * S[3] +
            coeff4 * S[4] +
            coeff5 * S[5] +
            coeff6 * S[6]
        )

        C_total += sumC
        S_total += sumS

    return C_total, S_total


def solve(n: int):
    _, s = compute_C_S(n)
    return s % MOD


def _run_asserts():
    # Asserts from the problem statement
    C1, S1 = compute_C_S(1)
    assert C1 == 1 and S1 == 8

    C2, S2 = compute_C_S(2)
    assert C2 == 9 and S2 == 91

    C4, S4 = compute_C_S(4)
    assert C4 == 100 and S4 == 1878

    C5, S5 = compute_C_S(5)
    assert C5 == 229 and S5 == 5832

    C10, S10 = compute_C_S(10)
    assert C10 == 4469 and S10 == 387003

    C50, S50 = compute_C_S(50)
    assert C50 == 8154671 and S50 == 29948928129


def main():
    _run_asserts()
    print(solve(5000))


if __name__ == "__main__":
    main()

