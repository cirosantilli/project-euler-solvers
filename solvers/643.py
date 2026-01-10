#!/usr/bin/env python3
"""
Project Euler 643: 2-Friendly

Two positive integers a and b are 2-friendly when gcd(a,b) is a power of 2
with exponent >= 1.

Let f(n) be the number of pairs (p,q) with 1 <= p < q <= n that are 2-friendly.
Compute f(10^11) modulo 1_000_000_007.

No external libraries are used.
"""

from array import array
import sys

MOD = 1_000_000_007
INV2 = (MOD + 1) // 2  # modular inverse of 2 mod MOD

# Precomputation limit.
# Tuned for n = 10^11: keeps runtime reasonable while using modest memory.
LIMIT = 10_000_000


def _tri_mod(n: int) -> int:
    """Return n*(n+1)//2 modulo MOD."""
    return (n % MOD) * ((n + 1) % MOD) % MOD * INV2 % MOD


def _build_totient_prefix(limit: int) -> array:
    """
    Linear sieve to compute phi(1..limit), then turn it into a prefix sum array:
    pref[i] = sum_{k=1..i} phi(k) mod MOD.
    Returned as an array('I') (32-bit unsigned).
    """
    phi = array("I", [0]) * (limit + 1)
    if limit >= 1:
        phi[1] = 1

    is_comp = bytearray(limit + 1)
    primes = array("I")
    primes_append = primes.append
    phi_local = phi
    is_comp_local = is_comp

    for i in range(2, limit + 1):
        if not is_comp_local[i]:
            primes_append(i)
            phi_local[i] = i - 1
        for p in primes:
            ip = i * p
            if ip > limit:
                break
            is_comp_local[ip] = 1
            if i % p == 0:
                phi_local[ip] = phi_local[i] * p
                break
            else:
                phi_local[ip] = phi_local[i] * (p - 1)

    # In-place prefix sum modulo MOD (reuse phi array as pref array).
    s = 0
    for i in range(1, limit + 1):
        s += phi_local[i]
        # Avoid big-int growth; reduce occasionally.
        if s >= (1 << 63):
            s %= MOD
        phi_local[i] = s % MOD

    return phi_local


class TotientSummatory:
    """
    Computes S(n) = sum_{k=1..n} phi(k) mod MOD using a Du Jiao sieve-style recursion:

        sum_{m=1..n} S(floor(n/m)) = n(n+1)/2

    Hence:
        S(n) = n(n+1)/2 - sum_{m=2..n} S(floor(n/m))

    Group m by equal floor(n/m) values to evaluate in O(sqrt(n)) time per distinct n,
    with memoization to avoid repetition.
    """

    __slots__ = ("limit", "pref", "memo")

    def __init__(self, limit: int):
        self.limit = limit
        self.pref = _build_totient_prefix(limit)
        self.memo = {}

    def S(self, n: int) -> int:
        if n <= self.limit:
            return self.pref[n]

        cached = self.memo.get(n)
        if cached is not None:
            return cached

        res = _tri_mod(n)

        l = 2
        # Avoid mod in the inner loop (it's safe to reduce only at the end).
        # Terms are at most ~O(n^2) but stay small enough for fast Python bigints.
        while l <= n:
            v = n // l
            r = n // v
            res -= (r - l + 1) * self.S(v)
            l = r + 1

        res %= MOD
        self.memo[n] = res
        return res


def friendly_pairs(n: int, ts: TotientSummatory) -> int:
    """
    Count pairs (p,q) with 1<=p<q<=n such that gcd(p,q) = 2^t for some t>=1.

    If gcd(p,q)=2^t, write p=2^t*a, q=2^t*b. Then gcd(a,b)=1 and 1<=a<b<=floor(n/2^t).
    For fixed t, the number of coprime pairs (a,b) with a<b<=m is:
        C(m) = sum_{k=2..m} phi(k) = S(m) - 1
    where S(m)=sum_{k=1..m} phi(k).
    Therefore:
        f(n) = sum_{t>=1} (S(floor(n/2^t)) - 1).
    """
    ans = 0
    t = 1
    while n >> t:
        m = n >> t
        ans += ts.S(m) - 1
        t += 1
    return ans % MOD


def main() -> None:
    sys.setrecursionlimit(1_000_000)

    ts = TotientSummatory(LIMIT)

    # Test values given in the problem statement:
    assert friendly_pairs(10**2, ts) == 1031
    assert friendly_pairs(10**6, ts) == 321418433

    print(friendly_pairs(10**11, ts))


if __name__ == "__main__":
    main()
