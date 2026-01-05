#!/usr/bin/env python3
"""Project Euler 337: Totient Stairstep Sequences

We count sequences {a1, a2, ..., an} such that:
  * a1 = 6
  * for all i: φ(ai) < φ(ai+1) < ai < ai+1

Let S(N) be the number of such sequences with an <= N.
We need S(20_000_000) mod 1e8.

No external libraries are used.
"""

from __future__ import annotations

from array import array
import sys


MOD_DEFAULT = 100_000_000
N_DEFAULT = 20_000_000


def compute_phi(n: int) -> array:
    """Compute Euler's totient φ(k) for all 0 <= k <= n (linear sieve).

    Returns an array('I') where result[k] == φ(k) (with φ(0)=0, φ(1)=1).
    """
    phi = array("I", [0]) * (n + 1)
    primes = array("I")
    if n >= 1:
        phi[1] = 1

    for i in range(2, n + 1):
        phi_i = phi[i]
        if phi_i == 0:
            phi_i = i - 1
            phi[i] = phi_i
            primes.append(i)

        # Linear sieve transition
        for p in primes:
            ip = i * p
            if ip > n:
                break
            if i % p == 0:
                phi[ip] = phi_i * p
                break
            else:
                phi[ip] = phi_i * (p - 1)

    return phi


def solve(n: int, mod: int | None = MOD_DEFAULT) -> int:
    """Compute S(n).

    If mod is None, returns the exact value (only practical for small n).
    Otherwise returns S(n) modulo mod.
    """
    if n < 6:
        return 0

    phi = compute_phi(n)

    # Fenwick tree (BIT) storing a difference array over totient-values:
    # after processing all a < current i, query(t) gives:
    #   sum_{a < i, φ(a) < t < a} f[a]
    if mod is None:
        bit = [0] * (n + 1)

        def add(idx: int, delta: int) -> None:
            if delta == 0:
                return
            while idx <= n:
                bit[idx] += delta
                idx += idx & -idx

        def query(idx: int) -> int:
            s = 0
            while idx > 0:
                s += bit[idx]
                idx -= idx & -idx
            return s

        ans = 0
        for i in range(2, n + 1):
            t = phi[i]
            f = 1 if i == 6 else query(t)
            ans += f
            if f:
                l = t + 1
                if l <= i - 1:
                    add(l, f)
                    add(i, -f)  # ends at i-1, so subtract at (i-1)+1 == i
        return ans

    MOD = mod
    bit = array("I", [0]) * (n + 1)

    def add_mod(idx: int, delta: int) -> None:
        if delta == 0:
            return
        delta %= MOD
        if delta == 0:
            return
        while idx <= n:
            v = bit[idx] + delta
            if v >= MOD:
                v -= MOD
            bit[idx] = v
            idx += idx & -idx

    def query_mod(idx: int) -> int:
        s = 0
        while idx > 0:
            s += bit[idx]
            if s >= MOD:
                s -= MOD
            idx -= idx & -idx
        return s

    ans = 0
    for i in range(2, n + 1):
        t = phi[i]
        f = 1 if i == 6 else query_mod(t)
        ans += f
        if ans >= MOD:
            ans -= MOD

        if f:
            l = t + 1
            if l <= i - 1:
                add_mod(l, f)
                add_mod(i, -f)

    return ans % MOD


def _run_tests() -> None:
    # Test values from the problem statement:
    assert solve(10, mod=None) == 4
    assert solve(100, mod=None) == 482073668
    assert solve(10_000, mod=MOD_DEFAULT) == 73808307


def main() -> None:
    _run_tests()
    n = N_DEFAULT
    if len(sys.argv) >= 2:
        n = int(sys.argv[1].replace("_", ""))
    print(solve(n, mod=MOD_DEFAULT))


if __name__ == "__main__":
    main()
