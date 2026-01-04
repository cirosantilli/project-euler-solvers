from __future__ import annotations

from typing import Dict, List, Tuple


def sieve_primes_upto(n: int) -> List[bool]:
    """Return boolean array is_prime[0..n]."""
    is_prime = [True] * (n + 1)
    if n >= 0:
        is_prime[0] = False
    if n >= 1:
        is_prime[1] = False
    p = 2
    while p * p <= n:
        if is_prime[p]:
            step = p
            start = p * p
            for x in range(start, n + 1, step):
                is_prime[x] = False
        p += 1
    return is_prime


def find_prime_perm_arith_sequence() -> Tuple[int, int, int]:
    is_prime = sieve_primes_upto(9999)
    primes_4d = [p for p in range(1000, 10000) if is_prime[p]]

    # Group primes by digit-multiset signature
    groups: Dict[str, List[int]] = {}
    for p in primes_4d:
        key = "".join(sorted(str(p)))
        groups.setdefault(key, []).append(p)

    target_known = (1487, 4817, 8147)

    for key, arr in groups.items():
        if len(arr) < 3:
            continue
        arr.sort()
        s = set(arr)

        # Look for length-3 arithmetic sequences within this permutation group
        m = len(arr)
        for i in range(m):
            for j in range(i + 1, m):
                a, b = arr[i], arr[j]
                d = b - a
                c = b + d
                if c in s:
                    seq = (a, b, c)
                    if seq != target_known:
                        return seq

    raise RuntimeError("No valid sequence found.")


def main() -> None:
    a, b, c = find_prime_perm_arith_sequence()
    result = int(f"{a}{b}{c}")
    print(result)


if __name__ == "__main__":
    main()
