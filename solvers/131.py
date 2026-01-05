#!/usr/bin/env python
"""Adapted from: https://github.com/stbrumme/euler/blob/b426763514558c3b39f2ec507f271d322088d28a/euler-0131.cpp"""


def is_prime(x: int) -> bool:
    if x % 2 == 0 or x % 3 == 0 or x % 5 == 0:
        return x in (2, 3, 5)

    deltas = (6, 4, 2, 4, 2, 4, 6, 2)
    i = 7
    pos = 1
    while i * i <= x:
        if x % i == 0:
            return False
        i += deltas[pos]
        pos = (pos + 1) & 7
    return x > 1


def count_primes(limit: int) -> int:
    matches = []
    a = 1
    while True:
        p = 3 * a * a + 3 * a + 1
        if p >= limit:
            break
        if is_prime(p):
            matches.append(p)
        a += 1

    lo = 0
    hi = len(matches)
    while lo < hi:
        mid = (lo + hi) // 2
        if matches[mid] < limit:
            lo = mid + 1
        else:
            hi = mid
    return lo


def main() -> None:
    assert count_primes(100) == 4
    print(count_primes(1000000))


if __name__ == "__main__":
    main()
