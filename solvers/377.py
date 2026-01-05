#!/usr/bin/env python3
"""
Project Euler 377: Sum of digits - experience #13

We need:
  f(n) = sum of all positive integers (base 10) that:
         - contain no digit 0
         - have digit sum n
Answer: last 9 digits of sum_{i=1..17} f(13^i)

No external libraries are used.
"""

MOD = 10**9


def _build_transition_matrix(mod: int = MOD):
    """
    State vector V(n) (length 18):
      [ g(n), g(n-1), ..., g(n-8),  f(n), f(n-1), ..., f(n-8) ]^T
    where
      g(n) = sum over all valid digit-sequences with digit-sum n of 10^{len(sequence)}
      f(n) = sum over all valid digit-sequences with digit-sum n of the corresponding base-10 number
    """
    size = 18
    M = [[0] * size for _ in range(size)]

    # g(n+1) = 10 * (g(n) + g(n-1) + ... + g(n-8))
    for j in range(9):
        M[0][j] = 10 % mod

    # shift g: g(n), g(n-1), ... down the vector
    for i in range(1, 9):
        M[i][i - 1] = 1

    # f(n+1) = (f(n) + ... + f(n-8)) + (1*g(n) + 2*g(n-1) + ... + 9*g(n-8))
    for j in range(9):
        M[9][j] = j + 1  # coefficients for g(n), g(n-1), ...
    for j in range(9):
        M[9][9 + j] = 1  # coefficients for f(n), f(n-1), ...

    # shift f
    for i in range(10, 18):
        M[i][i - 1] = 1

    return M


def _mat_mul(A, B, mod: int = MOD):
    """Matrix multiplication (small fixed size, optimized with sparse-ish checks)."""
    n = len(A)
    m = len(B[0])
    k = len(B)
    res = [[0] * m for _ in range(n)]
    for i in range(n):
        Ai = A[i]
        Ri = res[i]
        for t in range(k):
            a = Ai[t]
            if a:
                Bt = B[t]
                for j in range(m):
                    Ri[j] = (Ri[j] + a * Bt[j]) % mod
    return res


def _mat_vec(A, v, mod: int = MOD):
    """Matrix-vector multiplication."""
    n = len(A)
    res = [0] * n
    for i in range(n):
        s = 0
        row = A[i]
        for j in range(len(v)):
            s = (s + row[j] * v[j]) % mod
        res[i] = s
    return res


class _RecurrenceSolver:
    """Precomputes powers of the transition matrix to answer f(n) quickly."""

    __slots__ = ("powers", "v0", "mod")

    def __init__(self, mod: int = MOD):
        self.mod = mod
        M = _build_transition_matrix(mod)
        self.powers = [M]
        # Enough for n up to 13^17 (< 2^64)
        for _ in range(1, 64):
            self.powers.append(_mat_mul(self.powers[-1], self.powers[-1], mod))

        # Base state V(0):
        # g(0) = 1 (empty sequence), g(neg) = 0
        # f(0) = 0, f(neg) = 0
        self.v0 = [0] * 18
        self.v0[0] = 1

    def f(self, n: int) -> int:
        """Return f(n) modulo mod."""
        v = self.v0[:]  # M^0 * V(0)
        bit = 0
        while n:
            if n & 1:
                v = _mat_vec(self.powers[bit], v, self.mod)
            n >>= 1
            bit += 1
        return v[9]  # f(n)


def euler377() -> int:
    solver = _RecurrenceSolver(MOD)

    # Test value from the problem statement:
    assert solver.f(5) == 17891

    total = 0
    for i in range(1, 18):
        total = (total + solver.f(13**i)) % MOD
    return total


def main():
    print(euler377())


if __name__ == "__main__":
    main()
