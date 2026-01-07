#!/usr/bin/env python3
"""
Project Euler 554 - Centaurs on a Chess Board

We use the closed form:
    C(n) = 8 * binom(2n, n) - 3n^2 - 2n - 7

We need:
    sum_{i=2}^{90} C(F_i) mod 100000007
where F_i are Fibonacci numbers with F_1 = F_2 = 1.
"""

MOD = 100000007  # 10^8 + 7 (prime)


def fib_upto(n: int) -> list[int]:
    """Return Fibonacci numbers F_0..F_n with F_0=0, F_1=1."""
    f = [0, 1]
    for _ in range(2, n + 1):
        f.append(f[-1] + f[-2])
    return f


def gather_needed_factorials(ns: list[int]) -> list[int]:
    """
    Using Lucas theorem for binom(2n, n) mod MOD, we only need factorials for
    a small set of base-MOD digits. Gather all indices x where we need x!.
    """
    need = {0, 1}
    p = MOD

    for n in ns:
        N = 2 * n
        K = n
        while N or K:
            ni = N % p
            ki = K % p
            if ki <= ni:
                need.add(ni)
                need.add(ki)
                need.add(ni - ki)
            else:
                # Lucas product becomes 0; no factorials needed for this digit.
                pass
            N //= p
            K //= p

    return sorted(need)


def compute_sparse_factorials(targets: list[int]) -> dict[int, int]:
    """
    Compute factorials modulo MOD for the indices in `targets`,
    without storing the full table 0..MOD-1.

    This performs one linear sweep up to max(targets), recording only requested
    factorial values.
    """
    if not targets or targets[0] != 0:
        raise ValueError("targets must include 0")

    p = MOD
    max_idx = targets[-1]
    fact = {0: 1}

    # Pointer to next index we need.
    j = 1
    next_t = targets[j] if j < len(targets) else None

    f = 1
    for i in range(1, max_idx + 1):
        f = (f * i) % p
        if next_t is not None and i == next_t:
            fact[i] = f
            j += 1
            next_t = targets[j] if j < len(targets) else None

    return fact


def small_binom(n: int, k: int, fact: dict[int, int], invfact: dict[int, int]) -> int:
    """Compute C(n,k) mod MOD for 0<=n<MOD using precomputed sparse factorials."""
    if k < 0 or k > n:
        return 0
    return (fact[n] * invfact[k] % MOD) * invfact[n - k] % MOD


def lucas_binom(N: int, K: int, fact: dict[int, int], invfact: dict[int, int]) -> int:
    """Compute C(N,K) mod MOD using Lucas theorem (MOD is prime)."""
    p = MOD
    res = 1
    while N or K:
        ni = N % p
        ki = K % p
        if ki > ni:
            return 0
        res = (res * small_binom(ni, ki, fact, invfact)) % p
        N //= p
        K //= p
    return res


def C_mod(n: int, fact: dict[int, int], invfact: dict[int, int]) -> int:
    """Compute C(n) modulo MOD."""
    b = lucas_binom(2 * n, n, fact, invfact)
    nn = n % MOD
    poly = (3 * nn * nn + 2 * nn + 7) % MOD
    return (8 * b - poly) % MOD


def main() -> None:
    # Fibonacci numbers up to F_90 (F_1=F_2=1).
    F = fib_upto(90)

    # We'll need C(F_i) for i=2..90, plus test values from the statement.
    ns = [F[i] for i in range(2, 91)] + [1, 2, 10]

    targets = gather_needed_factorials(ns)
    fact = compute_sparse_factorials(targets)
    invfact = {x: pow(fact[x], MOD - 2, MOD) for x in fact}  # Fermat inverse

    # Test values given in the problem statement.
    assert C_mod(1, fact, invfact) == 4
    assert C_mod(2, fact, invfact) == 25
    assert C_mod(10, fact, invfact) == 1477721

    ans = 0
    for i in range(2, 91):
        ans = (ans + C_mod(F[i], fact, invfact)) % MOD

    print(ans)


if __name__ == "__main__":
    main()
