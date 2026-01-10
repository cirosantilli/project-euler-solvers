#!/usr/bin/env python3
"""
Project Euler 530: GCD of Divisors

We define:
  f(n) = sum_{d|n} gcd(d, n/d)
  F(N) = sum_{n=1..N} f(n)

This program computes F(10^15) (or an optional N passed on the command line)
without external libraries.

Key identity used:
  f(n) = sum_{k^2 | n} phi(k) * tau(n / k^2)
where tau is the divisor-counting function and phi is Euler's totient.

Let b(m) be: b(k^2)=phi(k), otherwise 0. Then f = tau * b (Dirichlet convolution).
So:
  F(N) = sum_{i*j <= N} tau(i) * b(j)

We evaluate this double sum using the Dirichlet hyperbola method.
"""

from __future__ import annotations

from array import array
from math import gcd, isqrt
import sys


def f_single(n: int) -> int:
    """Compute f(n) for small n using divisor pairs (used only in asserts)."""
    r = isqrt(n)
    s = 0
    for d in range(1, r + 1):
        if n % d == 0:
            term = gcd(d, n // d)
            if d * d == n:
                s += term
            else:
                s += 2 * term
    return s


def sieve_phi_tau(n: int) -> tuple[array, array]:
    """
    Linear sieve up to n producing:
      - phi[i] = Euler totient
      - tau[i] = number of divisors
    """
    phi = array("I", [0]) * (n + 1)
    tau = array("H", [0]) * (n + 1)
    lp = array("I", [0]) * (n + 1)  # least prime factor
    exp = array("B", [0]) * (n + 1)  # exponent of lp in i
    primes: list[int] = []

    phi[1] = 1
    tau[1] = 1

    for i in range(2, n + 1):
        if lp[i] == 0:
            lp[i] = i
            primes.append(i)
            phi[i] = i - 1
            tau[i] = 2
            exp[i] = 1

        for p in primes:
            ip = i * p
            if ip > n:
                break
            lp[ip] = p
            if i % p == 0:
                # p divides i -> increase exponent
                phi[ip] = phi[i] * p
                e = exp[i] + 1
                exp[ip] = e
                # tau(i) = (e_i+1)*rest, so tau(ip) replaces (e_i+1) with (e_i+2)
                tau[ip] = (tau[i] // (exp[i] + 1)) * (e + 1)
                break
            else:
                # new prime factor
                phi[ip] = phi[i] * (p - 1)
                exp[ip] = 1
                tau[ip] = tau[i] * 2

    return phi, tau


def divisor_summatory(n: int) -> int:
    """
    D(n) = sum_{m<=n} tau(m) = sum_{d<=n} floor(n/d)

    Computed with the classic sqrt formula:
      D(n) = 2*sum_{i=1..isqrt(n)} floor(n/i) - isqrt(n)^2
    """
    s = isqrt(n)
    acc = 0
    for i in range(1, s + 1):
        acc += n // i
    return 2 * acc - s * s


def compute_F(N: int) -> int:
    """
    Compute F(N) using:
      F(N) = sum_{i*j<=N} tau(i) * b(j)
    with b(k^2)=phi(k), otherwise 0, via Dirichlet hyperbola.

    Choose:
      k = floor(sqrt(N))
      l = floor(N / k)

    Then:
      F(N) = sum_{i=1..k} tau(i) * B(N//i)
           + sum_{j=1..l} b(j) * T(N//j)
           - T(k) * B(l)

    where:
      T(x)=sum_{i<=x} tau(i) = D(x)
      B(x)=sum_{j<=x} b(j) = Phi(isqrt(x))
    """
    if N <= 0:
        return 0

    k = isqrt(N)
    l = N // k
    tmax = isqrt(l)  # because b(j) is only nonzero for squares j=t^2<=l

    # Sieve up to k for tau and phi, then build Phi prefix sum (totient summatory).
    phi, tau = sieve_phi_tau(k)

    Phi = array("Q", [0]) * (k + 1)
    running = 0
    for i in range(1, k + 1):
        running += phi[i]
        Phi[i] = running

    # Store phi(t) needed for the square-only second sum, then free the big phi array.
    phi_small = [0] * (tmax + 1)
    for t in range(1, tmax + 1):
        phi_small[t] = phi[t]
    del phi

    # First hyperbola sum and T(k) (=sum_tau) in one pass.
    sum1 = 0
    sum_tau = 0
    for i in range(1, k + 1):
        ti = tau[i]
        sum_tau += ti
        m = isqrt(N // i)
        sum1 += ti * Phi[m]

    # Second hyperbola sum: only squares j=t^2 contribute.
    # We memoize D for repeated arguments (and seed D(k)=sum_tau).
    cache: dict[int, int] = {k: sum_tau}

    def D(x: int) -> int:
        v = cache.get(x)
        if v is not None:
            return v
        v = divisor_summatory(x)
        cache[x] = v
        return v

    sum2 = 0
    for t in range(1, tmax + 1):
        sum2 += phi_small[t] * D(N // (t * t))

    # Overlap subtraction term
    result = sum1 + sum2 - sum_tau * Phi[tmax]
    return result


def main() -> None:
    # Problem statement test values
    assert f_single(12) == 8
    assert compute_F(10) == 32
    assert compute_F(1000) == 12776

    N = 10**15
    if len(sys.argv) >= 2:
        N = int(sys.argv[1])

    print(compute_F(N))


if __name__ == "__main__":
    main()
