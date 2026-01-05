from __future__ import annotations

from typing import Dict, List


def sieve_primes(limit: int) -> List[int]:
    """Return list of all primes <= limit."""
    if limit < 2:
        return []
    is_prime = bytearray(b"\x01") * (limit + 1)
    is_prime[0:2] = b"\x00\x00"
    p = 2
    while p * p <= limit:
        if is_prime[p]:
            step = p
            start = p * p
            is_prime[start : limit + 1 : step] = b"\x00" * (
                ((limit - start) // step) + 1
            )
        p += 1
    return [i for i in range(2, limit + 1) if is_prime[i]]


def is_prime(n: int, trial_primes: List[int], cache: Dict[int, bool]) -> bool:
    if n in cache:
        return cache[n]
    if n < 2:
        cache[n] = False
        return False
    for p in trial_primes:
        if p * p > n:
            cache[n] = True
            return True
        if n % p == 0:
            cache[n] = n == p
            return cache[n]
    # Should not happen for this problem constraints (trial_primes are enough),
    # but keep a safe fallback.
    p = trial_primes[-1] + 2
    while p * p <= n:
        if n % p == 0:
            cache[n] = False
            return False
        p += 2
    cache[n] = True
    return True


def consecutive_prime_length(
    a: int, b: int, trial_primes: List[int], cache: Dict[int, bool]
) -> int:
    n = 0
    while True:
        val = n * n + a * n + b
        if not is_prime(val, trial_primes, cache):
            return n
        n += 1


def solve() -> int:
    # Enough for trial division up to sqrt(max quadratic value) in this search.
    trial_primes = sieve_primes(100_000)

    # For n = 0, expression equals b, so b must be prime (positive).
    b_candidates = [p for p in sieve_primes(1000) if p <= 1000]

    cache: Dict[int, bool] = {}

    best_len = -1
    best_a = 0
    best_b = 0

    for b in b_candidates:
        for a in range(-999, 1000):
            # Parity pruning:
            # For odd prime b (most cases), n=1 gives 1+a+b; since 1+b is even,
            # we need a odd to make the result odd (and thus possibly prime).
            if b != 2:
                if a % 2 == 0:
                    continue
            else:
                # If b=2, then 1+b=3 is odd; a must be even to keep odd.
                if a % 2 != 0:
                    continue

            # Quick check for n=1 to prune many pairs
            if not is_prime(1 + a + b, trial_primes, cache):
                continue

            length = consecutive_prime_length(a, b, trial_primes, cache)
            if length > best_len:
                best_len = length
                best_a = a
                best_b = b

    return best_a * best_b


if __name__ == "__main__":
    ans = solve()
    print(ans)
