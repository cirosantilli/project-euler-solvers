#!/usr/bin/env python3
"""Project Euler 422: Sequence of Points on a Hyperbola.

Problem:
  H: 12x^2 + 7xy - 12y^2 = 625
  X = (7, 1)
  P1 = (13, 61/4)
  P2 = (-43/6, -4)
  For i>2: Pi is the other intersection of H with the line through P_{i-1}
          parallel to the line P_{i-2}X.

We need P_n for n = 11^14. If P_n = (a/b, c/d) in lowest terms with
positive denominators, output (a+b+c+d) mod 1_000_000_007.

This implementation uses only the Python standard library.
"""

from __future__ import annotations

import math

MOD = 1_000_000_007
PHI_MOD = MOD - 1  # Fermat exponent modulus (MOD is prime)


# ------------------------------
# Fast doubling Fibonacci
# ------------------------------


def fib_mod(n: int, mod: int) -> tuple[int, int]:
    """Return (F_n, F_{n+1}) modulo mod, with F_0=0, F_1=1."""
    if n == 0:
        return (0, 1)
    a, b = fib_mod(n >> 1, mod)
    # c = F_{2k}, d = F_{2k+1}
    two_b_minus_a = (2 * b - a) % mod
    c = (a * two_b_minus_a) % mod
    d = (a * a + b * b) % mod
    if n & 1:
        return (d, (c + d) % mod)
    return (c, d)


# ------------------------------
# Exact rationals for statement checks
# ------------------------------


class Rat:
    __slots__ = ("n", "d")

    def __init__(self, n: int, d: int = 1) -> None:
        if d == 0:
            raise ZeroDivisionError("denominator is zero")
        if d < 0:
            n, d = -n, -d
        g = math.gcd(abs(n), d)
        self.n = n // g
        self.d = d // g

    def __add__(self, other: "Rat") -> "Rat":
        return Rat(self.n * other.d + other.n * self.d, self.d * other.d)

    def __sub__(self, other: "Rat") -> "Rat":
        return Rat(self.n * other.d - other.n * self.d, self.d * other.d)

    def __mul__(self, other: "Rat") -> "Rat":
        return Rat(self.n * other.n, self.d * other.d)

    def __truediv__(self, other: "Rat") -> "Rat":
        if other.n == 0:
            raise ZeroDivisionError("division by zero")
        return Rat(self.n * other.d, self.d * other.n)

    def inv(self) -> "Rat":
        if self.n == 0:
            raise ZeroDivisionError("division by zero")
        return Rat(self.d, self.n)

    def __neg__(self) -> "Rat":
        return Rat(-self.n, self.d)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Rat):
            return NotImplemented
        return self.n == other.n and self.d == other.d

    def __repr__(self) -> str:
        if self.d == 1:
            return f"{self.n}"
        return f"{self.n}/{self.d}"


def point_exact(n: int) -> tuple[Rat, Rat]:
    """Compute P_n exactly for small n using the simplified recurrence."""
    if n < 1:
        raise ValueError("n must be >= 1")
    # Using the linear change of variables described in README, we get
    # a parameter s_n with:
    #   P(s) = (x, y) = (3s + 4/s, 4s - 3/s)
    # and the recurrence for i>2:
    #   s_i = s_{i-2} / s_{i-1}
    s1 = Rat(4, 1)
    s2 = Rat(-3, 2)
    if n == 1:
        s = s1
    elif n == 2:
        s = s2
    else:
        a, b = s1, s2
        for _ in range(3, n + 1):
            a, b = b, a / b
        s = b

    x = Rat(3, 1) * s + Rat(4, 1) * s.inv()
    y = Rat(4, 1) * s - Rat(3, 1) * s.inv()
    return x, y


# ------------------------------
# Modular solver (works for huge n)
# ------------------------------


def solve_mod(n: int) -> int:
    """Return (a+b+c+d) mod MOD for P_n = (a/b, c/d) reduced."""

    # Base cases (only needed for completeness / small tests)
    if n == 1:
        # P1 = (13, 61/4)
        a, b = 13, 1
        c, d = 61, 4
        return (a + b + c + d) % MOD
    if n == 2:
        # P2 = (-43/6, -4)
        a, b = -43, 6
        c, d = -4, 1
        g = math.gcd(abs(a), b)
        a //= g
        b //= g
        if b < 0:
            a, b = -a, -b
        g = math.gcd(abs(c), d)
        c //= g
        d //= g
        if d < 0:
            c, d = -c, -d
        return (a + b + c + d) % MOD

    # For n>=3 we use:
    #   s_n = (-1)^{F_{n-1}} * 2^{E} / 3^{F}  (if n odd)
    #   s_n = (-1)^{F_{n-1}} * 3^{F} / 2^{E}  (if n even)
    # where
    #   F = F_{n-1}
    #   E = F_n + F_{n-2}
    # and (x,y) = ( (3N^2+4D^2)/(ND), (4N^2-3D^2)/(ND) ) for s=N/D.

    Fn, Fn1 = fib_mod(n, PHI_MOD)  # (F_n, F_{n+1}) mod (MOD-1)
    Fnm1 = (Fn1 - Fn) % PHI_MOD
    Fnm2 = (Fn - Fnm1) % PHI_MOD

    # sign = (-1)^{F_{n-1}}
    Fn_minus1_parity = fib_mod(n - 1, 2)[0]
    sign = -1 if Fn_minus1_parity == 1 else 1

    E = (Fn + Fnm2) % PHI_MOD
    F = Fnm1

    if n & 1:
        # n odd: s = sign * 2^E / 3^F
        N_abs = pow(2, E, MOD)
        D = pow(3, F, MOD)
        gx, gy = 12, 1
    else:
        # n even: s = sign * 3^F / 2^E
        N_abs = pow(3, F, MOD)
        D = pow(2, E, MOD)
        gx, gy = 1, 12

    N = N_abs if sign == 1 else (MOD - N_abs)

    N2 = (N_abs * N_abs) % MOD
    D2 = (D * D) % MOD

    num_x = (3 * N2 + 4 * D2) % MOD
    num_y = (4 * N2 - 3 * D2) % MOD
    den = (N * D) % MOD  # includes sign

    # Make denominators positive by multiplying numerator+denominator by sign.
    if sign == -1:
        num_x = (-num_x) % MOD
        num_y = (-num_y) % MOD
        den = (-den) % MOD

    inv_gx = pow(gx, MOD - 2, MOD)
    inv_gy = pow(gy, MOD - 2, MOD)

    a = (num_x * inv_gx) % MOD
    b = (den * inv_gx) % MOD
    c = (num_y * inv_gy) % MOD
    d = (den * inv_gy) % MOD

    return (a + b + c + d) % MOD


def _run_statement_asserts() -> None:
    # Points given in the statement
    assert point_exact(1) == (Rat(13, 1), Rat(61, 4))
    assert point_exact(2) == (Rat(-43, 6), Rat(-4, 1))

    assert point_exact(3) == (Rat(-19, 2), Rat(-229, 24))
    assert point_exact(4) == (Rat(1267, 144), Rat(-37, 12))
    assert point_exact(7) == (
        Rat(17194218091, 143327232),
        Rat(274748766781, 1719926784),
    )

    # The statement's example modulo answer
    assert solve_mod(7) == 806236837


def main() -> None:
    _run_statement_asserts()
    n = pow(11, 14)
    print(solve_mod(n))


if __name__ == "__main__":
    main()
