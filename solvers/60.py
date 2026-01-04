from __future__ import annotations

from typing import Dict, List, Tuple


def primes_up_to(limit: int) -> List[int]:
    if limit < 2:
        return []
    sieve = bytearray(b"\x01") * (limit + 1)
    sieve[0:2] = b"\x00\x00"
    r = int(limit**0.5)
    for i in range(2, r + 1):
        if sieve[i]:
            start = i * i
            step = i
            sieve[start : limit + 1 : step] = b"\x00" * (((limit - start) // step) + 1)
    return [i for i in range(2, limit + 1) if sieve[i]]


# Deterministic Miller-Rabin for 64-bit integers
_MR_BASES_64 = (2, 325, 9375, 28178, 450775, 9780504, 1795265022)
_SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    for p in _SMALL_PRIMES:
        if n % p == 0:
            return n == p

    # write n-1 = d * 2^s with d odd
    d = n - 1
    s = 0
    while (d & 1) == 0:
        s += 1
        d >>= 1

    for a in _MR_BASES_64:
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = (x * x) % n
            if x == n - 1:
                break
        else:
            return False
    return True


def pow10_for(n: int) -> int:
    p = 1
    while p <= n:
        p *= 10
    return p


def solve(limit: int = 10000) -> Tuple[int, List[int]]:
    primes = [p for p in primes_up_to(limit) if p not in (2, 5)]
    pow10_map: Dict[int, int] = {p: pow10_for(p) for p in primes}

    pair_cache: Dict[Tuple[int, int], bool] = {}

    is_prime_local = is_prime
    pow10_local = pow10_map
    cache_local = pair_cache

    def pair_ok(p: int, q: int) -> bool:
        if p > q:
            p, q = q, p
        key = (p, q)
        v = cache_local.get(key)
        if v is not None:
            return v

        # Since 10^k ≡ 1 (mod 3), concat(p,q) ≡ p+q (mod 3).
        # Any concatenation > 3 divisible by 3 is composite.
        if (p + q) % 3 == 0:
            cache_local[key] = False
            return False

        c1 = p * pow10_local[q] + q
        if not is_prime_local(c1):
            cache_local[key] = False
            return False
        c2 = q * pow10_local[p] + p
        ok = is_prime_local(c2)
        cache_local[key] = ok
        return ok

    best_sum = 10**30
    best_set: List[int] = []

    def dfs(clique: List[int], candidates: List[int], curr_sum: int) -> None:
        nonlocal best_sum, best_set

        k = len(clique)
        if k == 5:
            if curr_sum < best_sum:
                best_sum = curr_sum
                best_set = clique[:]
            return

        need = 5 - k
        if len(candidates) < need:
            return

        for idx in range(len(candidates)):
            q = candidates[idx]
            # Lower bound using q as smallest possible for all remaining picks
            if curr_sum + q * need >= best_sum:
                break

            new_candidates: List[int] = []
            for j in range(idx + 1, len(candidates)):
                r = candidates[j]
                # Lower bound after choosing q, with r the smallest possible next pick
                if curr_sum + q + r * (need - 1) >= best_sum:
                    break
                if pair_ok(q, r):
                    new_candidates.append(r)

            if len(new_candidates) >= (need - 1):
                dfs(clique + [q], new_candidates, curr_sum + q)

    n = len(primes)
    for i in range(n):
        p = primes[i]
        if p * 5 >= best_sum:
            break

        candidates: List[int] = []
        for j in range(i + 1, n):
            q = primes[j]
            if p + q * 4 >= best_sum:
                break
            if pair_ok(p, q):
                candidates.append(q)

        if len(candidates) >= 4:
            dfs([p], candidates, p)

    return best_sum, best_set


def _concat_pair_ok_brutal(p: int, q: int) -> bool:
    if (p + q) % 3 == 0:
        return False
    c1 = p * pow10_for(q) + q
    c2 = q * pow10_for(p) + p
    return is_prime(c1) and is_prime(c2)


def main() -> None:
    # Problem statement example checks (size 4 set)
    example = [3, 7, 109, 673]
    for i in range(len(example)):
        for j in range(i + 1, len(example)):
            assert _concat_pair_ok_brutal(example[i], example[j])

    ans, clique = solve(10000)

    assert set(clique) == {13, 5197, 5701, 6733, 8389}

    print(ans)


if __name__ == "__main__":
    main()
