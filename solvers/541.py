#!/usr/bin/env python3
"""
Project Euler 541: Divisibility of Harmonic Number Denominators

We want M(p) = largest n such that the reduced denominator of H_n is NOT divisible by p.

No external (non-stdlib) libraries are used.
"""

from __future__ import annotations

from functools import lru_cache
from fractions import Fraction


def inv_mod(a: int, mod: int) -> int:
    """Modular inverse of a modulo mod (gcd(a,mod)=1) using extended Euclid."""
    a %= mod
    t, newt = 0, 1
    r, newr = mod, a
    while newr:
        q = r // newr
        t, newt = newt, t - q * newt
        r, newr = newr, r - q * newr
    if r != 1:
        raise ValueError("inverse does not exist")
    return t % mod


class HarmonicDenominatorSolver:
    """
    Solver for M(p) using p-adic techniques and a tree lift on base-p digits.

    For a fixed p we build sets A_e (e>=1) of integers m such that
        V_e(m) := sum_{t=1..e} p^{e-t} * U( floor(m / p^{t-1}) )  == 0 (mod p^e),
    where U(N) = sum_{1<=k<=N, p∤k} k^{-1} (mod p^s) (unit inverses sum).

    If m ∈ A_e, then every n in the block [p*m, p*m + (p-1)] has denominator not divisible by p
    (when n lies in the corresponding p-adic magnitude range). In particular, the maximum
    in that block is p*m + (p-1).
    """

    def __init__(self, p: int):
        self.p = p
        # We will need mod powers up to e+1; for p=137 this tops out at 8.
        self.S_MAX = (
            12  # safe small cap; computations are tiny for p<=137 and S_MAX<=12
        )

        # Binomial coefficients up to 12 (more than enough here)
        self._binom = [[0] * (self.S_MAX + 1) for _ in range(self.S_MAX + 1)]
        for n in range(self.S_MAX + 1):
            self._binom[n][0] = self._binom[n][n] = 1
            for k in range(1, n):
                self._binom[n][k] = self._binom[n - 1][k - 1] + self._binom[n - 1][k]

        # prefix_pows[r][k] = sum_{b=0}^{r-1} b^k  for r=0..p, k=0..S_MAX
        self._prefix_pows = [[0] * (self.S_MAX + 1) for _ in range(self.p + 1)]
        for r in range(1, self.p + 1):
            b = r - 1
            row = self._prefix_pows[r]
            prev = self._prefix_pows[r - 1]
            for k in range(self.S_MAX + 1):
                row[k] = prev[k] + (b**k)

        # digit_pows[k] = sum_{b=0}^{p-1} b^k
        self._digit_pows = [self._prefix_pows[self.p][k] for k in range(self.S_MAX + 1)]

        # Map residue -> list of digits a in [0..p-1] such that H_a (mod p) == residue,
        # where H_a = sum_{j=1..a} 1/j in F_p (a<p).
        self._ha_to_digits = self._build_ha_digit_map()

    def _build_ha_digit_map(self) -> dict[int, list[int]]:
        p = self.p
        invs = [0] * p
        for a in range(1, p):
            invs[a] = inv_mod(a, p)
        ha = [0] * p
        s = 0
        for a in range(1, p):
            s = (s + invs[a]) % p
            ha[a] = s
        ha[0] = 0

        mp: dict[int, list[int]] = {}
        for a, v in enumerate(ha):
            mp.setdefault(v, []).append(a)
        return mp

    @lru_cache(maxsize=None)
    def _pow_sum(self, m: int, q: int, s: int) -> int:
        """
        Compute S_m(q) = sum_{i=0}^{q-1} i^m modulo p^s using base-p recursion.
        This avoids divisions, so it works even when p divides denominators in Faulhaber formulas.
        """
        if q <= 0:
            return 0
        mod = self.p**s
        p = self.p
        if q <= p:
            return self._prefix_pows[q][m] % mod

        Q, R = divmod(q, p)
        res = 0

        # Full blocks: sum_{a=0..Q-1} sum_{b=0..p-1} (a p + b)^m
        for t in range(m + 1):
            # (a p + b)^m = sum_{t} C(m,t) (a p)^t b^{m-t}
            res = (
                res
                + self._binom[m][t]
                * pow(p, t, mod)
                * self._pow_sum(t, Q, s)
                * (self._digit_pows[m - t] % mod)
            ) % mod

        # Remainder: sum_{b=0..R-1} (Q p + b)^m
        base = (Q * p) % mod
        for t in range(m + 1):
            res = (
                res
                + self._binom[m][t]
                * pow(base, t, mod)
                * (self._prefix_pows[R][m - t] % mod)
            ) % mod

        return res

    @lru_cache(maxsize=None)
    def _Cm(self, s: int) -> tuple[int, ...]:
        """
        C_m = sum_{j=1..p-1} j^{-(m+1)} modulo p^s, for m=0..s-1.
        """
        mod = self.p**s
        p = self.p
        out = []
        for m in range(s):
            sm = 0
            for j in range(1, p):
                invj = inv_mod(j, mod)
                sm = (sm + pow(invj, m + 1, mod)) % mod
            out.append(sm)
        return tuple(out)

    @lru_cache(maxsize=None)
    def unit_inverse_sum(self, N: int, s: int) -> int:
        """
        U(N) = sum_{1<=k<=N, p∤k} k^{-1} modulo p^s.

        Computed by splitting into blocks of length p and using the p-adic series:
            1/(i p + j) = sum_{m=0..s-1} (-1)^m * i^m * p^m * j^{-(m+1)}   (mod p^s).
        """
        if N <= 0:
            return 0
        p = self.p
        mod = p**s
        q, r = divmod(N, p)
        Cm = self._Cm(s)

        total = 0
        if q:
            for m in range(s):
                Sm = self._pow_sum(m, q, s)
                term = (pow(p, m, mod) * Sm) % mod
                term = (term * Cm[m]) % mod
                if m & 1:
                    term = (-term) % mod
                total = (total + term) % mod

        # Tail in the last partial block (at i=q)
        base = q * p
        for j in range(1, r + 1):
            if j % p == 0:
                continue
            total = (total + inv_mod(base + j, mod)) % mod

        return total

    @lru_cache(maxsize=None)
    def V(self, e: int, m: int, mod_power: int) -> int:
        """
        Compute V_e(m) modulo p^{mod_power}.
        We use mod_power=e for membership test, and mod_power=e+1 for lifting.
        """
        p = self.p
        mod = p**mod_power
        val = 0
        div = 1
        for t in range(1, e + 1):
            coeff = p ** (e - t)
            N = m // div
            val = (val + coeff * self.unit_inverse_sum(N, mod_power)) % mod
            div *= p
        return val

    def M(self) -> int:
        """Compute M(p)."""
        p = self.p

        # p=3 is tiny; brute force is simple and avoids edge-cases for very small primes.
        if p == 3:
            H = Fraction(0, 1)
            best = 0
            for n in range(1, 500):  # plenty; M(3)=68
                H += Fraction(1, n)
                if H.denominator % 3 != 0:
                    best = n
            return best

        # Base: all n < p are valid, so current best is p-1.
        best = p - 1

        # Level e=1: find all m in [1..p-1] with H_m ≡ 0 (mod p)
        # Equivalent to V_1(m) ≡ 0 (mod p) since V_1(m)=U(m) mod p.
        A = self._ha_to_digits.get(0, [])
        A = [m for m in A if 1 <= m < p]  # ignore m=0

        e = 1
        while A:
            best = max(best, p * max(A) + (p - 1))

            # Lift A_e -> A_{e+1}
            next_set = set()
            for q in A:
                # Need one extra p-adic digit of V_e(q) to decide children.
                val = self.V(e, q, e + 1)  # modulo p^{e+1}
                d = (val // (p**e)) % p  # the (e-th) base-p digit of V_e(q)
                target = (-d) % p
                for a in self._ha_to_digits.get(target, []):
                    next_set.add(q * p + a)

            A = sorted(next_set)
            e += 1
            # Safety cap; for p=137 it stops naturally at e=8.
            if e > 30:
                break

        return best


def compute_M(p: int) -> int:
    return HarmonicDenominatorSolver(p).M()


def main() -> None:
    # Test values from the problem statement:
    assert compute_M(3) == 68
    assert compute_M(7) == 719102

    print(compute_M(137))


if __name__ == "__main__":
    main()
