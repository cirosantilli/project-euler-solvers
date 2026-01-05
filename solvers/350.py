#!/usr/bin/env python3
"""
Project Euler 350
Constraining the Least Greatest and the Greatest Least

Compute:
    f(10^6, 10^12, 10^18) mod 101^4

Where f(G, L, N) is the number of lists (a1..aN) of natural numbers with:
    gcd(a1..aN) >= G
    lcm(a1..aN) <= L

No external libraries are used (only Python standard library).
"""

from array import array

MOD = 101**4  # 104060401


def _linear_sieve_spf(n: int) -> array:
    """Smallest prime factor for each 0..n using a linear sieve."""
    spf = array("I", [0]) * (n + 1)
    if n >= 1:
        spf[1] = 1
    primes = []  # Python ints are fine here; ~78k primes up to 1e6.

    for i in range(2, n + 1):
        if spf[i] == 0:
            spf[i] = i
            primes.append(i)
        si = spf[i]
        for p in primes:
            ip = i * p
            if ip > n or p > si:
                break
            spf[ip] = p
    return spf


def _prefix_g_coprime_lcm(n: int, N: int, mod: int) -> array:
    """
    Build prefix sums:
        pref[m] = sum_{k<=m} c(k) (mod mod)
    where c(k) is the number of N-tuples with gcd=1 and lcm exactly k.
    """
    # Max exponent of any prime in [1..n] is achieved by 2^e <= n.
    max_e = 0
    t = n
    while t > 1:
        t //= 2
        max_e += 1

    # For each exponent e>=1, the per-prime contribution for gcd=1 and lcm=p^e is:
    # a_e = (e+1)^N - 2*e^N + (e-1)^N
    # because exponents are in [0..e], need min=0 and max=e.
    pow_cache = [pow(b, N, mod) for b in range(max_e + 2)]  # bases 0..max_e+1
    a = [0] * (max_e + 1)
    for e in range(1, max_e + 1):
        a[e] = (pow_cache[e + 1] - 2 * pow_cache[e] + pow_cache[e - 1]) % mod

    spf = _linear_sieve_spf(n)

    exp = bytearray(n + 1)  # exponent of spf[n] in n
    rest = array("I", [0]) * (n + 1)  # n with spf[n]^exp[n] removed
    c = array("I", [0]) * (n + 1)  # c[n] modulo mod

    rest[1] = 1
    c[1] = 1

    for i in range(2, n + 1):
        p = spf[i]
        m = i // p
        if spf[m] == p:
            exp[i] = exp[m] + 1
            rest[i] = rest[m]
        else:
            exp[i] = 1
            rest[i] = m
        c[i] = (c[rest[i]] * a[exp[i]]) % mod

    pref = array("I", [0]) * (n + 1)
    s = 0
    for i in range(1, n + 1):
        s += c[i]
        s %= mod
        pref[i] = s
    return pref


def f(G: int, L: int, N: int, mod: int = MOD) -> int:
    """
    Return f(G, L, N) modulo mod.

    Uses:
      - Decompose by exact gcd d:
            ai = d * bi, gcd(b)=1, lcm(b) <= floor(L/d)
        so:
            f(G,L,N) = sum_{d=G..L} g(floor(L/d), N)
        where g(M,N) counts N-tuples with gcd=1 and lcm<=M.

      - Compute g(M,N) for all M <= floor(L/G) via a multiplicative function and sieve.
      - Sum over d in O(sqrt(L)) groups using floor-division bucketing.
    """
    if G > L:
        return 0

    n = L // G  # maximum needed M in g(M,N)
    pref = _prefix_g_coprime_lcm(n, N, mod)

    ans = 0
    d = G
    while d <= L:
        q = L // d
        r = L // q
        cnt = r - d + 1
        ans = (ans + (cnt % mod) * pref[q]) % mod
        d = r + 1
    return ans


def main() -> None:
    # Tests from the problem statement
    assert f(10, 100, 1) == 91
    assert f(10, 100, 2) == 327
    assert f(10, 100, 3) == 1135
    assert f(10, 100, 1000) == 3286053

    # Required answer
    print(f(10**6, 10**12, 10**18))


if __name__ == "__main__":
    main()
