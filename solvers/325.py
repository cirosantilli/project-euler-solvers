"""Project Euler 325: Stone Game II

We need S(N) = sum_{(x,y) losing, 0<x<y<=N} (x+y), and finally S(10^16) mod 7^10.

Key facts used (proved in many references for the classic Euclid game):
    A position (a,b) with 0<a<b is losing for the player to move
    iff b/a < phi, where phi = (1+sqrt(5))/2.

That turns the game into a counting/summation problem over Beatty sequences.

The implementation below avoids floating point entirely and runs in O(log N).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isqrt


PHI_MOD = 7**10


def _isqrt5nn(n: int) -> int:
    """Return floor(n*sqrt(5)) exactly using integer arithmetic."""
    return isqrt(5 * n * n)


def floor_phi_mul(n: int) -> int:
    """Return floor(n * phi) exactly, where phi = (1+sqrt(5))/2."""
    if n <= 0:
        return 0
    t = _isqrt5nn(n)
    return (n + t) // 2


def floor_div_phi(n: int) -> int:
    """Return floor(n / phi) exactly."""
    if n <= 0:
        return 0
    t = _isqrt5nn(n)
    return (t - n) // 2


@dataclass
class BeattySums:
    """Fast summatory functions for a_n = floor(n*phi).

    Provides:
        A(n) = sum_{k=1..n} a_k
        B(n) = sum_{k=1..n} a_k^2
        H(n) = sum_{k=1..n} k*a_k

    All values are returned modulo `mod`.
    """

    mod: int

    def __post_init__(self) -> None:
        self.inv2 = pow(2, -1, self.mod)
        self.inv6 = pow(6, -1, self.mod)
        self._A = {0: 0}
        self._B = {0: 0}
        self._H = {0: 0}

    def tri(self, n: int) -> int:
        """1+2+...+n modulo mod."""
        return (n % self.mod) * ((n + 1) % self.mod) % self.mod * self.inv2 % self.mod

    def sqsum(self, n: int) -> int:
        """1^2+2^2+...+n^2 modulo mod."""
        return (
            (n % self.mod)
            * ((n + 1) % self.mod)
            % self.mod
            * ((2 * n + 1) % self.mod)
            % self.mod
            * self.inv6
            % self.mod
        )

    def A(self, n: int) -> int:
        """A(n) = sum_{k<=n} floor(k*phi) (mod)."""
        if n in self._A:
            return self._A[n]

        t = _isqrt5nn(n)
        m = (n + t) // 2  # floor(n*phi)
        c = (t - n) // 2  # floor(n/phi)

        # Beatty complement recursion:
        # A(n) = T(m) - A(c) - T(c)
        res = (self.tri(m) - self.A(c) - self.tri(c)) % self.mod
        self._A[n] = res
        return res

    def H(self, n: int) -> int:
        """H(n) = sum_{k<=n} k*floor(k*phi) (mod)."""
        if n in self._H:
            return self._H[n]

        c = floor_div_phi(n)
        # Derived via a lattice-point reciprocity for q = 1/phi:
        # H(n) = sum k^2 + c*T(n) - (B(c)+A(c))/2
        res = self.sqsum(n)
        res = (res + (c % self.mod) * self.tri(n)) % self.mod
        res = (res - (self.B(c) + self.A(c)) * self.inv2) % self.mod
        self._H[n] = res
        return res

    def B(self, n: int) -> int:
        """B(n) = sum_{k<=n} floor(k*phi)^2 (mod)."""
        if n in self._B:
            return self._B[n]

        t = _isqrt5nn(n)
        m = (n + t) // 2  # floor(n*phi)
        c = (t - n) // 2  # floor(n/phi)

        # Squares partition recursion (using b_k = floor(k*phi^2) = a_k + k):
        # B(n) = S2(m) - B(c) - 2*H(c) - S2(c)
        res = (self.sqsum(m) - self.B(c) - 2 * self.H(c) - self.sqsum(c)) % self.mod
        self._B[n] = res
        return res


def S_mod(N: int, mod: int = PHI_MOD) -> int:
    """Compute S(N) modulo mod."""
    bs = BeattySums(mod)

    d = floor_div_phi(N)  # threshold where floor(phi*x) reaches N

    # For x <= d:
    #   let t = floor(x/phi), then y_max = x + t and the contribution is
    #   sum_{y=x+1..x+t} (x+y) = 2*x*t + t(t+1)/2.
    A_d = bs.A(d)
    B_d = bs.B(d)
    H_d = bs.H(d)

    sum_t = (A_d - bs.tri(d)) % mod  # sum floor(x/phi)
    sum_xt = (H_d - bs.sqsum(d)) % mod  # sum x*floor(x/phi)
    sum_t2 = (B_d - 2 * H_d + bs.sqsum(d)) % mod  # sum floor(x/phi)^2

    part1 = (2 * sum_xt + (sum_t2 + sum_t) * bs.inv2) % mod

    # For x >= d+1, y ranges all the way to N. This part has a closed form:
    # part2 = (N-d-1) * (N(N+1) - d(d+1)) / 2
    k = (N - d - 1) % mod
    term = ((N % mod) * ((N + 1) % mod) - (d % mod) * ((d + 1) % mod)) % mod
    part2 = k * term % mod * bs.inv2 % mod

    return (part1 + part2) % mod


def S_exact(N: int) -> int:
    """Exact S(N) for small N (used for asserts)."""
    # Reuse the same formulas but with exact integer arithmetic.

    def tri(n: int) -> int:
        return n * (n + 1) // 2

    def sqsum(n: int) -> int:
        return n * (n + 1) * (2 * n + 1) // 6

    memoA = {0: 0}
    memoB = {0: 0}
    memoH = {0: 0}

    def A(n: int) -> int:
        if n in memoA:
            return memoA[n]
        t = _isqrt5nn(n)
        m = (n + t) // 2
        c = (t - n) // 2
        memoA[n] = tri(m) - A(c) - tri(c)
        return memoA[n]

    def H(n: int) -> int:
        if n in memoH:
            return memoH[n]
        c = floor_div_phi(n)
        memoH[n] = sqsum(n) + c * tri(n) - (B(c) + A(c)) // 2
        return memoH[n]

    def B(n: int) -> int:
        if n in memoB:
            return memoB[n]
        t = _isqrt5nn(n)
        m = (n + t) // 2
        c = (t - n) // 2
        memoB[n] = sqsum(m) - B(c) - 2 * H(c) - sqsum(c)
        return memoB[n]

    d = floor_div_phi(N)

    A_d = A(d)
    B_d = B(d)
    H_d = H(d)
    sum_t = A_d - tri(d)
    sum_xt = H_d - sqsum(d)
    sum_t2 = B_d - 2 * H_d + sqsum(d)
    part1 = 2 * sum_xt + (sum_t2 + sum_t) // 2
    part2 = (N - d - 1) * (N * (N + 1) - d * (d + 1)) // 2
    return part1 + part2


def main() -> None:
    # Test values from the problem statement
    assert S_exact(10) == 211
    assert S_exact(10_000) == 230312207313

    print(S_mod(10**16, PHI_MOD))


if __name__ == "__main__":
    main()
